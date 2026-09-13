# 宇树 G1 使用手册

面向研究人员和开发者的宇树 G1 人形机器人实用指南。

初次使用 G1 时，你可能既感到兴奋，也会遇到令人头疼的问题。本手册是在探索机器人的过程中编写的，重点介绍 G1 EDU 版本，面向使用 G1 开展研究和开发的读者。

初次使用 G1？请先阅读[安全指南](getting-started/safety.md)和[开箱指南](getting-started/unboxing.md)，再按照[网络连接指南](networking/connect-to-robot.md)建立连接。

## 建议阅读顺序

1. 确认设备配置，完成开箱检查，并熟悉遥控器与关机流程。
2. 建立有线连接，验证 IP、SSH 和开发主机信息。
3. 准备 SDK 或 ROS2 环境，先读取状态，确认数据持续更新。
4. 在仿真中验证程序，再按实机测试流程开展开发。

每一步先检查预期结果，再进入下一步。如果只做数据采集，可以先阅读 ROS2 和传感器页面；如果开发抓取任务，还需核对灵巧手和手臂配置。

## 目录

- 入门：[开箱与首次使用](getting-started/unboxing.md)、[遥控器](getting-started/remote-control.md)、[安全指南](getting-started/safety.md)。
- 网络：[连接机器人](networking/connect-to-robot.md)、[连接互联网](networking/connect-to-internet.md)。
- 开发：[SDK 配置](development/sdk-setup.md)、[灵巧手 SDK](development/hand-sdk.md)、[ROS2 集成](development/ros2.md)、[仿真](development/simulation.md)。
- 硬件：[规格与组件](hardware/specs.md)、[传感器与感知](hardware/sensors.md)。
- [故障排查](troubleshooting.md)：按现象定位网络、软件、遥控和传感器问题。

## 如何使用命令与资料

命令主要按 Ubuntu 与 Bash 编写。执行前确认命令所在主机、系统版本、网卡名称和机器人配置；示例 IP、SSID、路径和话题应按页面说明替换。安装或编译成功并不表示运动程序已经适配实机。

本轮资料核对日期为 2026-09-13，各页在相关步骤附有官方来源。本手册中的实验顺序和排查建议用于辅助工作；遥控按键、启动姿态、固件支持范围和硬件限值需要以交付设备对应的说明为准。

## 关于本手册

本手册由社区编写，属于非官方资料，与宇树科技无关联，也未获得其背书。内容基于 G1 EDU 的实际使用经验，旨在补充官方文档中未充分覆盖的内容。

发现错误或希望补充内容？欢迎在 [GitHub](https://github.com/yfrobotics/unitree-g1-handbook) 上参与贡献。
