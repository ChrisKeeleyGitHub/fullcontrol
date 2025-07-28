import pytest
from lab.fullcontrol.geometry.fill import fill_base_simple, fill_base_full
from fullcontrol import Point


def test_fill_base_simple_requires_points():
    steps = [Point(x=0, y=0, z=0), "bad", Point(x=1, y=1, z=0)]
    with pytest.raises(TypeError):
        fill_base_simple(steps, segments_per_layer=1, solid_layers=1, extrusion_width=0.4)


def test_fill_base_full_requires_points():
    steps = [Point(x=0, y=0, z=0), "bad", Point(x=1, y=1, z=0)]
    with pytest.raises(TypeError):
        fill_base_full(steps, segments_per_layer=1, solid_layers=1, extrusion_width=0.4)


def test_fill_base_simple_all_points():
    steps = [Point(x=0, y=0, z=0), Point(x=1, y=0, z=0), Point(x=2, y=0, z=0)]
    result = fill_base_simple(steps, segments_per_layer=1, solid_layers=0, extrusion_width=0.4)
    assert len(result) == len(steps)

