# 配置与验证记录

本页把设备负责人确认的配置、上游源码核对与本地运行结果分别记录。资料核对日期为 2026-09-26；没有连接实机的测试不代表该固件或设备已经兼容。

## 实验室目标配置

| 项目 | 已知信息 | 尚需记录 |
| --- | --- | --- |
| 机身 | G1 EDU，29-DoF | 序列号、固件、当前模式 |
| 双手 | BrainCo2；本手册按 Revo2 接口整理 | 铭牌、左右序列号、手固件与服务版本 |
| XR | Meta Quest 3 | 系统/浏览器版本、手势或手柄模式 |
| 相机/雷达 | 原装配置 | 型号、序列号、驱动、数据访问方式 |
| PC2 | 用户开发计算单元 | 型号、架构、OS、JetPack（如适用） |

以上来自设备负责人提供的信息，未替代实物验收。上游 teleop 文档的内置相机为 D435i，产品公开表只保证深度相机与 3D 雷达；因此不把雷达型号、固定 IP、腕部相机或某款 Jetson 写成实验室既定配置。

## 固定上游提交

以下提交用于本轮源码核对，不构成“整套组合已实机验证”的兼容性保证。机器可读清单见 [upstream-revisions.json](https://github.com/yfrobotics/unitree-g1-handbook/blob/main/examples/config/upstream-revisions.json)。

| 仓库 | 提交 |
| --- | --- |
| [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python/tree/814556d15970dd2ecf1c9984e845ca02ab07e206) | `814556d15970dd2ecf1c9984e845ca02ab07e206` |
| [unitree_sdk2](https://github.com/unitreerobotics/unitree_sdk2/tree/63096d0ac0c5d2dec9d6e0c22cd5233410ca2f36) | `63096d0ac0c5d2dec9d6e0c22cd5233410ca2f36` |
| [unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco/tree/1eb6642e3f3fdfb7fb13a9794fd6a2dd93ea0e7d) | `1eb6642e3f3fdfb7fb13a9794fd6a2dd93ea0e7d` |
| [xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate/tree/817fb00c63cde15e5f24a0f8fa08e1e33ed89d3b) | `817fb00c63cde15e5f24a0f8fa08e1e33ed89d3b` |
| [teleimager](https://github.com/unitreerobotics/teleimager/tree/57cf2a40572227273fa001cd17833b755331ec97) | `57cf2a40572227273fa001cd17833b755331ec97` |
| [brainco_hand_service](https://github.com/unitreerobotics/brainco_hand_service/tree/d71996b6999edb2f838a3dca3d9621429a2ef966) | `d71996b6999edb2f838a3dca3d9621429a2ef966` |
| [unitree_lerobot](https://github.com/unitreerobotics/unitree_lerobot/tree/41c2805742de879ddab2d8d6beaeaf215f876395) | `41c2805742de879ddab2d8d6beaeaf215f876395` |
| [lerobot](https://github.com/huggingface/lerobot/tree/a5b29d430105f5235eb05bbf2db5a0d747a869d6) | `a5b29d430105f5235eb05bbf2db5a0d747a869d6` |
| [unitree_sim_isaaclab](https://github.com/unitreerobotics/unitree_sim_isaaclab/tree/e30c25b1dffdf92ada1d6c8c1fe9a47bdde0fecc) | `e30c25b1dffdf92ada1d6c8c1fe9a47bdde0fecc` |
| [unitree_rl_gym](https://github.com/unitreerobotics/unitree_rl_gym/tree/276801e46c5d433564f24658bac64f254b7d2d4b) | `276801e46c5d433564f24658bac64f254b7d2d4b` |

## 本地验证矩阵

| 项目 | 环境/输入 | 结果与边界 |
| --- | --- | --- |
| C++ 只读订阅器 | x86_64，GCC 13.3，固定 C++ SDK | 编译/链接通过；本环境 DDS 初始化受限，未完成消息收发验收 |
| Python SDK 导入 | Python 3.12，CycloneDDS 0.10.2 | 安装/导入通过；本机 loopback 初始化在 DDS 原生库中中止，未完成真实订阅 |
| 状态诊断/演示检查 | Python unittest，合成边界样例 | 重复 tick、消息中断、缺图像、NaN、帧断号和维度变化测试 |
| 左臂 IK + 跟踪 | Python 3.12，MuJoCo 3.3.7，固定 29-DoF 模型 | [IK 输出](../_static/validation/arm-ik.json)，固定基座、无 BrainCo2 |
| CPU 行为克隆 | NumPy 2.2.6，合成 30 条示范 | [完整记录](../_static/validation/first-policy.json)，测试 5/5 关节到达，非抓取 |
| Quest 3 / Revo2 服务 | 固定源码与文档 | 未完成实验室实机联调 |
| 单 RGB LeRobot 转换/ACT | 固定转换器与子模块接口 | 已核对/静态检查；待真实数据和训练环境验证 |
| Isaac Gym 行走 RL | 固定任务与部署源码 | 未执行 GPU 训练或实机部署 |
| 原装相机与雷达 | 设备识别与条件式驱动流程 | 待现场型号确认与标定 |

本地结果不能推断固件兼容、机载实时性能或实验室任务成功率。可重复命令见对应教程，后续实测应附[实验报告](../maintenance/records.md)，记录开始姿态、停止流程、配置修改与失败次数。
