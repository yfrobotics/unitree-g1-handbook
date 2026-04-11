# MkDocs Wiki Setup - Design Spec

## Overview

Set up a MkDocs Material wiki for the Unitree G1 Handbook repo, deployed to GitHub Pages via GitHub Actions.

## Site Structure

```
docs/
├── index.md                    (Home - intro to the handbook)
├── getting-started/
│   ├── unboxing.md             (Unboxing & first boot)
│   ├── remote-control.md       (Remote controller usage) [placeholder]
│   └── safety.md               (Safety guidelines) [placeholder]
├── networking/
│   ├── connect-to-robot.md     (SSH, IP setup)
│   ├── connect-to-internet.md  (Internet access via router) [placeholder]
├── development/
│   ├── sdk-setup.md            (Download & compile SDK)
│   ├── hand-sdk.md             (Hand SDK & manipulation) [placeholder]
│   ├── ros2.md                 (ROS2 integration) [placeholder]
│   └── simulation.md           (Isaac Sim, Gazebo) [placeholder]
├── hardware/
│   ├── specs.md                (Hardware specs & components) [placeholder]
│   └── sensors.md              (Sensor data & perception) [placeholder]
└── troubleshooting.md          (FAQ & troubleshooting) [placeholder]
```

## Configuration

- **Theme:** Material for MkDocs with dark/light toggle and search
- **Navigation:** Explicitly defined in `mkdocs.yml`, follows learning path order
- **Deployment:** GitHub Actions workflow triggers on push to `main`, deploys to GitHub Pages

## Content Migration

- Existing README "Getting Started > Unboxing G1" section moves to `docs/getting-started/unboxing.md`
- Existing "Connect to the robot" section moves to `docs/networking/connect-to-robot.md`
- Existing "Download and compile the SDK" section moves to `docs/development/sdk-setup.md`
- README.md updated to point to the wiki site
- Placeholder pages include a brief topic description and "Work in progress" note

## Files to Create

- `mkdocs.yml` - MkDocs configuration
- `requirements.txt` - Python dependencies (mkdocs-material)
- `.github/workflows/deploy-wiki.yml` - GitHub Actions workflow
- All `docs/**/*.md` pages listed above
