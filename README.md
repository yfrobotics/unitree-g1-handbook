# 宇树 G1 使用手册

面向初学者的宇树 G1 使用指南。本手册由[云飞机器人实验室](https://yfrobotics.github.io/)编写，重点介绍 G1 EDU 版本，主要面向使用 G1 开展研究或开发的读者。

**在 Wiki 上阅读完整手册：[https://yfrobotics.github.io/unitree-g1-handbook/](https://yfrobotics.github.io/unitree-g1-handbook/)**

## 涵盖主题

- 入门指南（开箱、遥控器使用、安全注意事项）
- 网络连接（连接机器人、访问互联网）
- 开发指南（SDK、灵巧手 SDK、ROS2、仿真）
- 具身学习（开源数据集集合、VLA 模型与 G1 适配）
- 硬件（规格、传感器）
- 故障排查

## 问题反馈

如有任何问题，欢迎提交拉取请求（Pull Request）或议题（Issue）。

## 从哪里开始

首次使用请先阅读[安全指南](docs/getting-started/safety.md)和[开箱指南](docs/getting-started/unboxing.md)。开发者可继续完成[有线连接](docs/networking/connect-to-robot.md)、[SDK 配置](docs/development/sdk-setup.md)和 [ROS2 状态读取](docs/development/ros2.md)，再进入[仿真](docs/development/simulation.md)与实机联调。

正文按实际操作流程组织，包含前置条件、配置步骤、结果检查和官方来源。硬件与固件存在版本差异，请先核对交付配置。

操作学习资源见[开源数据集集合](docs/learning/datasets.md)和 [VLA：视觉、语言与动作](docs/learning/vla.md)，涵盖 G1 官方数据、跨机型数据、模型入口及训练评测建议。

## 本地预览

在仓库根目录创建 Python 虚拟环境并启动文档站：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdocs serve
```

打开终端显示的本地地址即可预览。发布前运行 `mkdocs build --strict` 检查构建，页面内容位于 `docs/`，导航配置位于 `mkdocs.yml`。

## 参与完善

补充操作经验时请注明机身自由度、末端配置、固件和软件版本，并链接对应的官方资料。步骤应写明执行主机和预期结果；涉及运动的示例应说明起始条件与停止方式。问题报告格式见[故障排查](docs/troubleshooting.md)。
