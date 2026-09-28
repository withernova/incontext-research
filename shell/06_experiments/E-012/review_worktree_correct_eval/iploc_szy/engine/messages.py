"""Structured, console-oriented messages emitted by the training framework."""

from dataclasses import dataclass
from typing import Mapping


def _duration(seconds: float) -> str:
    """Render a non-negative duration compactly for console progress."""
    seconds = max(0, int(round(seconds)))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}h{minutes:02d}m{seconds:02d}s"
    if minutes:
        return f"{minutes:d}m{seconds:02d}s"
    return f"{seconds:d}s"


@dataclass(frozen=True)
class TrainingProgressMessage:
    """One complete rank-zero progress update for an optimizer step."""

    step: int
    total_steps: int
    loss: float
    learning_rate: float
    step_seconds: float
    mean_step_seconds: float
    samples_seen: int
    examples_per_second: float
    peak_memory_gib: float
    localization_metrics: Mapping[str, float]

    def render(self) -> str:
        remaining = max(0, self.total_steps - self.step)
        eta_seconds = remaining * self.mean_step_seconds
        localization = self.localization_metrics
        localization_text = (
            f" tf_parse={localization.get('teacher_forced_bbox_parse_rate', 0.0):.1%}"
            f" tf_mIoU={localization.get('teacher_forced_mean_iou', 0.0):.3f}"
            f" tf_IoU@.25={localization.get('teacher_forced_iou_at_0.25', 0.0):.1%}"
            f" tf_IoU@.50={localization.get('teacher_forced_iou_at_0.5', 0.0):.1%}"
            f" tf_IoU@.75={localization.get('teacher_forced_iou_at_0.75', 0.0):.1%}"
        )
        return (
            f"[TRAIN] step={self.step}/{self.total_steps} "
            f"loss={self.loss:.6f} lr={self.learning_rate:.3e} "
            f"step_time={self.step_seconds:.2f}s "
            f"avg_step={self.mean_step_seconds:.2f}s eta={_duration(eta_seconds)} "
            f"samples={self.samples_seen} throughput={self.examples_per_second:.2f}/s "
            f"peak_mem={self.peak_memory_gib:.2f}GiB"
            f"{localization_text}"
        )


class ConsoleTrainingMessageBus:
    """Small message sink kept separate from hooks for future log backends."""

    def emit(self, message: TrainingProgressMessage) -> None:
        print(message.render(), flush=True)
