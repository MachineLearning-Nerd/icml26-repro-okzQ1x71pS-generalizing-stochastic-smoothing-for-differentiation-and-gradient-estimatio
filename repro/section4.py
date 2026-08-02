from __future__ import annotations

import heapq
import hashlib
import io
import itertools
import math
import os
import tarfile
import urllib.request
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import expit, ndtr, ndtri
from scipy.stats import qmc, t


DISTRIBUTIONS = ("Gaussian", "Logistic", "Gumbel", "Cauchy", "Laplace", "Triangular")
SYMMETRIC_DISTRIBUTIONS = {"Gaussian", "Logistic", "Cauchy", "Laplace", "Triangular"}
STRATEGIES = ("MC", "QMC-latin", "RQMC-latin", "RQMC-cartesian")
COVARIATES = ("none", "f(x)", "LOO")
SORTING_REPEATS = 64
PATH_REPEATS = 24
PATH_ORACLE_BLOCKS = {
    "default": 4,
    "Triangular": 32,
}
PATH_ORACLE_SAMPLES_PER_BLOCK = 65536
NOISE_SCALE = 1.0
WARCRAFT_URL = "https://edmond.mpg.de/api/access/datafile/102059"
WARCRAFT_MD5 = "acea5ea60a47664ff189923a84814e96"
WARCRAFT_BYTES = 915169563
PATH_SCALE_CANDIDATES = (0.0025, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6)
PATH_CALIBRATION_SAMPLES = 256


def _md5(path):
    digest = hashlib.md5()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def inverse_cdf(name, uniforms):
    u = np.clip(uniforms, 1e-10, 1.0 - 1e-10)
    if name == "Gaussian":
        return ndtri(u)
    if name == "Logistic":
        return np.log(u / (1.0 - u))
    if name == "Gumbel":
        return -np.log(-np.log(u))
    if name == "Cauchy":
        return np.tan(np.pi * (u - 0.5))
    if name == "Laplace":
        return np.where(u < 0.5, np.log(2.0 * u), -np.log(2.0 * (1.0 - u)))
    if name == "Triangular":
        return np.where(u < 0.5, np.sqrt(2.0 * u) - 1.0, 1.0 - np.sqrt(2.0 * (1.0 - u)))
    raise ValueError(name)


def score(name, noise):
    if name == "Gaussian":
        return noise
    if name == "Logistic":
        return np.tanh(noise / 2.0)
    if name == "Gumbel":
        return 1.0 - np.exp(-noise)
    if name == "Cauchy":
        return 2.0 * noise / (1.0 + noise * noise)
    if name == "Laplace":
        return np.sign(noise)
    if name == "Triangular":
        return np.sign(noise) / np.maximum(1.0 - np.abs(noise), 1e-10)
    raise ValueError(name)


def _cartesian_uniforms(dimension, samples, rng, antithetic):
    side = round(samples ** (1.0 / dimension))
    if side**dimension != samples:
        raise ValueError(f"{samples} is not a Cartesian power in dimension {dimension}")
    cells = np.asarray(list(itertools.product(range(side), repeat=dimension)), dtype=np.float64)
    if not antithetic:
        return (cells + rng.random(cells.shape)) / side

    mirrored = side - 1 - cells
    flat = np.ravel_multi_index(cells.astype(int).T, (side,) * dimension)
    mirrored_flat = np.ravel_multi_index(mirrored.astype(int).T, (side,) * dimension)
    first_cells = cells[flat < mirrored_flat]
    first = (first_cells + rng.random(first_cells.shape)) / side
    return np.concatenate([first, 1.0 - first], axis=0)


def draw_uniforms(strategy, dimension, samples, seed, antithetic=False):
    rng = np.random.default_rng(seed)
    if strategy == "RQMC-cartesian":
        return _cartesian_uniforms(dimension, samples, rng, antithetic)

    count = samples // 2 if antithetic else samples
    if antithetic and samples % 2:
        raise ValueError("antithetic sampling requires an even sample count")
    if strategy == "MC":
        uniforms = rng.random((count, dimension))
    elif strategy == "QMC-latin":
        uniforms = qmc.LatinHypercube(dimension, scramble=False, seed=seed).random(count)
    elif strategy == "RQMC-latin":
        uniforms = qmc.LatinHypercube(dimension, scramble=True, seed=seed).random(count)
    else:
        raise ValueError(strategy)
    if antithetic:
        uniforms = np.concatenate([uniforms, 1.0 - uniforms], axis=0)
    return uniforms


def hard_permutation(values):
    order = np.argsort(values, axis=1, kind="stable")
    ranks = np.empty_like(order)
    ranks[np.arange(len(values))[:, None], order] = np.arange(values.shape[1])
    return np.eye(values.shape[1], dtype=np.float64)[ranks].reshape(len(values), -1)


def estimate_gradient(function_values, scores, covariate, baseline):
    if covariate == "none":
        centered = function_values
    elif covariate == "f(x)":
        centered = function_values - baseline
    elif covariate == "LOO":
        leave_one_out = (function_values.sum(axis=0) - function_values) / (len(function_values) - 1)
        centered = function_values - leave_one_out
    else:
        raise ValueError(covariate)
    return centered.T @ scores / len(function_values)


def _cdf_pdf(name, value):
    if name == "Gaussian":
        return float(ndtr(value)), math.exp(-0.5 * value * value) / math.sqrt(2.0 * math.pi)
    if name == "Logistic":
        cdf = float(expit(value))
        return cdf, cdf * (1.0 - cdf)
    if name == "Gumbel":
        exp_term = math.inf if value < -700.0 else math.exp(-value)
        cdf = 0.0 if math.isinf(exp_term) else math.exp(-exp_term)
        return cdf, 0.0 if cdf == 0.0 else cdf * exp_term
    if name == "Cauchy":
        return 0.5 + math.atan(value) / math.pi, 1.0 / (math.pi * (1.0 + value * value))
    if name == "Laplace":
        if value < 0.0:
            return 0.5 * math.exp(value), 0.5 * math.exp(value)
        return 1.0 - 0.5 * math.exp(-value), 0.5 * math.exp(-value)
    if name == "Triangular":
        if value <= -1.0:
            return 0.0, 0.0
        if value < 0.0:
            return 0.5 * (value + 1.0) ** 2, value + 1.0
        if value < 1.0:
            return 1.0 - 0.5 * (1.0 - value) ** 2, 1.0 - value
        return 1.0, 0.0
    raise ValueError(name)


def _rank_probability_density(value, item, rank, inputs, distribution):
    _, density = _cdf_pdf(distribution, (value - inputs[item]) / NOISE_SCALE)
    density /= NOISE_SCALE
    coefficients = np.array([1.0])
    for other in range(len(inputs)):
        if other == item:
            continue
        cdf, _ = _cdf_pdf(distribution, (value - inputs[other]) / NOISE_SCALE)
        updated = np.zeros(len(coefficients) + 1)
        updated[:-1] += coefficients * (1.0 - cdf)
        updated[1:] += coefficients * cdf
        coefficients = updated
    return density * coefficients[rank]


def expected_permutation(inputs, distribution):
    size = len(inputs)
    expected = np.empty((size, size), dtype=np.float64)
    for item in range(size):
        if distribution == "Triangular":
            lower = inputs[item] - NOISE_SCALE
            upper = inputs[item] + NOISE_SCALE
            points = sorted(
                point
                for other in inputs
                for point in (other - NOISE_SCALE, other, other + NOISE_SCALE)
                if lower < point < upper
            )
            bounds = [lower, *points, upper]
        else:
            points = sorted(set(float(value) for value in inputs))
            bounds = [-np.inf, *points, np.inf]
        for rank in range(size):
            expected[item, rank] = sum(
                quad(
                    _rank_probability_density,
                    left,
                    right,
                    args=(item, rank, inputs, distribution),
                    epsabs=2e-9,
                    epsrel=2e-9,
                    limit=200,
                )[0]
                for left, right in zip(bounds, bounds[1:])
            )
    return expected


def sorting_oracle(inputs, distribution, step):
    output_size = len(inputs) ** 2
    gradient = np.empty((output_size, len(inputs)), dtype=np.float64)
    for coordinate in range(len(inputs)):
        delta = np.zeros_like(inputs)
        delta[coordinate] = step
        plus = expected_permutation(inputs + delta, distribution)
        minus = expected_permutation(inputs - delta, distribution)
        gradient[:, coordinate] = ((plus - minus) / (2.0 * step)).reshape(-1)
    return gradient


def _summary_row(domain, size, distribution, strategy, covariate, antithetic, samples, errors):
    values = np.asarray(errors, dtype=np.float64)
    mean = float(values.mean())
    std = float(values.std(ddof=1))
    half_width = float(t.ppf(0.975, len(values) - 1) * std / math.sqrt(len(values)))
    return {
        "domain": domain,
        "size": size,
        "distribution": distribution,
        "strategy": strategy,
        "covariate": covariate,
        "antithetic": bool(antithetic),
        "samples": int(samples),
        "repeats": int(len(values)),
        "mean_l2_error": mean,
        "std_l2_error": std,
        "ci95_low": max(0.0, mean - half_width),
        "ci95_high": mean + half_width,
    }


def _available_antithetic(distribution, strategy, dimension):
    if distribution not in SYMMETRIC_DISTRIBUTIONS:
        return False
    if strategy == "RQMC-cartesian" and dimension != 3:
        return False
    return True


def benchmark_sorting():
    rows = []
    oracle_audits = []
    negative_control = None
    inputs_by_size = {
        3: np.array([-0.41, 0.08, 0.57]),
        5: np.array([-0.71, -0.29, 0.04, 0.36, 0.82]),
    }
    for size, inputs in inputs_by_size.items():
        samples = 1000 if size == 3 else 1024
        baseline = hard_permutation(inputs[None, :])[0]
        for distribution_index, distribution in enumerate(DISTRIBUTIONS):
            oracle = sorting_oracle(inputs, distribution, step=2e-4)
            checker = sorting_oracle(inputs, distribution, step=1e-4)
            expected = expected_permutation(inputs, distribution)
            oracle_audits.append(
                {
                    "size": size,
                    "distribution": distribution,
                    "fd_step_disagreement": float(np.linalg.norm(oracle - checker)),
                    "row_sum_error": float(np.max(np.abs(expected.sum(axis=1) - 1.0))),
                    "column_sum_error": float(np.max(np.abs(expected.sum(axis=0) - 1.0))),
                }
            )
            for strategy_index, strategy in enumerate(STRATEGIES):
                antithetic_options = [False]
                if _available_antithetic(distribution, strategy, size):
                    antithetic_options.append(True)
                for antithetic in antithetic_options:
                    errors = {covariate: [] for covariate in COVARIATES}
                    for repeat in range(SORTING_REPEATS):
                        seed = 10_000 * size + 1_000 * distribution_index + 100 * strategy_index + repeat
                        uniforms = draw_uniforms(strategy, size, samples, seed, antithetic)
                        noise = inverse_cdf(distribution, uniforms)
                        values = hard_permutation(inputs + NOISE_SCALE * noise)
                        scores = score(distribution, noise) / NOISE_SCALE
                        for covariate in COVARIATES:
                            estimate = estimate_gradient(values, scores, covariate, baseline)
                            errors[covariate].append(float(np.linalg.norm(estimate - oracle)))
                        if (
                            negative_control is None
                            and size == 5
                            and distribution == "Laplace"
                            and strategy == "RQMC-cartesian"
                            and not antithetic
                            and repeat == 0
                        ):
                            correct = estimate_gradient(values, scores, "LOO", baseline)
                            wrong = estimate_gradient(values, noise, "LOO", baseline)
                            correct_error = float(np.linalg.norm(correct - oracle))
                            wrong_error = float(np.linalg.norm(wrong - oracle))
                            negative_control = {
                                "name": "Gaussian score substituted for the Laplace score",
                                "correct_error": correct_error,
                                "wrong_error": wrong_error,
                                "wrong_over_correct": wrong_error / correct_error,
                            }
                    for covariate in COVARIATES:
                        rows.append(
                            _summary_row(
                                "sorting",
                                f"n={size}",
                                distribution,
                                strategy,
                                covariate,
                                antithetic,
                                samples,
                                errors[covariate],
                            )
                        )
    return rows, oracle_audits, negative_control


def _neighbors(index, size):
    row, column = divmod(index, size)
    for row_delta in (-1, 0, 1):
        for column_delta in (-1, 0, 1):
            if row_delta == 0 and column_delta == 0:
                continue
            next_row = row + row_delta
            next_column = column + column_delta
            if 0 <= next_row < size and 0 <= next_column < size:
                yield next_row * size + next_column


def shortest_path_indicator(log_costs, size):
    costs = np.exp(np.clip(log_costs, -20.0, 20.0))
    count = size * size
    distances = np.full(count, np.inf)
    previous = np.full(count, -1, dtype=np.int32)
    distances[0] = costs[0]
    queue = [(float(costs[0]), 0)]
    while queue:
        distance, node = heapq.heappop(queue)
        if distance != distances[node]:
            continue
        if node == count - 1:
            break
        for neighbor in _neighbors(node, size):
            candidate = distance + costs[neighbor]
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (float(candidate), neighbor))
    output = np.zeros(count, dtype=np.float64)
    node = count - 1
    while node >= 0:
        output[node] = 1.0
        if node == 0:
            return output
        node = int(previous[node])
    raise RuntimeError("shortest-path reconstruction failed")


def shortest_path_batch(log_costs, size):
    return np.asarray([shortest_path_indicator(costs, size) for costs in log_costs])


def _download_warcraft_archive():
    cache = Path(".cache/openresearch")
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / "warcraft_maps.tar.gz"
    if archive.exists() and archive.stat().st_size == WARCRAFT_BYTES:
        digest = _md5(archive)
        if digest == WARCRAFT_MD5:
            return archive
    request = urllib.request.Request(WARCRAFT_URL, headers={"User-Agent": "OpenResearch-Reproduction/1.0"})
    digest = hashlib.md5()
    downloaded = 0
    temporary = archive.with_suffix(".partial")
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
        while chunk := response.read(8 * 1024 * 1024):
            output.write(chunk)
            digest.update(chunk)
            downloaded += len(chunk)
            if downloaded % (128 * 1024 * 1024) < len(chunk):
                print(f"Warcraft download: {downloaded}/{WARCRAFT_BYTES} bytes", flush=True)
    if downloaded != WARCRAFT_BYTES or digest.hexdigest() != WARCRAFT_MD5:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"Warcraft archive integrity failure: bytes={downloaded}, md5={digest.hexdigest()}"
        )
    temporary.replace(archive)
    return archive


def _official_warcraft_inputs():
    archive = _download_warcraft_archive()
    arrays = {}
    members_used = {}
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        suffix = "/12x12/train_vertex_weights.npy"
        matches = [
            member
            for member in members
            if member.name == suffix[1:] or member.name.endswith(suffix)
        ]
        if len(matches) != 1:
            raise RuntimeError(f"expected one archive member ending {suffix}, found {len(matches)}")
        handle = bundle.extractfile(matches[0])
        if handle is None:
            raise RuntimeError(f"could not read {matches[0].name}")
        official_weights = np.asarray(
            np.load(io.BytesIO(handle.read()), allow_pickle=False), dtype=np.float64
        )
        official_weights = official_weights.reshape(len(official_weights), 12, 12)
        for size in (8, 12):
            weights = official_weights[:, :size, :size].reshape(len(official_weights), -1)
            if weights.shape[1] != size * size or np.any(~np.isfinite(weights)):
                raise RuntimeError(f"invalid official Warcraft array shape {weights.shape}")
            sample = weights[: min(256, len(weights))]
            coefficients = sample.std(axis=1) / np.maximum(sample.mean(axis=1), 1e-12)
            median = float(np.median(coefficients))
            index = int(np.argmin(np.abs(coefficients - median)))
            positive = np.maximum(weights[index], 1e-8)
            arrays[size] = np.log(positive)
            members_used[size] = {
                "member": matches[0].name,
                "derivation": "native 12x12" if size == 12 else "top-left 8x8 crop of official 12x12 weights",
                "source_array_shape": list(official_weights.shape),
                "array_shape": list(weights.shape),
                "selected_index": index,
                "selection": "closest coefficient of variation to median among first 256 training maps",
                "selected_map_sha256": hashlib.sha256(weights[index].tobytes()).hexdigest(),
                "minimum_weight": float(weights[index].min()),
                "maximum_weight": float(weights[index].max()),
            }
    audit = {
        "source_url": WARCRAFT_URL,
        "dataset_doi": "10.17617/3.YJCQ5S",
        "published_filename": "warcraft_maps.tar.gz",
        "published_bytes": WARCRAFT_BYTES,
        "published_md5": WARCRAFT_MD5,
        "verified_md5": _md5(archive),
        "members_used": members_used,
    }
    return arrays, audit


def _path_change_rate(inputs, size, distribution, scale, seed, samples):
    baseline = shortest_path_indicator(inputs, size)
    sampler = qmc.Sobol(len(inputs), scramble=True, seed=seed)
    uniforms = sampler.random_base2(int(math.log2(samples)))
    noise = inverse_cdf(distribution, uniforms)
    paths = shortest_path_batch(inputs + scale * noise, size)
    return float(np.mean(np.any(paths != baseline, axis=1)))


def calibrate_path_scales(inputs_by_size):
    scales = {}
    audits = []
    for size, inputs in inputs_by_size.items():
        for distribution_index, distribution in enumerate(DISTRIBUTIONS):
            calibration_seed = 500_000 + 10_000 * size + 100 * distribution_index
            sweep = [
                {
                    "scale": scale,
                    "path_change_rate": _path_change_rate(
                        inputs, size, distribution, scale, calibration_seed, PATH_CALIBRATION_SAMPLES
                    ),
                }
                for scale in PATH_SCALE_CANDIDATES
            ]
            selected = min(sweep, key=lambda item: (abs(item["path_change_rate"] - 0.5), item["scale"]))
            validation_seed = calibration_seed + 1
            validation_rate = _path_change_rate(
                inputs,
                size,
                distribution,
                selected["scale"],
                validation_seed,
                PATH_CALIBRATION_SAMPLES,
            )
            scales[(size, distribution)] = selected["scale"]
            audits.append(
                {
                    "size": f"{size}x{size}",
                    "distribution": distribution,
                    "candidate_scales": list(PATH_SCALE_CANDIDATES),
                    "calibration_seed": calibration_seed,
                    "validation_seed": validation_seed,
                    "samples_per_rate": PATH_CALIBRATION_SAMPLES,
                    "selection_target": "path change rate closest to 0.5; smaller scale breaks ties",
                    "sweep": sweep,
                    "selected_scale": selected["scale"],
                    "calibration_path_change_rate": selected["path_change_rate"],
                    "held_out_path_change_rate": validation_rate,
                    "non_vacuous": bool(0.1 <= validation_rate <= 0.9),
                }
            )
    return scales, audits


def _path_oracle_half(specification):
    size, distribution, seed, inputs, scale = specification
    sampler = qmc.Sobol(len(inputs), scramble=True, seed=seed)
    uniforms = sampler.random_base2(int(math.log2(PATH_ORACLE_SAMPLES_PER_BLOCK)))
    noise = inverse_cdf(distribution, uniforms)
    values = shortest_path_batch(inputs + scale * noise, size)
    scores = score(distribution, noise) / scale
    return size, distribution, seed, values.T @ scores / len(values)


def _path_trial(specification):
    size, distribution, strategy, antithetic, repeat, oracle, inputs, scale = specification
    dimension = len(inputs)
    seed = 1_000_000 + 10_000 * size + 1_000 * DISTRIBUTIONS.index(distribution)
    seed += 100 * STRATEGIES.index(strategy) + 10 * int(antithetic) + repeat
    uniforms = draw_uniforms(strategy, dimension, 1024, seed, antithetic)
    noise = inverse_cdf(distribution, uniforms)
    values = shortest_path_batch(inputs + scale * noise, size)
    scores = score(distribution, noise) / scale
    baseline = shortest_path_indicator(inputs, size)
    errors = {}
    for covariate in COVARIATES:
        estimate = estimate_gradient(values, scores, covariate, baseline)
        errors[covariate] = float(np.linalg.norm(estimate - oracle))
    return size, distribution, strategy, antithetic, repeat, errors


def _valid_path(indicator, size):
    active = set(np.flatnonzero(indicator))
    if 0 not in active or size * size - 1 not in active:
        return False
    frontier = [0]
    reached = {0}
    while frontier:
        node = frontier.pop()
        for neighbor in _neighbors(node, size):
            if neighbor in active and neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)
    return reached == active


def benchmark_shortest_paths(workers):
    inputs_by_size, dataset_audit = _official_warcraft_inputs()
    scales, calibration_audits = calibrate_path_scales(inputs_by_size)
    oracle_specs = []
    for size in (8, 12):
        for distribution_index, distribution in enumerate(DISTRIBUTIONS):
            blocks = PATH_ORACLE_BLOCKS.get(distribution, PATH_ORACLE_BLOCKS["default"])
            for block in range(blocks):
                seed = 700_000 + 10_000 * size + 100 * distribution_index + block
                oracle_specs.append(
                    (size, distribution, seed, inputs_by_size[size], scales[(size, distribution)])
                )

    with ProcessPoolExecutor(max_workers=workers) as executor:
        oracle_halves = list(executor.map(_path_oracle_half, oracle_specs))

    grouped_oracles = {}
    oracle_audits = []
    for size in (8, 12):
        for distribution in DISTRIBUTIONS:
            blocks = [item[3] for item in oracle_halves if item[0] == size and item[1] == distribution]
            oracle = np.mean(blocks, axis=0)
            grouped_oracles[(size, distribution)] = oracle
            deviations = np.asarray([np.linalg.norm(block - oracle) for block in blocks])
            uncertainty = float(
                t.ppf(0.975, len(blocks) - 1)
                * math.sqrt(float(np.sum(deviations**2)) / (len(blocks) * (len(blocks) - 1)))
            )
            oracle_audits.append(
                {
                    "size": f"{size}x{size}",
                    "distribution": distribution,
                    "blocks": len(blocks),
                    "samples_per_block": PATH_ORACLE_SAMPLES_PER_BLOCK,
                    "samples": len(blocks) * PATH_ORACLE_SAMPLES_PER_BLOCK,
                    "selected_scale": scales[(size, distribution)],
                    "block_deviation_l2_mean": float(deviations.mean()),
                    "oracle_uncertainty_95": uncertainty,
                    "oracle_l2": float(np.linalg.norm(oracle)),
                }
            )

    trial_specs = []
    for size in (8, 12):
        for distribution in DISTRIBUTIONS:
            for strategy in STRATEGIES[:3]:
                antithetic_options = [False, True] if distribution in SYMMETRIC_DISTRIBUTIONS else [False]
                for antithetic in antithetic_options:
                    for repeat in range(PATH_REPEATS):
                        trial_specs.append(
                            (
                                size,
                                distribution,
                                strategy,
                                antithetic,
                                repeat,
                                grouped_oracles[(size, distribution)],
                                inputs_by_size[size],
                                scales[(size, distribution)],
                            )
                        )

    with ProcessPoolExecutor(max_workers=workers) as executor:
        trials = list(executor.map(_path_trial, trial_specs))

    errors = {}
    for size, distribution, strategy, antithetic, _, result in trials:
        for covariate, error in result.items():
            key = (size, distribution, strategy, covariate, antithetic)
            errors.setdefault(key, []).append(error)
    rows = [
        _summary_row(
            "shortest_path",
            f"{size}x{size}",
            distribution,
            strategy,
            covariate,
            antithetic,
            1024,
            values,
        )
        for (size, distribution, strategy, covariate, antithetic), values in errors.items()
    ]

    for audit in oracle_audits:
        case_errors = [
            row["mean_l2_error"]
            for row in rows
            if row["size"] == audit["size"] and row["distribution"] == audit["distribution"]
        ]
        minimum_error = min(case_errors)
        audit["minimum_estimator_error"] = minimum_error
        audit["uncertainty_over_minimum_error"] = audit["oracle_uncertainty_95"] / minimum_error

    path_checks = []
    for size in (8, 12):
        for distribution_index, distribution in enumerate(DISTRIBUTIONS):
            inputs = inputs_by_size[size]
            uniforms = draw_uniforms(
                "RQMC-latin", size * size, 16, 900_000 + 100 * size + distribution_index
            )
            noise = inverse_cdf(distribution, uniforms)
            paths = shortest_path_batch(inputs + scales[(size, distribution)] * noise, size)
            path_checks.append(
                {
                    "size": f"{size}x{size}",
                    "distribution": distribution,
                    "scale": scales[(size, distribution)],
                    "paths_checked": len(paths),
                    "all_binary": bool(np.all((paths == 0.0) | (paths == 1.0))),
                    "all_connected_8_neighborhood": bool(all(_valid_path(path, size) for path in paths)),
                }
            )
    return rows, oracle_audits, path_checks, dataset_audit, calibration_audits


def ranking_contract(rows):
    cases = []
    verified = True
    for size in ("n=3", "n=5"):
        for distribution in DISTRIBUTIONS:
            candidates = [
                row
                for row in rows
                if row["domain"] == "sorting"
                and row["size"] == size
                and row["distribution"] == distribution
                and not row["antithetic"]
            ]
            minimum = min(row["mean_l2_error"] for row in candidates)
            if distribution == "Triangular":
                target_strategy = "QMC-latin"
            else:
                target_strategy = "RQMC-cartesian"
            target = next(
                row
                for row in candidates
                if row["strategy"] == target_strategy and row["covariate"] == "LOO"
            )
            within_one_percent = target["mean_l2_error"] <= 1.01 * minimum
            verified = verified and within_one_percent
            cases.append(
                {
                    "size": size,
                    "distribution": distribution,
                    "paper_target": f"{target_strategy}/LOO/no-antithetic",
                    "target_mean_l2_error": target["mean_l2_error"],
                    "minimum_mean_l2_error": minimum,
                    "within_one_percent": bool(within_one_percent),
                }
            )
    return {"verified": bool(verified), "criterion": "paper target within 1% of cell minimum", "cases": cases}


def run_section4():
    workers = min(32, os.cpu_count() or 1)
    sorting_rows, sorting_oracles, negative_control = benchmark_sorting()
    path_rows, path_oracles, path_checks, dataset_audit, calibration_audits = benchmark_shortest_paths(
        workers
    )
    rows = sorting_rows + path_rows
    ranking = ranking_contract(rows)
    expected_cells = 447
    oracle_checks_pass = all(
        audit["fd_step_disagreement"] < 5e-4
        and audit["row_sum_error"] < 2e-7
        and audit["column_sum_error"] < 2e-7
        for audit in sorting_oracles
    )
    path_checks_pass = all(
        check["all_binary"] and check["all_connected_8_neighborhood"] for check in path_checks
    )
    path_oracle_checks_pass = all(
        audit["uncertainty_over_minimum_error"] < 0.2 for audit in path_oracles
    )
    non_vacuity_pass = all(audit["non_vacuous"] for audit in calibration_audits)
    dataset_pass = dataset_audit["verified_md5"] == WARCRAFT_MD5
    control_pass = negative_control["wrong_over_correct"] > 1.25
    coverage_pass = len(rows) == expected_cells and all(np.isfinite(row["mean_l2_error"]) for row in rows)
    claim4_verified = (
        coverage_pass
        and dataset_pass
        and oracle_checks_pass
        and path_oracle_checks_pass
        and non_vacuity_pass
        and path_checks_pass
        and control_pass
    )
    return {
        "rows": rows,
        "summary": {
            "estimated_useful_cores": 32,
            "workers": workers,
            "sorting_repeats": SORTING_REPEATS,
            "path_repeats": PATH_REPEATS,
            "path_oracle_blocks": PATH_ORACLE_BLOCKS,
            "path_oracle_samples_per_block": PATH_ORACLE_SAMPLES_PER_BLOCK,
            "path_oracle_samples_per_distribution_and_size": {
                name: PATH_ORACLE_BLOCKS.get(name, PATH_ORACLE_BLOCKS["default"])
                * PATH_ORACLE_SAMPLES_PER_BLOCK
                for name in DISTRIBUTIONS
            },
            "cell_count": len(rows),
            "expected_cell_count": expected_cells,
            "coverage_pass": bool(coverage_pass),
            "sorting_oracle_checks_pass": bool(oracle_checks_pass),
            "path_oracle_checks_pass": bool(path_oracle_checks_pass),
            "path_checks_pass": bool(path_checks_pass),
            "official_dataset_integrity_pass": bool(dataset_pass),
            "non_vacuity_pass": bool(non_vacuity_pass),
            "negative_control_pass": bool(control_pass),
            "claim4_verified": bool(claim4_verified),
            "claim5_verified": bool(ranking["verified"]),
        },
        "sorting_oracle_audit": sorting_oracles,
        "path_oracle_audit": path_oracles,
        "path_checks": path_checks,
        "warcraft_dataset_audit": dataset_audit,
        "path_scale_calibration": calibration_audits,
        "negative_control": negative_control,
        "ranking_contract": ranking,
    }
