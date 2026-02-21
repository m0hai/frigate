"""Test birdseye functionality."""

import unittest
from unittest.mock import MagicMock

from frigate.config import BirdseyeModeEnum
from frigate.output.birdseye import BirdsEyeFrameManager, get_canvas_shape


class MockBirdseyeConfig:
    def __init__(self, mode, modes_by_label=None):
        self.mode = mode
        self.modes_by_label = modes_by_label or {}


class TestBirdseyeCameraActive(unittest.TestCase):
    """Test camera_active logic for per-object modes."""

    def _camera_active(self, config, objects, motion_count):
        return BirdsEyeFrameManager.camera_active(
            MagicMock(), config, objects, motion_count
        )

    def test_continuous_always_active(self):
        cfg = MockBirdseyeConfig(BirdseyeModeEnum.continuous)
        assert self._camera_active(cfg, [], 0) is True

    def test_motion_active_when_motion(self):
        cfg = MockBirdseyeConfig(BirdseyeModeEnum.motion)
        assert self._camera_active(cfg, [], 1) is True
        assert self._camera_active(cfg, [], 0) is False

    def test_objects_any_object_active(self):
        cfg = MockBirdseyeConfig(BirdseyeModeEnum.objects)
        assert self._camera_active(
            cfg, [{"label": "car", "stationary": True}], 0
        ) is True
        assert self._camera_active(cfg, [], 0) is False

    def test_active_objects_only_non_stationary(self):
        cfg = MockBirdseyeConfig(BirdseyeModeEnum.active_objects)
        assert self._camera_active(
            cfg, [{"label": "person", "stationary": False}], 0
        ) is True
        assert self._camera_active(
            cfg, [{"label": "car", "stationary": True}], 0
        ) is False

    def test_modes_by_label_per_class(self):
        cfg = MockBirdseyeConfig(
            BirdseyeModeEnum.objects,
            modes_by_label={
                "person": BirdseyeModeEnum.active_objects,
                "car": BirdseyeModeEnum.objects,
            },
        )
        # Stationary car triggers (car uses objects)
        assert self._camera_active(
            cfg, [{"label": "car", "stationary": True}], 0
        ) is True
        # Stationary person does NOT trigger (person uses active_objects)
        assert self._camera_active(
            cfg, [{"label": "person", "stationary": True}], 0
        ) is False
        # Active person triggers
        assert self._camera_active(
            cfg, [{"label": "person", "stationary": False}], 0
        ) is True


class TestBirdseye(unittest.TestCase):
    def test_16x9(self):
        """Test 16x9 aspect ratio works as expected for birdseye."""
        width = 1280
        height = 720
        canvas_width, canvas_height = get_canvas_shape(width, height)
        assert canvas_width == width
        assert canvas_height == height

    def test_4x3(self):
        """Test 4x3 aspect ratio works as expected for birdseye."""
        width = 1280
        height = 960
        canvas_width, canvas_height = get_canvas_shape(width, height)
        assert canvas_width == width
        assert canvas_height == height

    def test_32x9(self):
        """Test 32x9 aspect ratio works as expected for birdseye."""
        width = 2560
        height = 720
        canvas_width, canvas_height = get_canvas_shape(width, height)
        assert canvas_width == width
        assert canvas_height == height

    def test_9x16(self):
        """Test 9x16 aspect ratio works as expected for birdseye."""
        width = 720
        height = 1280
        canvas_width, canvas_height = get_canvas_shape(width, height)
        assert canvas_width == width
        assert canvas_height == height

    def test_non_16x9(self):
        """Test non 16x9 aspect ratio fails for birdseye."""
        width = 1280
        height = 840
        canvas_width, canvas_height = get_canvas_shape(width, height)
        assert canvas_width == width  # width will be the same
        assert canvas_height != height
