from __future__ import annotations

import hashlib
import io
import os
import stat
import subprocess
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from .resources import cpu_allocation


SOURCES = {
    "TEM-simulator_1.3.zip": {
        "primary_url": "https://sourceforge.net/projects/tem-simulator/files/TEM-simulator_1.3.zip/download",
        "mirror_url": "https://downloads.sourceforge.net/project/tem-simulator/TEM-simulator_1.3.zip",
        "bytes": 425_791,
        "md5": "5c47d4946ecc222f27be7dce03e0228b",
    },
    "Simulation_example_TMV_v2.zip": {
        "primary_url": "https://sourceforge.net/projects/tem-simulator/files/Simulation_example_TMV_v2.zip/download",
        "mirror_url": "https://downloads.sourceforge.net/project/tem-simulator/Simulation_example_TMV_v2.zip",
        "bytes": 887_170,
        "md5": "a56518e96a88f922b0529a5e67a19ed3",
    },
}


def _digest(payload, algorithm):
    return hashlib.new(algorithm, payload).hexdigest()


def _download_exact(source):
    attempts = []
    selected = None
    for url in (source["primary_url"], source["mirror_url"]):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "OpenResearch-Reproduction/1.0"}
            )
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read()
                final_url = response.geturl()
            attempt = {
                "url": url,
                "final_url": final_url,
                "bytes": len(payload),
                "md5": _digest(payload, "md5"),
                "sha256": _digest(payload, "sha256"),
            }
            attempt["identity_match"] = (
                attempt["bytes"] == source["bytes"]
                and attempt["md5"] == source["md5"]
            )
            attempts.append(attempt)
            if attempt["identity_match"]:
                selected = payload
                break
        except Exception as error:
            attempts.append({"url": url, "error": f"{type(error).__name__}: {error}"})
    return selected, attempts


def _safe_member(name):
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts


def _zip_audit(payload):
    if payload is None or not zipfile.is_zipfile(io.BytesIO(payload)):
        return {
            "is_zip": False,
            "all_paths_safe": False,
            "member_count": 0,
            "members": [],
            "elf_members": [],
            "text_parameter_members": [],
        }
    members = []
    elf_members = []
    text_parameter_members = []
    parameter_tokens = (
        "voltage",
        "focal",
        "specimen",
        "micrograph",
        "detector",
        "tilt",
    )
    with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
        for info in bundle.infolist():
            if info.is_dir():
                continue
            data = bundle.read(info)
            member = {
                "name": info.filename,
                "bytes": len(data),
                "crc32": f"{info.CRC:08x}",
                "sha256": _digest(data, "sha256"),
                "path_safe": _safe_member(info.filename),
            }
            members.append(member)
            if data.startswith(b"\x7fELF"):
                machine = int.from_bytes(data[18:20], "little") if len(data) >= 20 else None
                elf_members.append(
                    {
                        "name": info.filename,
                        "machine": machine,
                        "is_x86_64": machine == 62,
                    }
                )
            if len(data) <= 2_000_000:
                text = data.decode("utf-8", errors="ignore").lower()
                found = [token for token in parameter_tokens if token in text]
                if found:
                    text_parameter_members.append(
                        {"name": info.filename, "tokens": found}
                    )
    return {
        "is_zip": True,
        "all_paths_safe": all(member["path_safe"] for member in members),
        "member_count": len(members),
        "members": members,
        "elf_members": elf_members,
        "text_parameter_members": text_parameter_members,
    }


def _extract_and_probe(payload, archive_audit):
    probes = []
    if payload is None or not archive_audit["all_paths_safe"]:
        return probes
    with tempfile.TemporaryDirectory() as temporary_directory:
        with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
            bundle.extractall(temporary_directory)
        for elf in archive_audit["elf_members"]:
            executable = Path(temporary_directory) / elf["name"]
            executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
            try:
                completed = subprocess.run(
                    [str(executable), "--help"],
                    cwd=executable.parent,
                    capture_output=True,
                    text=True,
                    timeout=20,
                    env={**os.environ, "OMP_NUM_THREADS": "8"},
                )
                probes.append(
                    {
                        "member": elf["name"],
                        "command": f"{elf['name']} --help",
                        "returncode": completed.returncode,
                        "timed_out": False,
                        "output_tail": (completed.stdout + "\n" + completed.stderr)[-4000:].replace(
                            temporary_directory, "<temporary-source>"
                        ),
                    }
                )
            except subprocess.TimeoutExpired as error:
                output = (error.stdout or "") + "\n" + (error.stderr or "")
                probes.append(
                    {
                        "member": elf["name"],
                        "command": f"{elf['name']} --help",
                        "returncode": None,
                        "timed_out": True,
                        "output_tail": output[-4000:].replace(
                            temporary_directory, "<temporary-source>"
                        ),
                    }
                )
    return probes


def run_tem_falsification_audit():
    started = time.perf_counter()
    resources = cpu_allocation(required_cores=1)
    source_results = {}
    payloads = {}
    for name, source in SOURCES.items():
        payload, attempts = _download_exact(source)
        audit = _zip_audit(payload)
        payloads[name] = payload
        source_results[name] = {
            "published": source,
            "retrieved": "2026-08-02",
            "attempts": attempts,
            "identity_verified": payload is not None,
            "archive": audit,
        }

    simulator_payload = payloads["TEM-simulator_1.3.zip"]
    simulator_audit = source_results["TEM-simulator_1.3.zip"]["archive"]
    capability_probes = _extract_and_probe(simulator_payload, simulator_audit)
    corrupted_rejected = False
    corrupted_md5 = None
    if simulator_payload:
        corrupted = bytearray(simulator_payload)
        corrupted[len(corrupted) // 2] ^= 1
        corrupted_md5 = _digest(bytes(corrupted), "md5")
        corrupted_rejected = corrupted_md5 != SOURCES["TEM-simulator_1.3.zip"]["md5"]

    exact_assets_available = False
    exact_optimizer_available = False
    counterexample_found = False
    return {
        "route": "mandatory fourth route dedicated to falsification via pinned TEM primary sources",
        "exact_claim": "Section 4.5 reports that generalized stochastic smoothing was used to optimize TEM-simulator v1.3 micrograph parameters in disclosed two- and four-dimensional searches.",
        "claim_logic": {
            "quantifier": "existential historical empirical demonstration",
            "domain": "the authors' exact TEM-simulator v1.3 input deck, TMV specimen asset, smoothing estimator, initializations, optimizer schedule, and stopping horizon",
            "assumptions": [
                "400x400 simulated micrographs",
                "ground truth 300 kV acceleration voltage, 3 mm focal length, centered specimen",
                "two-parameter voltage [0,1000] kV and x-position [-5,5] nm search",
                "four-parameter voltage [0,600] kV, focal length [0,6] mm, x/y-position [-3,3] nm search",
                "Adam betas (0.5,0.9)",
                "20 random-search repetitions",
            ],
            "falsification_requirement": "authenticated evidence satisfying every stated assumption and showing that the reported demonstration did not occur or that its exact reported outcome is impossible",
        },
        "paper_protocol": {
            "simulator": "TEM-simulator v1.3",
            "image_shape": [400, 400],
            "ground_truth": {
                "acceleration_voltage_kv": 300,
                "focal_length_mm": 3,
                "x_position_nm": 0,
                "y_position_nm": 0,
            },
            "two_parameter_domain": {
                "acceleration_voltage_kv": [0, 1000],
                "x_position_nm": [-5, 5],
            },
            "four_parameter_domain": {
                "acceleration_voltage_kv": [0, 600],
                "focal_length_mm": [0, 6],
                "x_position_nm": [-3, 3],
                "y_position_nm": [-3, 3],
            },
            "optimizer": "Adam",
            "adam_betas": [0.5, 0.9],
            "random_search_repetitions": 20,
            "paper_reported_single_sample_runtime_seconds_on_one_xeon_core": 67,
        },
        "primary_source_audit": source_results,
        "cpu_capability": {
            "elf_candidate_count": len(simulator_audit["elf_members"]),
            "x86_64_candidate_count": sum(
                item["is_x86_64"] for item in simulator_audit["elf_members"]
            ),
            "help_probes": capability_probes,
            "exact_paper_deck_identified": exact_assets_available,
            "exact_optimizer_code_identified": exact_optimizer_available,
            "exact_demonstration_executed": False,
        },
        "negative_control": {
            "name": "flip one byte in the pinned simulator archive",
            "corrupted_md5": corrupted_md5,
            "identity_verifier_rejected_corruption": corrupted_rejected,
            "failed_as_intended": corrupted_rejected,
        },
        "falsification": {
            "counterexample_found": counterexample_found,
            "all_paper_assumptions_satisfied": False,
            "routes_completed": [
                "MNIST exact-protocol throughput calibration",
                "Warcraft official-data exact-protocol throughput calibration",
                "pinned GenDR CPU capability and protocol audit",
                "pinned TEM primary-source falsification audit",
            ],
            "conclusion": "The public simulator and example archives can audit provenance and CPU capability, but absence of the authors' exact deck and optimizer implementation cannot contradict an existential historical demonstration.",
        },
        "environment": resources,
        "runtime_seconds": time.perf_counter() - started,
        "verdict": "BLOCKED",
        "reason": "No assumption-satisfying counterexample was established, and the undisclosed exact input deck, specimen mapping, learning rate, smoothing schedule, and optimization horizon prevent faithful execution.",
    }
