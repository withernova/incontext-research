"""Small torch.distributed helpers used by the optional DDP training path."""

import os
from dataclasses import dataclass
from typing import Any, Dict, List

import torch
import torch.distributed as dist


@dataclass(frozen=True)
class DistributedContext:
    """Describe the current torchrun process and its assigned CUDA device."""

    enabled: bool
    rank: int
    local_rank: int
    world_size: int
    device: torch.device

    @property
    def is_main_process(self) -> bool:
        """Return whether this process owns shared artifacts and console output."""
        return self.rank == 0


def initialize_distributed() -> DistributedContext:
    """Initialize NCCL when launched by torchrun, otherwise remain single-process."""
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    launched_by_torchrun = "LOCAL_RANK" in os.environ or "RANK" in os.environ
    if not launched_by_torchrun:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        return DistributedContext(False, 0, 0, 1, device)

    if not torch.cuda.is_available():
        raise RuntimeError("NCCL DDP requires CUDA")
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    torch.cuda.set_device(local_rank)
    if not dist.is_initialized():
        dist.init_process_group(backend="nccl", init_method="env://")
    return DistributedContext(
        enabled=True,
        rank=dist.get_rank(),
        local_rank=local_rank,
        world_size=dist.get_world_size(),
        device=torch.device("cuda", local_rank),
    )


def mean_scalar(value: float, context: DistributedContext) -> float:
    """Average one scalar over ranks and return the result on every rank."""
    if not context.enabled:
        return value
    tensor = torch.tensor(value, dtype=torch.float64, device=context.device)
    dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
    return float((tensor / context.world_size).item())


def gather_objects(value: Any, context: DistributedContext) -> List[Any]:
    """Gather small JSON-compatible metadata on every rank."""
    if not context.enabled:
        return [value]
    output: List[Any] = [None] * context.world_size
    dist.all_gather_object(output, value)
    return output


def barrier(context: DistributedContext) -> None:
    """Synchronize ranks when distributed execution is active."""
    if context.enabled:
        dist.barrier()


def shutdown_distributed(context: DistributedContext) -> None:
    """Close a process group created by :func:`initialize_distributed`."""
    if context.enabled and dist.is_initialized():
        dist.destroy_process_group()
