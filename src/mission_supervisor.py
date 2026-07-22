"""Hardware-independent mission supervisor for portfolio demonstration.

This module is a clean reconstruction. It is not the team's submitted ROS2 code.
"""

from dataclasses import dataclass
from enum import Enum, auto


class Mission(Enum):
    WAIT_GREEN = auto()
    CONE = auto()
    LANE = auto()
    FINISHED = auto()


@dataclass(frozen=True)
class Observation:
    green: bool = False
    cone_path_valid: bool = False
    lane_valid: bool = False
    lane_error: float = 0.0
    cone_section_clear: bool = False
    school_zone: bool = False
    obstacle_distance_m: float | None = None
    finish: bool = False


@dataclass(frozen=True)
class Command:
    speed: float
    steering: float
    state: Mission
    reason: str


class MissionSupervisor:
    """Select conservative motion commands from debounced mission observations."""

    def __init__(self, confirm_frames: int = 3, clear_frames: int = 3) -> None:
        if confirm_frames < 1 or clear_frames < 1:
            raise ValueError("frame thresholds must be positive")
        self.state = Mission.WAIT_GREEN
        self.confirm_frames = confirm_frames
        self.clear_frames = clear_frames
        self._green_count = 0
        self._cone_clear_count = 0
        self._obstacle_clear_count = 0
        self._emergency = False

    @staticmethod
    def _clamp(value: float, limit: float = 1.0) -> float:
        return max(-limit, min(limit, value))

    def update(self, obs: Observation) -> Command:
        self._update_emergency(obs)
        if self._emergency:
            return Command(0.0, 0.0, self.state, "emergency stop")

        if self.state is Mission.WAIT_GREEN:
            self._green_count = self._green_count + 1 if obs.green else 0
            if self._green_count >= self.confirm_frames:
                self.state = Mission.CONE
            return Command(0.0, 0.0, self.state, "waiting for confirmed green")

        if self.state is Mission.CONE:
            self._cone_clear_count = self._cone_clear_count + 1 if obs.cone_section_clear else 0
            if self._cone_clear_count >= self.confirm_frames:
                self.state = Mission.LANE
                return Command(0.15, 0.0, self.state, "cone section cleared")
            if not obs.cone_path_valid:
                return Command(0.10, 0.0, self.state, "cone path degraded")
            return Command(0.30, self._clamp(obs.lane_error), self.state, "cone path tracking")

        if self.state is Mission.LANE:
            if obs.finish:
                self.state = Mission.FINISHED
                return Command(0.0, 0.0, self.state, "finish confirmed")
            if not obs.lane_valid:
                return Command(0.10, 0.0, self.state, "lane lost: straight fallback")
            speed = 0.20 if obs.school_zone else 0.45
            return Command(speed, self._clamp(obs.lane_error), self.state, "lane tracking")

        return Command(0.0, 0.0, Mission.FINISHED, "run complete")

    def _update_emergency(self, obs: Observation) -> None:
        distance = obs.obstacle_distance_m
        if distance is not None and distance < 0.45:
            self._emergency = True
            self._obstacle_clear_count = 0
            return

        if not self._emergency:
            return

        if distance is None or distance > 0.80:
            self._obstacle_clear_count += 1
            if self._obstacle_clear_count >= self.clear_frames:
                self._emergency = False
                self._obstacle_clear_count = 0
        else:
            self._obstacle_clear_count = 0
