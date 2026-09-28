"""Localization evaluator registrations."""

from .bbox import LocalizationEvaluator, box_iou

__all__ = ["LocalizationEvaluator", "box_iou"]
