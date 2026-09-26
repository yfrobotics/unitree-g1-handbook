"""Validate one xr_teleoperate episode and export numeric data (never replay it)."""
import argparse
import csv
import json
import math
from pathlib import Path


def inspect(path, parts):
    episode = json.loads(path.read_text(encoding="utf-8"))
    frames = episode["data"]
    if not frames:
        raise ValueError("empty episode")
    widths, rows, camera_keys = {}, [], None
    previous_idx = -1
    for frame in frames:
        idx = frame["idx"]
        if not isinstance(idx, int) or idx != previous_idx + 1:
            raise ValueError("idx must start at zero and be contiguous")
        previous_idx = idx
        row = [idx]
        for group in ("states", "actions"):
            for part in parts:
                values = frame[group][part]["qpos"]
                if not isinstance(values, list) or not values or not all(
                    type(v) in (int, float) and math.isfinite(v) for v in values
                ):
                    raise ValueError(f"invalid {group}.{part}.qpos at frame {idx}")
                key = f"{group}.{part}"
                if key in widths and widths[key] != len(values):
                    raise ValueError(f"changing dimension: {key}")
                widths[key] = len(values)
                row.extend(values)
        colors = frame["colors"]
        if not colors or (camera_keys is not None and set(colors) != camera_keys):
            raise ValueError("missing or changing camera keys")
        camera_keys = set(colors)
        for relative in colors.values():
            image = (path.parent / relative).resolve()
            if not image.is_relative_to(path.parent.resolve()) or not image.is_file():
                raise ValueError(f"missing image or path outside episode: {relative}")
        rows.append(row)
    for part in parts:
        if widths[f"states.{part}"] != widths[f"actions.{part}"]:
            raise ValueError(f"state/action dimensions disagree: {part}")
    headers = ["idx"] + [f"{key}.{i}" for key, n in widths.items() for i in range(n)]
    return {
        "frames": len(rows), "dimensions": widths, "cameras": sorted(camera_keys),
        "nominal_fps": episode.get("info", {}).get("image", {}).get("fps"),
        "task": episode.get("text", {}).get("goal"),
        "timing": "NOT_VERIFIED: frame indices and nominal fps do not prove synchronization",
        "images": "EXISTENCE_ONLY: use the matching viewer to check decoding and alignment",
    }, headers, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", type=Path, help="Path to data.json")
    parser.add_argument("--parts", nargs="+", default=["left_arm", "right_arm", "left_ee", "right_ee"])
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    report, headers, rows = inspect(args.episode, args.parts)
    if args.csv:
        with args.csv.open("x", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
