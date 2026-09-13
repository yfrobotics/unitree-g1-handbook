# ROS2 集成

本页以 Ubuntu 22.04 和 ROS2 Humble 为例，建立 G1 的只读状态订阅。先完成[有线连接](../networking/connect-to-robot.md)，并在开发电脑安装 ROS2 Humble。宇树仓库将这一系统组合列为推荐的已测试环境。[官方环境说明](https://github.com/unitreerobotics/unitree_ros2#system-requirements)

## 通信关系

宇树接口使用 DDS，ROS2 可通过兼容的中间件和消息定义参与通信。需要同时匹配网卡、DDS 域、消息类型和 QoS；能通过 SSH 登录，不代表这些条件已满足。

G1 的底层状态使用 `unitree_hg/msg/LowState`。该消息包含 IMU、关节状态、遥控数据等字段；它的关节数组容量为 35，不代表你的机身装有 35 个关节。[消息定义](https://github.com/unitreerobotics/unitree_ros2/blob/master/cyclonedds_ws/src/unitree/unitree_hg/msg/LowState.msg)

## 安装消息包

在已安装 Humble 的**开发电脑**执行：

```bash
sudo apt update
sudo apt install git python3-colcon-common-extensions ros-humble-rmw-cyclonedds-cpp ros-humble-rosidl-generator-dds-idl libyaml-cpp-dev
cd ~
git clone https://github.com/unitreerobotics/unitree_ros2.git
source /opt/ros/humble/setup.bash
cd ~/unitree_ros2/cyclonedds_ws
colcon build --packages-select unitree_go unitree_hg unitree_api
source install/setup.bash
ros2 interface show unitree_hg/msg/LowState
```

这里先只编译消息包，以便完成状态查看。官方仓库还包含多个机型的控制示例，初次通信验证无需启动它们。Humble 的 CycloneDDS 配置与旧版 Foxy 流程不同，不要直接照抄 Foxy 的依赖编译步骤。[官方安装说明](https://github.com/unitreerobotics/unitree_ros2#install-unitree-ros2-package)

## 设置实机通信环境

每个用于通信的新终端都需要加载环境。将 `enp3s0` 替换为电脑实际连接机器人的网卡：

```bash
source /opt/ros/humble/setup.bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=0
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="enp3s0" priority="default" multicast="default" /></Interfaces></General></Domain></CycloneDDS>'
ros2 daemon stop
ros2 topic list -t
```

网卡绑定方式依据[宇树 ROS2 配置示例](https://github.com/unitreerobotics/unitree_ros2#connect-to-unitree-robot)。这里使用实机默认域 `0`；若设备被配置为其他域，需保持一致。仿真应使用独立配置，见[仿真页面](simulation.md)。停止 ROS2 CLI 后台进程是为了让后续查询重新采用当前环境，不会停止机器人控制服务。

## 读取第一条状态

先在话题列表中确认实际存在 `/lowstate`，并且类型为 `unitree_hg/msg/LowState`，再执行：

```bash
ros2 topic info /lowstate --verbose
ros2 topic echo /lowstate unitree_hg/msg/LowState --once --qos-reliability best_effort
ros2 topic hz /lowstate
```

以上命令只读取数据；频率查看可用 `Ctrl+C` 结束。官方 [`read_low_state_hg` 示例](https://github.com/unitreerobotics/unitree_ros2/blob/master/example/src/src/read_low_state_hg.cpp)也使用 `lowstate`，并提供低频 `lf/lowstate` 的选择。以设备实际发布的话题为准。

读取成功后检查数据是否持续刷新、数值是否有限、关节状态是否与机器人姿态相符。频率命令测得的是订阅端实际接收情况，不应直接当作机器人内部控制频率。

## 话题可见但没有数据

先比较发布端和订阅端的 QoS。传感器发布端若使用 `best_effort`，要求 `reliable` 的订阅端可能无法匹配。可靠性之外，持久性等策略也可能影响匹配。[ROS2 QoS 兼容性说明](https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst)

再检查网卡、域号、消息包版本、组播转发和防火墙。若同时打开了多个 ROS2 发行版终端，使用新的干净终端重新加载上述环境。

## 记录与回放

需要留存实验数据时，可先只录一个状态话题：

```bash
ros2 bag record /lowstate
```

录制结束后用 `Ctrl+C` 正常退出，记录生成的目录，再用 `ros2 bag info 目录名` 检查实际消息数。查看到话题并不保证录包已收到数据。

回放会重新发布消息。应在与实机隔离的域和网络环境中分析数据，尤其不要把包含控制命令的话题包直接回放到实机网络。图像、点云及坐标系处理继续阅读[传感器与感知](../hardware/sensors.md)。
