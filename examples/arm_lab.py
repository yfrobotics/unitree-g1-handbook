"""Offline fixed-base G1 arm exercises. This module never imports a robot SDK."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import mujoco
import numpy as np

ARM = ["left_" + name + "_joint" for name in (
    "shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow",
    "wrist_roll", "wrist_pitch", "wrist_yaw")]


class ArmLab:
    def __init__(self, xml):
        root = ET.parse(xml).getroot()
        root.find("compiler").set("meshdir", str((xml.parent / "meshes").resolve()))
        for body in root.iter("body"):
            for joint in list(body.findall("joint")):
                if joint.get("type") == "free":
                    body.remove(joint)
        self.model = mujoco.MjModel.from_xml_string(ET.tostring(root, encoding="unicode"))
        self.model.opt.timestep = 0.002
        self.data = mujoco.MjData(self.model)
        ids = np.array([self.model.joint(name).id for name in ARM])
        self.qadr = self.model.jnt_qposadr[ids]
        self.vadr = self.model.jnt_dofadr[ids]
        self.limits = self.model.jnt_range[ids].copy()
        self.body = self.model.body("left_wrist_yaw_link").id
        self.act_joint = self.model.actuator_trnid[:, 0]
        self.act_q = self.model.jnt_qposadr[self.act_joint]
        self.act_v = self.model.jnt_dofadr[self.act_joint]
        self.home = self.model.qpos0.copy()
        for name, value in {"left_shoulder_roll_joint": 0.2,
                            "right_shoulder_roll_joint": -0.2,
                            "left_elbow_joint": 1.0, "right_elbow_joint": 1.0}.items():
            self.home[self.model.joint(name).qposadr[0]] = value
        self.reset()

    def reset(self):
        mujoco.mj_resetData(self.model, self.data)
        self.data.qpos[:] = self.home
        mujoco.mj_forward(self.model, self.data)
        return self.data.qpos[self.qadr].copy()

    def step(self, target):
        desired = self.home.copy()
        desired[self.qadr] = np.clip(target, self.limits[:, 0], self.limits[:, 1])
        # Educational fixed-base PD + model bias compensation, NOT real robot gains.
        for _ in range(10):
            tau = 80 * (desired[self.act_q] - self.data.qpos[self.act_q])
            tau -= 4 * self.data.qvel[self.act_v]
            tau += self.data.qfrc_bias[self.act_v]
            self.data.ctrl[:] = np.clip(tau, self.model.actuator_ctrlrange[:, 0],
                                       self.model.actuator_ctrlrange[:, 1])
            mujoco.mj_step(self.model, self.data)
        if not np.isfinite(self.data.qpos).all():
            raise ValueError("nonfinite simulation state")
        return self.data.qpos[self.qadr].copy()

    def ik(self):
        self.reset()
        # Generate a reachable target pose from a known nearby configuration.
        self.data.qpos[self.qadr] += np.array([-.08, .06, .04, .1, .02, .03, -.02])
        mujoco.mj_forward(self.model, self.data)
        target_pos = self.data.xpos[self.body].copy()
        target_quat = self.data.xquat[self.body].copy()
        self.reset()
        jp, jr = np.zeros((3, self.model.nv)), np.zeros((3, self.model.nv))
        rotation_error = np.zeros(3)
        for iteration in range(300):
            mujoco.mj_forward(self.model, self.data)
            ep = target_pos - self.data.xpos[self.body]
            # mju_subQuat gives local angular velocity; rotate it to the world frame.
            mujoco.mju_subQuat(rotation_error, target_quat, self.data.xquat[self.body])
            er = self.data.xmat[self.body].reshape(3, 3) @ rotation_error
            if np.linalg.norm(ep) < 1e-4 and np.linalg.norm(er) < 1e-3:
                break
            mujoco.mj_jacBody(self.model, self.data, jp, jr, self.body)
            jac = np.vstack([jp[:, self.vadr], jr[:, self.vadr]])
            error = np.concatenate([ep, er])
            dq = jac.T @ np.linalg.solve(jac @ jac.T + 1e-4 * np.eye(6), error)
            self.data.qpos[self.qadr] = np.clip(
                self.data.qpos[self.qadr] + np.clip(dq, -.05, .05),
                self.limits[:, 0], self.limits[:, 1])
        if np.linalg.norm(ep) >= 1e-4 or np.linalg.norm(er) >= 1e-3:
            raise ValueError("IK did not converge; refusing to track the last iterate")
        solution = self.data.qpos[self.qadr].copy()
        # Now track the IK solution through physics, rather than overwriting qpos.
        initial = self.reset()
        for n in range(200):
            u = min((n + 1) / 100, 1.0)
            self.step(initial + (3 * u**2 - 2 * u**3) * (solution - initial))
        return {"ik_iterations": iteration + 1, "ik_position_error_m": float(np.linalg.norm(ep)),
                "ik_rotation_error_rad": float(np.linalg.norm(er)),
                "tracking_joint_error_rad": float(np.max(np.abs(self.data.qpos[self.qadr] - solution))),
                "solution_rad": solution.tolist(), "target_position_m": target_pos.tolist(),
                "target_quaternion_wxyz": target_quat.tolist(),
                "scope": "fixed base, wrist-link origin, no BrainCo2 hand or grasp"}


def collect(lab, output, seed):
    rng = np.random.default_rng(seed)
    observations, actions, episodes, splits, goals = [], [], [], [], []
    for episode in range(30):
        q = lab.reset()
        goal = np.clip(q + rng.uniform(-.18, .18, 7), lab.limits[:, 0] + .02, lab.limits[:, 1] - .02)
        goals.append(goal)
        for _ in range(100):
            error = goal - q
            delta = np.clip(.2 * error, -.025, .025)
            observations.append(error)
            actions.append(delta)
            episodes.append(episode)
            splits.append(0 if episode < 20 else 1 if episode < 25 else 2)
            q = lab.step(q + delta)
    np.savez(output / "demonstrations.npz", observation=observations, action=actions,
             episode=episodes, split=splits, goals=goals)


def train(output):
    with np.load(output / "demonstrations.npz", allow_pickle=False) as ds:
        x, y, split = ds["observation"], ds["action"], ds["split"]
        if x.shape != y.shape or x.shape[1] != 7 or not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("invalid demonstration shape or values")
        for episode in np.unique(ds["episode"]):
            if len(np.unique(split[ds["episode"] == episode])) != 1:
                raise ValueError("episode crosses splits")
        mean, scale = x[split == 0].mean(0), x[split == 0].std(0).clip(1e-6)
        features = np.column_stack([(x - mean) / scale, np.ones(len(x))])
        a, b = features[split == 0], y[split == 0]
        weights = np.linalg.solve(a.T @ a + 1e-5 * np.eye(8), a.T @ b)
        np.savez(output / "policy.npz", weights=weights, mean=mean, scale=scale)
        valid = split == 1
        return float(np.mean((features[valid] @ weights - y[valid])**2))


def evaluate(lab, output):
    # Restore from disk so the example exercises the checkpoint path.
    with np.load(output / "policy.npz", allow_pickle=False) as ckpt:
        weights, mean, scale = ckpt["weights"], ckpt["mean"], ckpt["scale"]
        if weights.shape != (8, 7) or mean.shape != (7,) or scale.shape != (7,):
            raise ValueError("checkpoint dimensions do not match the arm")
        if not all(np.isfinite(a).all() for a in (weights, mean, scale)) or np.any(scale <= 0):
            raise ValueError("invalid checkpoint values")
    with np.load(output / "demonstrations.npz", allow_pickle=False) as ds:
        goals = ds["goals"][25:]
    errors, trace = [], []
    for i, goal in enumerate(goals):
        q = lab.reset()
        for step in range(150):
            feature = np.append((goal - q - mean) / scale, 1.)
            delta = np.clip(feature @ weights, -.025, .025)
            q = lab.step(q + delta)
            trace.append([i, step * .02, float(np.max(np.abs(goal - q)))])
        errors.append(float(np.max(np.abs(goal - q))))
    with (output / "rollout.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["test_episode", "time_s", "max_joint_error_rad"])
        writer.writerows(trace)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for i in range(len(goals)):
        rows = np.array([r for r in trace if r[0] == i])
        plt.plot(rows[:, 1], rows[:, 2], label=f"episode {25+i}")
    plt.axhline(.02, color="black", linestyle="--", label="success threshold")
    plt.xlabel("Time (s)")
    plt.ylabel("Maximum joint error (rad)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "rollout.png", dpi=160)
    plt.close()
    return {"test_episodes": len(errors), "successes": sum(e < .02 for e in errors),
            "threshold_rad": .02, "final_max_joint_errors_rad": errors,
            "scope": "synthetic joint-reaching demonstrations; fixed-base MuJoCo; no vision, hand, or hardware"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["ik", "collect", "train", "evaluate"])
    p.add_argument("--model", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.command != "train" and args.model is None:
        p.error("--model is required for IK, collection and evaluation")
    if args.command == "train":
        result = {"validation_action_mse": train(args.output)}
    else:
        lab = ArmLab(args.model)
        if args.command == "ik":
            result = lab.ik()
        elif args.command == "collect":
            collect(lab, args.output, args.seed)
            result = {"episodes": 30, "frames": 3000, "seed": args.seed,
                      "joints": ARM, "dt": .02, "split": {"train": [0, 19], "validation": [20, 24], "test": [25, 29]},
                      "model_sha256": hashlib.sha256(args.model.read_bytes()).hexdigest(),
                      "mujoco": mujoco.__version__, "numpy": np.__version__}
        else:
            metadata = json.loads((args.output / "collect.json").read_text())
            if metadata["model_sha256"] != hashlib.sha256(args.model.read_bytes()).hexdigest():
                raise ValueError("evaluation model differs from collection model")
            result = evaluate(lab, args.output)
    (args.output / f"{args.command}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
