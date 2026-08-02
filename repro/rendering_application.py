from __future__ import annotations

import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import PurePosixPath

import torch

from .resources import cpu_allocation


SOURCE_COMMIT = "c89269cb38eef7a95be703154f676a56d791958f"
ARCHIVE_URL = f"https://github.com/Felix-Petersen/gendr/archive/{SOURCE_COMMIT}.zip"
RAW_ROOT = f"https://raw.githubusercontent.com/Felix-Petersen/gendr/{SOURCE_COMMIT}"
EXPECTED_HASHES = {
    "experiments/opt_camera.py": "926ad20864e018fb9b945ac374f57b146d676f8bb15f78b1364bbbe05b0359f1",
    "experiments/data/teapot.obj": "2f833c87e691d949dfa1325df94efe3c25e95b948c7f147e2d08e3ffb719fcda",
    "setup.py": "fe2452a26d699ca09269054086444370f3c5f3e1bed1db2366c0a4ca8fd588a6",
    "README.md": "b1bf5f6c79136ae674798f7e439de58ce1b4188faae37d509d1452797f184a03",
}


def _download(url):
    request = urllib.request.Request(url, headers={"User-Agent": "OpenResearch-Reproduction/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def _safe_extract(bundle, destination):
    for name in bundle.namelist():
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"unsafe archive member: {name}")
    bundle.extractall(destination)


def _source_files(bundle):
    source_root = bundle.namelist()[0].split("/", 1)[0]
    result = {}
    for relative_path in EXPECTED_HASHES:
        archive_path = f"{source_root}/{relative_path}"
        if archive_path not in bundle.namelist():
            raise RuntimeError(f"missing {archive_path}")
        result[relative_path] = bundle.read(archive_path)
    return result


def _mesh_counts(mesh):
    lines = mesh.decode("utf-8").splitlines()
    return {
        "vertices": sum(line.startswith("v ") for line in lines),
        "faces": sum(line.startswith("f ") for line in lines),
    }


def run_rendering_capability_audit():
    started = time.perf_counter()
    resources = cpu_allocation(required_cores=1)
    archive = _download(ARCHIVE_URL)
    archive_sha256 = hashlib.sha256(archive).hexdigest()
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        files = _source_files(bundle)
        source_root_name = bundle.namelist()[0].split("/", 1)[0]
        with tempfile.TemporaryDirectory() as temporary_directory:
            _safe_extract(bundle, temporary_directory)
            source_root = os.path.join(temporary_directory, source_root_name)
            build = subprocess.run(
                [sys.executable, "setup.py", "build_ext"],
                cwd=source_root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            build_tail = (build.stdout + "\n" + build.stderr)[-4000:].replace(
                temporary_directory, "<temporary-source>"
            )

    hashes = {name: hashlib.sha256(payload).hexdigest() for name, payload in files.items()}
    camera = files["experiments/opt_camera.py"].decode("utf-8")
    setup = files["setup.py"].decode("utf-8")
    readme = files["README.md"].decode("utf-8")
    device_token = "device = 'cuda'"
    shallow_cpu_patch = camera.replace(device_token, "device = 'cpu'")
    shallow_patch_still_cuda_dependent = (
        device_token not in shallow_cpu_patch
        and setup.count("CUDAExtension(") == 4
        and "requires CUDA" in readme
    )
    elapsed = time.perf_counter() - started
    return {
        "route": "pinned cited-source CPU capability and protocol audit; no substitute renderer",
        "paper_protocol": {
            "asset": "Utah teapot",
            "camera_degrees_of_freedom": 4,
            "initial_orientation_error_degrees": [15, 75],
            "ground_truth_camera_angle_degrees": 20,
            "ground_truth_camera_distance": [2.5, 4.0],
            "initial_camera_distance": [2.0, 10.0],
            "initial_camera_angle_degrees": [10, 30],
            "optimizer": "Adam",
            "adam_betas": [0.5, 0.99],
            "initial_learning_rate": 0.3,
            "scheduler": "CosineAnnealingLR",
            "steps": 1000,
            "seeds": 768,
            "success_orientation_error_below_degrees": 5,
            "smoothing": "black-box hard rendering algorithm in four-dimensional camera coordinates",
        },
        "source_audit": {
            "repository": "Felix-Petersen/gendr",
            "commit": SOURCE_COMMIT,
            "archive_url": ARCHIVE_URL,
            "archive_bytes": len(archive),
            "archive_sha256": archive_sha256,
            "retrieved": "2026-08-02",
            "files": {
                name: {
                    "url": f"{RAW_ROOT}/{name}",
                    "bytes": len(files[name]),
                    "sha256": hashes[name],
                    "expected_sha256": EXPECTED_HASHES[name],
                }
                for name in EXPECTED_HASHES
            },
            "mesh": _mesh_counts(files["experiments/data/teapot.obj"]),
            "camera_script_hardcodes_cuda": device_token in camera,
            "setup_cuda_extension_count": setup.count("CUDAExtension("),
            "setup_cuda_kernel_count": setup.count(".cu'"),
            "readme_explicitly_requires_cuda": "requires CUDA" in readme,
            "cited_script_uses_normal_angles_not_uniform_sphere": (
                "torch.randn(batch_size) * 60" in camera
            ),
            "cited_script_uses_internal_differentiable_renderer_not_black_box_sampling": (
                "diff_renderer.dist_scale = sigma" in camera
            ),
        },
        "capability_test": {
            "command": f"{sys.executable} setup.py build_ext",
            "returncode": build.returncode,
            "failed": build.returncode != 0,
            "output_tail": build_tail,
            "torch_cuda_available": bool(torch.cuda.is_available()),
            "torch_cuda_build": torch.version.cuda,
            "nvcc_path": shutil.which("nvcc"),
        },
        "negative_control": {
            "name": "replace only the camera script device token with cpu",
            "shallow_patch_still_requires_four_cuda_extensions": shallow_patch_still_cuda_dependent,
            "failed_as_intended": shallow_patch_still_cuda_dependent,
        },
        "environment": resources,
        "runtime_seconds": elapsed,
        "verdict": "BLOCKED",
        "reason": "The cited renderer requires CUDA and its camera script is not the paper's black-box stochastic-smoothing implementation. GPU use is prohibited, and substituting a CPU renderer would not test the exact claim.",
    }
