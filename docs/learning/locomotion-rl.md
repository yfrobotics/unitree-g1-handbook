# 行走强化学习与策略部署

本页以宇树 unitree_rl_gym 的 G1 示例理解观测、动作、奖励和 sim-to-sim 流程。它使用简化的 12 动作行走模型，并不控制实验室 G1 的全部 29 个机身关节或 BrainCo2 双手；与 [SONIC 运动跟踪](whole-body.md)的参考轨迹任务也不同。

## 固定环境与训练入口

参考提交为 `276801e46c5d433564f24658bac64f254b7d2d4b`。它使用 Isaac Gym 和旧版 rsl_rl，不应与 Isaac Lab 安装环境混用。按照该提交的[安装文档](https://github.com/unitreerobotics/unitree_rl_gym/blob/276801e46c5d433564f24658bac64f254b7d2d4b/doc/setup_en.md)准备独立 Python 3.8、NVIDIA GPU、PyTorch 与 Isaac Gym，并安装 rsl_rl `v1.0.2`。

在 GPU 开发电脑上：

```bash
git clone https://github.com/unitreerobotics/unitree_rl_gym.git ~/unitree_rl_gym_lab
git -C ~/unitree_rl_gym_lab checkout --detach 276801e46c5d433564f24658bac64f254b7d2d4b
conda activate unitree-rl
cd ~/unitree_rl_gym_lab
python -m pip install -e .
python legged_gym/scripts/train.py --task=g1 --headless --num_envs=64 --max_iterations=10
```

先用短训练确认资源、日志和 checkpoint 写入正常，再调整环境数量与训练轮数。10 次迭代是安装检查，不是可行走策略。官方默认配置与说明见[训练入口](https://github.com/unitreerobotics/unitree_rl_gym/blob/276801e46c5d433564f24658bac64f254b7d2d4b/README.md)。本手册未在 GPU 上执行此训练。

## 观测、动作与频率

固定版本的 G1 actor 使用 47 维观测，critic 配置另有特权观测。部署端排列如下：

| 维度 | 观测内容 |
| --- | --- |
| 0—2 | 缩放后的机体角速度 |
| 3—5 | 机体系重力方向 |
| 6—8 | 缩放后的目标平移/转向速度 |
| 9—20 | 相对默认姿态的 12 个关节角 |
| 21—32 | 缩放后的关节速度 |
| 33—44 | 上一次策略动作 |
| 45—46 | 周期相位的 sin/cos |

来源：[部署代码](https://github.com/unitreerobotics/unitree_rl_gym/blob/276801e46c5d433564f24658bac64f254b7d2d4b/deploy/deploy_mujoco/deploy_mujoco.py)。动作变换为 `q_target = q_default + 0.25 × action`，随后由 PD 产生力矩。`action` 不是力矩，也不是可直接发送到任意关节数组的绝对角。

策略周期等于物理步长乘 decimation。该 MuJoCo 配置使用 `0.002 × 10 = 0.02 s`，即 50 Hz；训练端应从有效配置读取，不仅抄一个频率数字。重力方向、角速度坐标系、默认姿态、缩放、关节顺序和上一动作都必须在训练/部署一致。[配置文件](https://github.com/unitreerobotics/unitree_rl_gym/blob/276801e46c5d433564f24658bac64f254b7d2d4b/deploy/deploy_mujoco/configs/g1.yaml)

## 奖励与域随机化

固定 [G1 配置](https://github.com/unitreerobotics/unitree_rl_gym/blob/276801e46c5d433564f24658bac64f254b7d2d4b/legged_gym/envs/g1/g1_config.py)包含速度跟踪、姿态/高度、动作变化、关节限制、脚部接触等项，以及摩擦、基座附加质量和外力扰动。总奖励上升并不保证脚滑、跌倒或能耗下降。

每次改动先保存原配置与种子，画各奖励分项及 episode 长度，再观察动作。先做一个变量的对照，不用增加奖励权重来掩盖错误观测或关节映射。不同控制频率下，奖励累积与动作平滑惩罚也需要重新检查。

## 导出与 MuJoCo 验证

选定训练日志后，按固定版本参数指定 run/checkpoint；简单情况下：

```bash
python legged_gym/scripts/play.py --task=g1
```

记录实际加载的 run，避免默认选中另一次训练。该 G1 配置采用循环策略，导出通常为 `logs/g1/exported/policies/policy_lstm_1.pt`；部署到多个 episode 时还需核对隐藏状态重置。

先检查仓库预训练模型，再替换成自己的导出：复制 `deploy/deploy_mujoco/configs/g1.yaml` 为同目录的 `g1_lab.yaml`，只修改 `policy_path` 指向实际文件，再运行：

```bash
python deploy/deploy_mujoco/deploy_mujoco.py g1_lab.yaml
```

该路径只使用本地 MuJoCo，不需要机器人网卡。预训练路径 `deploy/pre_train/g1/motion.pt` 与训练产生的文件应分别记录。默认配置有非零前进命令，不把启动后移动误判为异常。

## 验收与实机边界

| 阶段 | 至少记录 |
| --- | --- |
| 训练环境 | 同种子复现、速度误差、episode 长度、跌倒定义 |
| MuJoCo | 站立/前进/转向、脚滑、关节限幅、隐藏状态重置 |
| 扰动测试 | 初始姿态、延迟、质量与摩擦变化后的失败条件 |
| 实机准备 | 原始运控交接、状态来源、控制周期、通信超时、支撑与停止 |

BrainCo2、相机和其他载荷改变惯量与质心；简化模型结果不能直接证明实机兼容。实机部署前应完成[配置记录](../hardware/validated-configurations.md)、[关节映射](../hardware/joint-mapping.md)及[安全流程](../getting-started/safety.md)，按匹配固件的官方部署实现单独验收。这里不提供未经现场验证的整机低层启动命令。
