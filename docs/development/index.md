# 开发指南

从 SDK 和状态读取开始，逐步接入手臂、灵巧手与 ROS2。在仿真中检查消息、关节映射和控制流程，再开展受控实机验证。

## 本章内容

| 页面 | 阅读重点 |
| --- | --- |
| [SDK 配置](sdk-setup.md) | 准备依赖并验证通信 |
| [第一个只读程序](first-program.md) | Python/C++ 状态订阅与消息超时诊断 |
| [手臂控制与逆运动学](arm-control.md) | 固定基座位姿求解与动力学跟踪 |
| [灵巧手 SDK 与操作](hand-sdk.md) | 核对手型、接口与动作映射 |
| [BrainCo2 灵巧手](brainco2.md) | Revo2 串口服务、归一化通道与只读验收 |
| [Quest 3 遥操作](teleoperation.md) | 实验室配置的视频、跟踪、启动与录制 |
| [ROS2 集成](ros2.md) | 建立消息环境并读取机器人状态 |
| [仿真](simulation.md) | 验证机器人模型与控制流程 |

## 建议阅读路径

先完成 SDK 与只读程序，再查[关节映射](../hardware/joint-mapping.md)。无实机时可直接进入手臂离线实验；使用实验室设备时继续 BrainCo2 和 Quest 3 流程，再进入[数据采集](../learning/data-collection.md)。ROS2 与仿真页面提供所需基础环境。
