"""GT-independent dominant-component selection followed by a fractional IoU gate."""
import numpy as np


def dominant_mass_component(attention, occupancy, retained_mass=0.5):
    values = np.asarray(attention, dtype=np.float64)
    target = np.asarray(occupancy, dtype=np.float64)
    if values.ndim != 2 or target.shape != values.shape or not 0 < retained_mass <= 1:
        raise ValueError("invalid attention/occupancy shape or retained mass")
    if not np.isfinite(values).all() or (values < 0).any() or values.sum() <= 0:
        raise ValueError("attention must have finite, nonnegative, positive total mass")
    if not np.isfinite(target).all() or (target < 0).any() or (target > 1).any():
        raise ValueError("GT occupancy must lie in [0, 1]")
    weights = values / values.sum()
    order = np.argsort(-weights.ravel(), kind="stable")
    # Rounding at retained_mass=1 must not pull zero-weight bridge cells into a component.
    count = min(int(np.count_nonzero(values)), int(np.searchsorted(np.cumsum(weights.ravel()[order]), retained_mass)) + 1)
    support = np.zeros(values.size, dtype=bool)
    support[order[:count]] = True
    support = support.reshape(values.shape)
    visited = np.zeros_like(support)
    components = []
    height, width = values.shape
    for yy, xx in zip(*np.nonzero(support)):
        if visited[yy, xx]:
            continue
        stack, cells = [(int(yy), int(xx))], []
        visited[yy, xx] = True
        while stack:
            y, x = stack.pop()
            cells.append((y, x))
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < height and 0 <= nx < width and support[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((ny, nx))
        mass = float(sum(weights[y, x] for y, x in cells))
        # Deterministic ties use the first spatial index, never GT overlap.
        components.append((mass, min(y * width + x for y, x in cells), cells))
    mass, _, cells = max(components, key=lambda item: (item[0], -item[1]))
    chosen = np.zeros_like(support)
    for y, x in cells:
        chosen[y, x] = True
    intersection = float(target[chosen].sum())
    union = float(chosen.sum() + target.sum() - intersection)
    return dict(dominant_component_fiou=intersection / union if union else 0.0,
                dominant_component_area=int(chosen.sum()), dominant_component_mass=mass,
                support50_area=int(support.sum()), support50_mass=float(weights[support].sum()),
                support50_components=len(components),
                gt_attention_mass=float((weights * target).sum()),
                peak_gt_occupancy=float(target.ravel()[int(values.argmax())]),
                top_left_attention_mass=float(weights[0, 0]))


def choose_iou_heads(items, role, mass_floor, max_heads, min_iou):
    if max_heads < 1 or not 0 < min_iou <= 1:
        raise ValueError("invalid maximum head count or IoU threshold")
    eligible = [item for item in items
                if item[f"{role}_visual_mass"] >= mass_floor
                and item["normalized_entropy"] is not None
                and item["dominant_component_fiou"] >= min_iou]
    eligible.sort(key=lambda item: (-item["dominant_component_fiou"], -item["gradient_absolute"],
                                    item["normalized_entropy"], item["layer"], item["query_head"]))
    return eligible[:max_heads]
