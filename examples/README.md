# G1 handbook examples

Run commands from the repository root. These examples supplement the Chinese tutorials.

| File | Purpose | Dependencies |
| --- | --- | --- |
| `read_state.py` | Read-only G1 LowState subscriber; arrival/tick diagnostics | Pinned Unitree Python SDK |
| `cpp/` | Read-only C++ subscriber | Pinned C++ SDK, CMake, compiler |
| `inspect_model.py` | Export joint names, addresses, axes and limits | `requirements-sim.txt` |
| `arm_lab.py` | Fixed-base IK, physics tracking, synthetic behavior cloning | `requirements-sim.txt` |
| `inspect_episode.py` | Validate raw XR episode structure and export CSV | Python 3.10+ standard library |
| `convert_brainco2.py` | Single-RGB, 26-dimensional BrainCo2 dataset conversion | Pinned Unitree LeRobot; `--check-only` uses standard library |
| `config/` | Source revisions and camera configuration | Replace hardware-specific fields before use |
| `data/synthetic/` | Tiny schema fixture with synthetic pixels and states | Not robot data or a training dataset |

The SDK examples create no command publishers or mode switches. The arm lab does not import any SDK. The conversion wrapper never uploads data and refuses to replace an existing dataset. Upstream hand/teleoperation services described in the handbook can move hardware; they are separate from these local examples.

```bash
python3 -m unittest discover -s examples/tests -v
python3 examples/inspect_episode.py examples/data/synthetic/reach/episode_0000/data.json
python3 examples/convert_brainco2.py --raw-dir examples/data/synthetic --repo-id local/schema-check --check-only
```

Simulation setup and commands: [arm tutorial](../docs/development/arm-control.md), [learning tutorial](../docs/learning/first-policy.md). Source pins and actual verification boundaries: [validation record](../docs/hardware/validated-configurations.md).
