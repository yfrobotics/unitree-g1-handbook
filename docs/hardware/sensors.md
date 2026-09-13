# 传感器与感知

感知开发应先回答三个问题：数据来自哪个设备、坐标和单位是什么、时间是否对应当前时刻。接收到消息后，再考虑可视化、建图或抓取算法。

## 数据来源

| 数据 | 常见用途 | 首次检查 |
| --- | --- | --- |
| 关节状态 | 姿态、运动学、执行器诊断 | 编号、角度单位、更新时间和有效关节范围 |
| IMU | 姿态与惯性观测 | 坐标轴、四元数顺序、角速度和加速度含义 |
| 深度相机 | 近距离几何、目标定位 | 实际型号、深度单位、标定和图像配准 |
| 3D 激光雷达 | 空间测量、点云、定位建图 | 点云坐标系、时间戳、视场和发布服务 |
| 手部触觉或压力 | 抓取接触判断 | 是否安装、数据有效性和标定方式 |

G1 公开配置包含深度相机和 3D 激光雷达，具体设备型号、驱动和开放方式仍需按实机确认。[官方产品配置](https://www.unitree.com/g1/)

## 先读取关节与 IMU

完成 [ROS2 集成](../development/ros2.md)后，先查看消息定义和当前话题：

```bash
ros2 interface show unitree_hg/msg/LowState
ros2 interface show unitree_hg/msg/IMUState
ros2 interface show unitree_hg/msg/MotorState
ros2 topic list -t
```

`LowState` 中的 `imu_state` 与 `motor_state` 提供基础机体状态。IMU 定义包含四元数、角速度、加速度、欧拉角和温度字段；不要假定它已经等同于标准 ROS2 的 `sensor_msgs/msg/Imu`。[IMU 消息定义](https://github.com/unitreerobotics/unitree_ros2/blob/master/cyclonedds_ws/src/unitree/unitree_hg/msg/IMUState.msg)

官方状态示例将四元数按 `w, x, y, z` 输出，关节 `q` 和 `dq` 分别按弧度和弧度每秒解释。转换到其他库时显式检查分量顺序和单位。[官方状态读取示例](https://github.com/unitreerobotics/unitree_ros2/blob/master/example/src/src/read_low_state_hg.cpp)

`MotorState` 还定义了估计力矩、温度、电压及状态字段。估计力矩不能直接当作经过标定的接触力；数组中预留或未安装关节的数据也不能作为有效测量。[MotorState 定义](https://github.com/unitreerobotics/unitree_ros2/blob/master/cyclonedds_ws/src/unitree/unitree_hg/msg/MotorState.msg)

## 找到相机和激光雷达数据

先在机器人开发计算单元上检查已部署服务和交付文档，再确认传感器数据是以 ROS2、DDS、视频流还是设备驱动接口提供。安装 SDK 本身不保证相机和点云话题自动出现。

如果数据通过 ROS2 发布，使用以下方法查找类型，不预设固定话题名：

```bash
ros2 topic list -t
```

寻找图像、相机标定或点云对应的消息类型，再对实际话题执行 `ros2 topic info 话题名 --verbose`。如果没有任何相关话题，应先确认驱动或数据服务是否启动，以及它是否运行在另一台计算单元或另一个 ROS 环境中。

图像先检查分辨率、编码、帧率和曝光，再检查彩色与深度是否对齐。点云先看时间戳、`frame_id` 和数值范围，再判断是否需要裁剪或滤波。不要通过反复启动多个驱动实例解决设备占用问题。

## 坐标系与标定

下面是本手册建议的数据验收方法：

1. 画出相机、雷达、躯干、手臂基座和末端之间的坐标关系，记录每个变换的来源。
2. 用实际测量或标定结果确定传感器外参，不用猜测的安装角度代替。
3. 在可视化工具中查看地面、墙面和机器人结构，检查上下、前后和左右方向。
4. 将已知距离的静态物体与深度或点云测量比较，先验证单位再调算法。
5. 移动手臂或机身后检查变换链是否随关节状态更新，避免把动态关系写成静态变换。

在 RViz 中出现点云倾斜或图像定位偏移时，优先查坐标和时间，而不是立即调整控制增益。

## 时间同步与记录

区分设备采样时间、驱动发布时间和电脑接收时间。跨计算单元采集时，先检查各主机时钟与同步方式，再比较不同传感器；`LowState` 的 `tick` 不应未经确认就解释为 Unix 时间戳。

建议先记录短时静态场景，检查消息数、频率、时间是否单调和是否掉帧，再扩大录制规模。图像与点云的数据量较大，先用 `df -h` 检查磁盘余量。

录包方法和回放注意事项见 [ROS2 页面](../development/ros2.md)。记录模型版本、相机内外参、采样配置和环境信息，才能让离线结果与实机实验对应。

## 从感知到动作

感知输出进入抓取或导航控制前，应检查置信度、数据新鲜度、坐标变换和目标可达性。先在静态数据上验证，再用[仿真](../development/simulation.md)测试闭环流程；传感器暂时失效时应有明确的停止或等待行为。

遇到无数据、频率异常或坐标错误，继续阅读[故障排查](../troubleshooting.md)。
