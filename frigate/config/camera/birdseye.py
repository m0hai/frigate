from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from ..base import FrigateBaseModel

__all__ = [
    "BirdseyeCameraConfig",
    "BirdseyeConfig",
    "BirdseyeLayoutConfig",
    "BirdseyeModeEnum",
]


class BirdseyeModeEnum(str, Enum):
    """Birdseye display modes.

    - objects: include camera when any tracked object is present (including stationary)
    - active_objects: include camera only when non-stationary/active objects are present
    - motion: include camera when motion is detected
    - continuous: always include camera
    """

    objects = "objects"
    active_objects = "active_objects"
    motion = "motion"
    continuous = "continuous"

    @classmethod
    def get_index(cls, type):
        return list(cls).index(type)

    @classmethod
    def get(cls, index):
        return list(cls)[index]


class BirdseyeLayoutConfig(FrigateBaseModel):
    scaling_factor: float = Field(
        default=2.0, title="Birdseye Scaling Factor", ge=1.0, le=5.0
    )
    max_cameras: Optional[int] = Field(default=None, title="Max cameras")


class BirdseyeConfig(FrigateBaseModel):
    enabled: bool = Field(default=True, title="Enable birdseye view.")
    mode: BirdseyeModeEnum = Field(
        default=BirdseyeModeEnum.objects, title="Default tracking mode."
    )
    modes_by_label: Optional[dict[str, BirdseyeModeEnum]] = Field(
        default=None,
        title="Override mode per object class. Only 'objects' and 'active_objects' apply per-label.",
    )

    @model_validator(mode="after")
    def validate_modes_by_label(self):
        if self.modes_by_label:
            for label, m in self.modes_by_label.items():
                if m not in (BirdseyeModeEnum.objects, BirdseyeModeEnum.active_objects):
                    raise ValueError(
                        f"modes_by_label for '{label}' must be 'objects' or 'active_objects', got '{m}'"
                    )
        return self

    restream: bool = Field(default=False, title="Restream birdseye via RTSP.")
    width: int = Field(default=1280, title="Birdseye width.")
    height: int = Field(default=720, title="Birdseye height.")
    quality: int = Field(
        default=8,
        title="Encoding quality.",
        ge=1,
        le=31,
    )
    inactivity_threshold: int = Field(
        default=30, title="Birdseye Inactivity Threshold", gt=0
    )
    layout: BirdseyeLayoutConfig = Field(
        default_factory=BirdseyeLayoutConfig, title="Birdseye Layout Config"
    )


# uses BaseModel because some global attributes are not available at the camera level
class BirdseyeCameraConfig(BaseModel):
    enabled: bool = Field(default=True, title="Enable birdseye view for camera.")
    mode: BirdseyeModeEnum = Field(
        default=BirdseyeModeEnum.objects, title="Default tracking mode for camera."
    )
    modes_by_label: Optional[dict[str, BirdseyeModeEnum]] = Field(
        default=None,
        title="Override mode per object class. Only 'objects' and 'active_objects' apply per-label.",
    )

    @model_validator(mode="after")
    def validate_modes_by_label(self):
        if self.modes_by_label:
            for label, m in self.modes_by_label.items():
                if m not in (BirdseyeModeEnum.objects, BirdseyeModeEnum.active_objects):
                    raise ValueError(
                        f"modes_by_label for '{label}' must be 'objects' or 'active_objects', got '{m}'"
                    )
        return self

    order: int = Field(default=0, title="Position of the camera in the birdseye view.")
