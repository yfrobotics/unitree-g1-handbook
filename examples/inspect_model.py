"""Export MuJoCo joint/actuator addresses and local axes; no hardware access."""
import argparse
import csv
import sys
import mujoco

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("model")
args = p.parse_args()
m = mujoco.MjModel.from_xml_path(args.model)
w = csv.writer(sys.stdout)
w.writerow(["actuator_index", "joint_name", "qpos_address", "velocity_address", "axis_x", "axis_y", "axis_z", "lower_rad", "upper_rad"])
for aid in range(m.nu):
    jid = m.actuator_trnid[aid, 0]
    if m.actuator_trntype[aid] != mujoco.mjtTrn.mjTRN_JOINT:
        raise ValueError("example expects direct joint actuators")
    w.writerow([aid, m.joint(jid).name, m.jnt_qposadr[jid], m.jnt_dofadr[jid],
                *m.jnt_axis[jid], *m.jnt_range[jid]])
