"""Small runtime compatibility shims for the local training environment."""

import torch


_TORCHVISION_LIBRARY = None


def ensure_torchvision_nms_schema() -> None:
    """Declare the torchvision NMS schema when its binary extension is absent.

    Recent Transformers imports torchvision image transforms even for Qwen-VL.
    This environment's torchvision binary lacks the optional NMS operator, which
    causes that import to fail before any vision preprocessing occurs. Qwen-VL
    does not invoke NMS; this declares only the missing operator schema so
    torchvision's fake-registration import can complete.
    """
    global _TORCHVISION_LIBRARY
    try:
        torch._C._dispatch_has_kernel_for_dispatch_key("torchvision::nms", "Meta")
        return
    except RuntimeError as error:
        if "does not exist" not in str(error):
            raise
    _TORCHVISION_LIBRARY = torch.library.Library("torchvision", "FRAGMENT")
    _TORCHVISION_LIBRARY.define(
        "nms(Tensor boxes, Tensor scores, float iou_threshold) -> Tensor"
    )
