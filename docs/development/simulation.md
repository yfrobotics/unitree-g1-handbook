# 仿真

仿真适合先验证关节映射、消息通信、控制逻辑和任务流程。它不能证明同一程序已具备实机运行条件；模型质量、接触、延迟和执行器特性都会影响迁移结果。

## 选择环境

| 环境 | 主要用途 | 入门时先确认 |
| --- | --- | --- |
| [Unitree MuJoCo](https://github.com/unitreerobotics/unitree_mujoco) | SDK 接口联调、底层控制验证 | G1 模型、DDS 配置和控制器 |
| [Unitree Isaac Lab 仿真](https://github.com/unitreerobotics/unitree_sim_isaaclab) | 操作任务、相机场景和数据采集 | Isaac Sim／Lab 版本、显卡、任务和末端配置 |
| Gazebo 自建环境 | 与已有 ROS2 仿真工程集成 | 自行准备兼容模型、执行器插件和通信桥接 |

下面给出 MuJoCo Python 版本的准备流程。官方仓库同时提供 C++ 和 Python 实现，当前说明侧重底层开发；不要把它当作实机所有高层运控功能的完整复刻。[MuJoCo 项目说明](https://github.com/unitreerobotics/unitree_mujoco#supported-unitree-sdk2-messages)

## 准备独立 Python 环境

在有图形桌面的 Linux 开发电脑上执行。先按 [SDK 页](sdk-setup.md)下载 Python SDK 源码，再建立单独的仿真环境：

```bash
python3 -m venv ~/venvs/g1-sim
source ~/venvs/g1-sim/bin/activate
python -m pip install -e ~/unitree_sdk2_python
python -m pip install mujoco pygame
cd ~
git clone https://github.com/unitreerobotics/unitree_mujoco.git
cd unitree_mujoco
git rev-parse HEAD
```

首次安装成功后保存依赖版本与仓库提交号，后续复现实验使用相同组合。无桌面的服务器需要额外配置显示或无头渲染；下面的查看器流程按本地图形环境编写。

## 明确选择 G1 和仿真网络

打开 `simulate_python/config.py`，修改以下已有字段，其他参数先保持仓库默认值：

```python
ROBOT = "g1"
ROBOT_SCENE = "../unitree_robots/" + ROBOT + "/scene.xml"
DOMAIN_ID = 1
INTERFACE = "lo"
USE_JOYSTICK = 0
PRINT_SCENE_INFORMATION = True
ENABLE_ELASTIC_BAND = True
```

字段名称见[官方配置文件](https://github.com/unitreerobotics/unitree_mujoco/blob/main/simulate_python/config.py)。这里关闭未连接的手柄，并启用用于初始支撑的虚拟弹性带；核对时的[启动代码](https://github.com/unitreerobotics/unitree_mujoco/blob/main/simulate_python/unitree_mujoco.py)支持将其连接到 G1 躯干。

在启动前再次检查网络：仿真和测试程序都使用本机 `lo` 与域 `1`。不要让测试程序自动选中接着实机的网卡。跨电脑仿真时需要重新规划隔离网络，不能直接沿用本机回环设置。

## 启动并检查

```bash
cd ~/unitree_mujoco/simulate_python
source ~/venvs/g1-sim/bin/activate
python unitree_mujoco.py
```

预期会打开场景窗口，并打印关节、连接体和传感器信息。核对加载的是 G1 及预期关节配置。加载模型不等于已经加载稳定站立或行走策略；无控制器时机器人不能自动表现出实机的全部运动能力。

若使用 ROS2 观察仿真，在新的终端加载 [ROS2 消息环境](ros2.md)后设置：

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=1
export ROS_LOCALHOST_ONLY=0
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="lo" priority="default" multicast="default" /></Interfaces></General></Domain></CycloneDDS>'
ros2 daemon stop
ros2 topic list -t
```

确认话题属于仿真后，再读取 `/lowstate`。Python SDK 程序需要在自己的 `ChannelFactoryInitialize` 中设置对应域和网卡；只修改 `ROS_DOMAIN_ID` 不会自动改变任意 SDK 程序的配置。[官方仿真通信示例](https://github.com/unitreerobotics/unitree_mujoco#3-sim-to-real)

## Isaac Lab 与视觉操作

宇树 Isaac Lab 项目提供不同机身和末端组合的操作任务，并使用与实机相同类型的 DDS 接口。选择任务时同时核对机身自由度、末端型号、是否固定基座以及是否启用相机；配置不一致会影响命令维度和观测内容。[官方任务与安装说明](https://github.com/unitreerobotics/unitree_sim_isaaclab)

按所选提交对应的文档安装 Isaac Sim、Isaac Lab 和资源包，再运行该任务的启动命令。资源首次加载较慢时先查看下载和显存日志；不要把修改消息类型当作解决渲染失败的方法。

## 从仿真转到实机前

本手册建议逐项验收：关节顺序和限位正确、目标连续、控制频率和状态超时可测量、退出流程明确、初始姿态一致，以及末端和负载与模型一致。先保存仿真日志，再进入受支撑的实机验证。

仿真中可用的理想位置或速度观测，在关闭实机原有运控服务后未必仍然可用；算法应明确每个观测的实际来源。[官方仿真与实机差异说明](https://github.com/unitreerobotics/unitree_mujoco#supported-unitree-sdk2-messages)

继续阅读：[安全指南](../getting-started/safety.md) · [传感器与感知](../hardware/sensors.md)
