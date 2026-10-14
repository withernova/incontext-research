"""Scientific selection contracts: component identity, fractional GT, and no forced fill."""
import numpy as np
import pytest
from iploc_szy.head_screening.spatial_iou_gate import dominant_mass_component, choose_iou_heads


def test_dominant_uses_mass_not_peak_or_gt_overlap():
    # Single corner peak .26 loses to a connected .20+.19 component.
    a = np.array([[.26, 0, .20, .19], [.1, .1, 0, .15]])
    g = np.zeros_like(a)
    g[0, 0] = 1
    out = dominant_mass_component(a, g)
    assert out["dominant_component_area"] == 2
    assert out["dominant_component_mass"] == pytest.approx(.39)
    assert out["dominant_component_fiou"] == 0
    # Moving GT changes overlap, never the selected component.
    g[:] = 0
    g[0, 2:] = 1
    other = dominant_mass_component(a, g)
    assert other["dominant_component_mass"] == out["dominant_component_mass"]
    assert other["dominant_component_fiou"] == 1


def test_larger_area_cannot_hide_a_corner_carrying_more_mass():
    a = np.array([[.6, 0, .1, .1], [0, 0, .1, .1]])
    g = np.array([[0, 0, 1, 1], [0, 0, 1, 1]])
    out = dominant_mass_component(a, g, retained_mass=1)
    assert out["dominant_component_area"] == 1
    assert out["dominant_component_fiou"] == 0


def test_fractional_occupancy_and_threshold_mass():
    out = dominant_mass_component(np.array([[.6, .4]]), np.array([[.5, .25]]))
    assert out["dominant_component_fiou"] == pytest.approx(.5 / 1.25)
    assert out["support50_area"] == 1
    assert out["support50_mass"] == pytest.approx(.6)


def item(head, iou, entropy=0, gradient=1, mass=.8):
    return dict(head=str(head), layer=0, query_head=head, dominant_component_fiou=iou,
                normalized_entropy=entropy, gradient_absolute=gradient, reference_visual_mass=mass)


def test_hard_iou_cannot_be_compensated_by_low_entropy_or_gradient():
    rows = [item(0, .4999, gradient=999), item(1, .5, entropy=.9)]
    assert [x["head"] for x in choose_iou_heads(rows, "reference", .5, 10, .5)] == ["1"]
    assert choose_iou_heads(rows[:1], "reference", .5, 10, .5) == []


def test_iou_ranks_first_and_visual_mass_gate_remains():
    rows = [item(0, .5, gradient=999), item(1, .8, entropy=.9), item(2, 1, mass=.1)]
    assert [x["head"] for x in choose_iou_heads(rows, "reference", .5, 10, .5)] == ["1", "0"]


def test_diagonal_cells_are_disconnected_and_ties_are_spatial():
    a = np.array([[.5, 0], [0, .5]])
    g = np.array([[0, 0], [0, 1]])
    out = dominant_mass_component(a, g, retained_mass=1)
    assert out["support50_components"] == 2
    assert out["dominant_component_fiou"] == 0


@pytest.mark.parametrize("bad", [np.array([[0., 0.]]), np.array([[np.nan, 1.]]), np.array([[-1., 2.]])])
def test_invalid_attention_fails(bad):
    with pytest.raises(ValueError):
        dominant_mass_component(bad, np.ones_like(bad))
