"""Local-only conversion for G1_29 + Revo2 + one RGB camera, using Unitree LeRobot."""
import argparse
from dataclasses import replace
import json
from pathlib import Path

from inspect_episode import inspect


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw-dir", type=Path, required=True, help="Parent of task/episode_*/data.json")
    p.add_argument("--repo-id", required=True, help="Local dataset name, e.g. local/g1_brainco2_rgb_run01")
    p.add_argument("--check-only", action="store_true", help="Validate raw input without importing LeRobot or writing data")
    args = p.parse_args()
    if len(args.repo_id.split("/")) != 2 or any(
        not part or part in (".", "..") or "\\" in part for part in args.repo_id.split("/")
    ):
        p.error("repo-id must have two nonempty safe path components")
    parts = ["left_arm", "right_arm", "left_ee", "right_ee"]
    paths = sorted(args.raw_dir.glob("*/*/data.json"))
    if not paths:
        p.error("expected raw-dir/task/episode_*/data.json")
    upstream_entries = [entry for task in args.raw_dir.iterdir() if task.is_dir()
                        for entry in task.iterdir()]
    if set(upstream_entries) != {path.parent for path in paths}:
        p.error("raw-dir must contain only task directories with episode directories; move other files outside this tree")
    for path in paths:
        report, _, rows = inspect(path, parts)
        if report["cameras"] != ["color_0"] or report["nominal_fps"] != 30:
            p.error(f"{path}: this profile requires color_0 only and nominal 30 fps")
        if not report["task"]:
            p.error(f"{path}: missing task goal")
        for group in ("states", "actions"):
            for part, n in zip(parts, [7, 7, 6, 6]):
                if report["dimensions"][f"{group}.{part}"] != n:
                    p.error(f"{path}: wrong dimension for {group}.{part}")
        for row in rows:
            if not all(0 <= x <= 1 for x in row[15:27] + row[41:53]):
                p.error(f"{path}: Revo2 values must be normalized to [0,1]")
    if args.check_only:
        print(f"Validated {len(paths)} raw episode(s); timing and image decoding still require review.")
        return
    # These imports require the separate, pinned training environment.
    from lerobot.utils.constants import HF_LEROBOT_HOME
    from unitree_lerobot.utils.constants import ROBOT_CONFIGS
    from unitree_lerobot.utils.convert_unitree_json_to_lerobot import create_empty_dataset, populate_dataset
    import cv2
    target = HF_LEROBOT_HOME / args.repo_id
    if target.exists():
        p.error(f"refusing to replace an existing dataset: {target}")
    for path in paths:
        for frame in json.loads(path.read_text())["data"]:
            image = cv2.imread(str(path.parent / frame["colors"]["color_0"]))
            if image is None or image.shape != (480, 640, 3):
                p.error(f"{path}: converter requires decodable 640x480 RGB frames")
    name = "G1_29_BrainCo2_RGB"
    ROBOT_CONFIGS[name] = replace(
        ROBOT_CONFIGS["Unitree_G1_Brainco"], cameras=["cam_head"],
        camera_to_image_key={"color_0": "cam_head"})
    dataset = create_empty_dataset(args.repo_id, robot_type=name)
    populate_dataset(dataset, args.raw_dir, robot_type=name)
    dataset.finalize()  # Flush v3 writers before another process opens the dataset.
    (target / "handbook-profile.json").write_text(json.dumps({
        "profile": name, "state_action_order": parts, "dimensions": [7, 7, 6, 6],
        "units": ["rad", "rad", "normalized_0_1", "normalized_0_1"],
        "camera": {"color_0": "cam_head"}, "nominal_fps": 30,
        "timing_verified": False, "source_episodes": [str(path.resolve()) for path in paths],
    }, indent=2) + "\n")
    print(f"Local dataset: {target}")


if __name__ == "__main__":
    main()
