from __future__ import annotations

import math
import os
from pathlib import Path


CPU_UPGRADE_VCPUS = 8
CPU_UPGRADE_USD_PER_HOUR = 0.03
HF_JOBS_HARDWARE_URL = "https://huggingface.co/docs/huggingface_hub/guides/jobs"


def _cgroup_quota_vcpus():
    cpu_max = Path("/sys/fs/cgroup/cpu.max")
    if not cpu_max.exists():
        return None
    quota, period = cpu_max.read_text().strip().split()
    if quota == "max":
        return None
    return float(quota) / float(period)


def cpu_allocation(required_cores=32):
    visible = os.cpu_count() or 1
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else visible
    quota = _cgroup_quota_vcpus()
    quota_limit = max(1, math.floor(quota)) if quota is not None else CPU_UPGRADE_VCPUS
    worker_limit = min(CPU_UPGRADE_VCPUS, affinity, quota_limit)
    return {
        "estimated_required_cores": required_cores,
        "selected_flavor": "hf/cpu-upgrade",
        "selected_flavor_declared_vcpus": CPU_UPGRADE_VCPUS,
        "visible_logical_cpus": visible,
        "affinity_logical_cpus": affinity,
        "cgroup_quota_vcpus": quota,
        "worker_limit": worker_limit,
        "declared_cost_usd_per_hour": CPU_UPGRADE_USD_PER_HOUR,
        "hardware_source_url": HF_JOBS_HARDWARE_URL,
        "hardware_source_retrieved": "2026-08-02",
        "gpu_requested": False,
    }
