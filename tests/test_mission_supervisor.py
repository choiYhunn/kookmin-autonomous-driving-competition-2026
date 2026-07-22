import unittest

from src.mission_supervisor import Mission, MissionSupervisor, Observation


class MissionSupervisorTest(unittest.TestCase):
    def test_green_requires_consecutive_frames(self):
        supervisor = MissionSupervisor(confirm_frames=2)
        supervisor.update(Observation(green=True))
        self.assertEqual(supervisor.state, Mission.WAIT_GREEN)
        supervisor.update(Observation(green=False))
        supervisor.update(Observation(green=True))
        command = supervisor.update(Observation(green=True))
        self.assertEqual(command.state, Mission.CONE)

    def test_lane_loss_uses_slow_straight_fallback(self):
        supervisor = MissionSupervisor(confirm_frames=1)
        supervisor.update(Observation(green=True))
        supervisor.update(Observation(cone_section_clear=True))
        command = supervisor.update(Observation(lane_valid=False))
        self.assertEqual(command.state, Mission.LANE)
        self.assertEqual(command.steering, 0.0)
        self.assertLessEqual(command.speed, 0.10)

    def test_emergency_release_is_debounced(self):
        supervisor = MissionSupervisor(confirm_frames=1, clear_frames=2)
        supervisor.update(Observation(green=True))
        stop = supervisor.update(Observation(obstacle_distance_m=0.30))
        self.assertEqual(stop.speed, 0.0)
        still_stopped = supervisor.update(Observation(obstacle_distance_m=1.0))
        self.assertEqual(still_stopped.speed, 0.0)
        released = supervisor.update(Observation(obstacle_distance_m=1.0, cone_path_valid=True))
        self.assertGreater(released.speed, 0.0)

    def test_school_zone_caps_lane_speed(self):
        supervisor = MissionSupervisor(confirm_frames=1)
        supervisor.update(Observation(green=True))
        supervisor.update(Observation(cone_section_clear=True))
        normal = supervisor.update(Observation(lane_valid=True))
        school = supervisor.update(Observation(lane_valid=True, school_zone=True))
        self.assertLess(school.speed, normal.speed)


if __name__ == "__main__":
    unittest.main()
