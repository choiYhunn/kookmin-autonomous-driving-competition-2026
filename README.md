# Kookmin Autonomous Driving Competition 2026

> Public-safe engineering reconstruction of the SKKU EMP team's preliminary autonomous-driving work. The competition is still in progress; this repository does **not** contain the submitted ROS2 source, organizer material, simulator assets, videos, or team calibration values.

## What we built

For the preliminary round of the 9th Kookmin University Autonomous Driving Competition, the SKKU EMP working group developed a ROS2/Unity driving pipeline for a three-lap mission course. The local implementation integrates camera, LiDAR, and IMU inputs with perception, mission planning, and Ackermann steering control.

The source artifacts inspected locally cover:

- traffic-light start and intersection decisions;
- cone-course center-path estimation;
- lane following and curve-speed reduction;
- pedestrian stop and obstacle-overtake decisions;
- school-zone speed limiting;
- mission transitions, debounce counters, and boundary recovery.

## My scope

The team planning document assigns the single Electronic and Electrical Engineering member to ROS2 setup, the `track_drive.py` framework, sensor-node integration, and final integration/debugging. Because the working folder has no Git history or per-file authorship metadata, this repository does not claim sole authorship of the team's implementation.

This public version is limited to a newly separated, hardware-independent mission supervisor that demonstrates the integration concepts without exposing the submitted source or team tuning data.

## System structure

```text
Camera / LiDAR / IMU
        |
        v
Perception snapshot  -->  Mission supervisor  -->  steering / speed command
                                |
                                +--> debounce, timeout, emergency stop
```

The original workspace separates `perception`, `planning`, `control`, configuration, and the ROS2 node. That tree remains private while the event is active.

## Public reconstruction

[`src/mission_supervisor.py`](src/mission_supervisor.py) is a standard-library-only state machine with:

- consecutive-frame confirmation before transitions;
- an emergency-stop override with explicit release confirmation;
- conservative degraded behavior when a lane is temporarily lost;
- bounded speed selection for cone, lane, school-zone, and finish states.

Run its tests with:

```bash
python -m unittest discover -s tests -v
```

## Status and evidence boundary

- Competition schedule in the organizer material: final event on **2026-08-25**.
- Preliminary submission deadline in the organizer schedule: **2026-06-26** after extension.
- Result or award: **not claimed**.
- Team size: local EMP briefing records six members; the official event rule allows 3–5 members, so the final registered roster requires confirmation.
- This repository is not a drop-in replacement for the submitted ROS2 package.

## Excluded from publication

- submitted/team-owned ROS2 source and exact tuning constants;
- organizer PDFs, simulator installer, server keys, and course assets;
- local IP addresses, absolute paths, logs, videos, and calibration captures;
- files without clear individual authorship.

See [`docs/provenance.md`](docs/provenance.md) for the verification notes.
