from __future__ import annotations

import itertools

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.integrate import quad


def _expect(piecewise_integrand, points):
    bounds = [-np.inf, *points, np.inf]
    return sum(
        quad(piecewise_integrand, left, right, epsabs=1e-11, epsrel=1e-11, limit=300)[0]
        for left, right in zip(bounds, bounds[1:])
    )


def lemma3_check():
    x = 0.37

    laplace_pdf = lambda e: 0.5 * np.exp(-abs(e))
    laplace_score = lambda e: np.sign(e)
    laplace_value = lambda z: abs(z)
    laplace_identity = _expect(
        lambda e: laplace_value(x + e) * laplace_score(e) * laplace_pdf(e),
        [-x, 0.0],
    )
    laplace_derivative = 1.0 - np.exp(-x)

    def triangular_pdf(e):
        return max(1.0 - abs(e), 0.0)

    def triangular_score(e):
        if abs(e) >= 1.0:
            return 0.0
        return np.sign(e) / (1.0 - abs(e)) if e else 0.0

    triangular_identity = quad(
        lambda e: abs(x + e) * triangular_score(e) * triangular_pdf(e),
        -1.0,
        1.0,
        points=[-x, 0.0],
        epsabs=1e-11,
        epsrel=1e-11,
    )[0]
    triangular_cdf = 0.5 + x - 0.5 * x * x
    triangular_derivative = 2.0 * triangular_cdf - 1.0

    wrong_gaussian_score = _expect(
        lambda e: laplace_value(x + e) * e * laplace_pdf(e),
        [-x, 0.0],
    )

    return {
        "laplace_error": abs(laplace_identity - laplace_derivative),
        "triangular_error": abs(triangular_identity - triangular_derivative),
        "wrong_score_error": abs(wrong_gaussian_score - laplace_derivative),
    }


def gaussian_grid(order=24, dimension=2):
    nodes, weights = hermgauss(order)
    points = []
    point_weights = []
    for index in itertools.product(range(order), repeat=dimension):
        points.append([np.sqrt(2.0) * nodes[i] for i in index])
        point_weights.append(np.prod([weights[i] for i in index]) / np.pi ** (dimension / 2))
    return np.asarray(points), np.asarray(point_weights)


def _f_scalar(y):
    return y[..., 0] ** 2 + y[..., 0] * y[..., 1] + 0.5 * y[..., 1] ** 2


def _f_vector(y):
    return np.stack(
        [y[..., 0] ** 2 + 0.3 * y[..., 1], np.sin(y[..., 1]) + 0.2 * y[..., 0]],
        axis=-1,
    )


def _mean_scalar(x, scale, points, weights):
    return np.sum(weights * _f_scalar(x + points @ scale.T))


def _mean_vector(x, scale, points, weights):
    return np.sum(weights[:, None] * _f_vector(x + points @ scale.T), axis=0)


def _covariance(x, scale, points, weights):
    values = _f_vector(x + points @ scale.T)
    mean = np.sum(weights[:, None] * values, axis=0)
    centered = values - mean
    return np.einsum("s,si,sj->ij", weights, centered, centered)


def theorem7_check():
    points, weights = gaussian_grid()
    x = np.array([0.31, -0.27])
    scale = np.diag([0.7, 1.1])
    values = _f_scalar(x + points @ scale.T)
    score = points
    inv_scale = np.linalg.inv(scale)

    grad_x_identity = np.einsum("s,si->i", weights * values, score @ inv_scale.T)
    grad_scale_identity = np.einsum(
        "s,s,sij->ij",
        weights,
        values,
        np.asarray([inv_scale.T @ (np.outer(e, e) - np.eye(2)) for e in points]),
    )

    h = 1e-5
    grad_x_fd = np.empty(2)
    for i in range(2):
        delta = np.zeros(2)
        delta[i] = h
        grad_x_fd[i] = (
            _mean_scalar(x + delta, scale, points, weights)
            - _mean_scalar(x - delta, scale, points, weights)
        ) / (2.0 * h)

    grad_scale_fd = np.empty((2, 2))
    for i in range(2):
        for j in range(2):
            delta = np.zeros((2, 2))
            delta[i, j] = h
            grad_scale_fd[i, j] = (
                _mean_scalar(x, scale + delta, points, weights)
                - _mean_scalar(x, scale - delta, points, weights)
            ) / (2.0 * h)

    return {
        "grad_x_error": float(np.max(np.abs(grad_x_identity - grad_x_fd))),
        "grad_scale_error": float(np.max(np.abs(grad_scale_identity - grad_scale_fd))),
    }


def theorem8_check():
    points, weights = gaussian_grid(order=30)
    x = np.array([0.21, -0.34])
    scale = np.diag([0.65, 0.9])
    shifted = x + points @ scale.T
    values = _f_vector(shifted)
    mean = np.einsum("s,si->i", weights, values)
    inv_scale = np.linalg.inv(scale)
    score_x = points @ inv_scale.T
    score_scale = np.asarray([inv_scale.T @ (np.outer(e, e) - np.eye(2)) for e in points])

    grad_mean_x = np.einsum("s,si,sj->ij", weights, values, score_x)
    grad_mean_scale = np.einsum("s,si,sjk->ijk", weights, values, score_scale)
    second_x = np.einsum("s,si,sj,sk->ijk", weights, values, values, score_x)
    second_scale = np.einsum("s,si,sj,skl->ijkl", weights, values, values, score_scale)
    grad_cov_x = second_x - np.einsum("i,jk->ijk", mean, grad_mean_x) - np.einsum(
        "j,ik->ijk", mean, grad_mean_x
    )
    grad_cov_scale = second_scale - np.einsum(
        "i,jkl->ijkl", mean, grad_mean_scale
    ) - np.einsum("j,ikl->ijkl", mean, grad_mean_scale)

    h = 1e-5
    grad_cov_x_fd = np.empty((2, 2, 2))
    for k in range(2):
        delta = np.zeros(2)
        delta[k] = h
        grad_cov_x_fd[..., k] = (
            _covariance(x + delta, scale, points, weights)
            - _covariance(x - delta, scale, points, weights)
        ) / (2.0 * h)

    grad_cov_scale_fd = np.empty((2, 2, 2, 2))
    for k in range(2):
        for ell in range(2):
            delta = np.zeros((2, 2))
            delta[k, ell] = h
            grad_cov_scale_fd[..., k, ell] = (
                _covariance(x, scale + delta, points, weights)
                - _covariance(x, scale - delta, points, weights)
            ) / (2.0 * h)

    return {
        "grad_cov_x_error": float(np.max(np.abs(grad_cov_x - grad_cov_x_fd))),
        "grad_cov_scale_error": float(np.max(np.abs(grad_cov_scale - grad_cov_scale_fd))),
    }


def baseline_variance_proxy(seed=2024, samples=64, repeats=150):
    rng = np.random.default_rng(seed)
    distributions = ["Gaussian", "Logistic", "Gumbel", "Cauchy", "Laplace", "Triangular"]
    samplers = ["MC", "MC-antithetic", "QMC-cart", "RQMC-cart", "QMC-latin", "RQMC-latin"]
    covariates = ["none", "f(x)", "LOO"]
    variances = {}

    def inverse_cdf(name, u):
        u = np.clip(u, 1e-9, 1.0 - 1e-9)
        if name == "Gaussian":
            from scipy.special import ndtri

            return ndtri(u)
        if name == "Logistic":
            return np.log(u / (1.0 - u))
        if name == "Gumbel":
            return -np.log(-np.log(u))
        if name == "Cauchy":
            return np.tan(np.pi * (u - 0.5))
        if name == "Laplace":
            return np.where(u < 0.5, np.log(2.0 * u), -np.log(2.0 * (1.0 - u)))
        return np.where(u < 0.5, np.sqrt(2.0 * u) - 1.0, 1.0 - np.sqrt(2.0 * (1.0 - u)))

    def score(name, e):
        if name == "Gaussian":
            return e
        if name == "Logistic":
            return np.tanh(e / 2.0)
        if name == "Gumbel":
            return 1.0 - np.exp(-e)
        if name == "Cauchy":
            return 2.0 * e / (1.0 + e * e)
        if name == "Laplace":
            return np.sign(e)
        return np.sign(e) / np.maximum(1.0 - np.abs(e), 1e-9)

    for distribution in distributions:
        for sampler in samplers:
            estimates = {covariate: [] for covariate in covariates}
            for repeat in range(repeats):
                if sampler == "MC":
                    u = rng.random(samples)
                elif sampler == "MC-antithetic":
                    half = rng.random(samples // 2)
                    u = np.concatenate([half, 1.0 - half])
                elif sampler.startswith("QMC-"):
                    u = (np.arange(samples) + 0.5) / samples
                else:
                    u = (np.arange(samples) + rng.random(samples)) / samples
                    rng.shuffle(u)
                epsilon = inverse_cdf(distribution, u)
                function_values = np.abs(0.37 + epsilon)
                scores = score(distribution, epsilon)
                estimates["none"].append(np.mean(function_values * scores))
                estimates["f(x)"].append(np.mean((function_values - abs(0.37)) * scores))
                loo = (np.sum(function_values) - function_values) / (samples - 1)
                estimates["LOO"].append(np.mean((function_values - loo) * scores))
            for covariate in covariates:
                variances[f"{distribution}/{sampler}/{covariate}"] = float(
                    np.var(estimates[covariate], ddof=1)
                )

    return {
        "seed": seed,
        "samples": samples,
        "repeats": repeats,
        "combination_count": len(variances),
        "all_finite": bool(all(np.isfinite(value) for value in variances.values())),
        "variances": variances,
    }
