# 下载并编译 SDK

本页在 Ubuntu 开发环境中准备 C++ 或 Python SDK，并检查安装结果。先完成[连接机器人](../networking/connect-to-robot.md)；编译可在不连接实机的情况下进行。

## 选择接口与运行位置

| 接口 | 适合的工作 |
| --- | --- |
| `unitree_sdk2` | C++ 应用、阅读官方控制示例、集成已有 CMake 项目 |
| `unitree_sdk2_python` | Python 原型、数据读取、算法联调 |
| `unitree_ros2` | ROS2 消息、记录与可视化，见 [ROS2 集成](ros2.md) |

先检查机器人是否已有 SDK。已有部署往往包含适配当前固件的版本，应记录其提交号并保留原目录，再创建自己的工作副本。

```bash
uname -m
cat /etc/os-release
cmake --version
g++ --version
```

官方 C++ SDK 列出的预编译环境为 Ubuntu 20.04、GCC 9.4，支持 `aarch64` 和 `x86_64`。其他组合需自行验证依赖和 ABI 兼容性。[C++ SDK 环境说明](https://github.com/unitreerobotics/unitree_sdk2#prebuild-environment)

## 编译 C++ SDK

以下在准备运行 SDK 的开发主机上执行。安装依赖后，将仓库放在用户主目录中：

```bash
sudo apt update
sudo apt install git cmake g++ build-essential libyaml-cpp-dev libeigen3-dev libboost-all-dev libfmt-dev
cd ~
git clone https://github.com/unitreerobotics/unitree_sdk2.git
cd unitree_sdk2
git rev-parse HEAD
cmake -S . -B build
cmake --build build --parallel 2
```

这里限制为两个并行编译任务，便于在内存较小的开发计算单元上操作；可按可用资源调整。构建退出码为零后，检查 `build` 目录中的目标文件。编译成功不会让机器人运动。

需要在自己的 CMake 项目中使用 SDK 时，再安装到独立前缀：

```bash
cmake -S . -B build -DCMAKE_INSTALL_PREFIX=/opt/unitree_robotics
sudo cmake --install build
```

以上构建和安装流程依据[官方 SDK 说明](https://github.com/unitreerobotics/unitree_sdk2#build-examples)整理。自己的项目可参考仓库内的 `example/cmake_sample`；使用其他安装位置时，需要为 CMake 提供对应前缀。

## 安装 Python SDK

使用独立虚拟环境，避免把依赖装进机器人已有应用的 Python 环境：

```bash
sudo apt install python3-venv python3-pip
cd ~
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
python3 -m venv ~/venvs/g1-sdk
source ~/venvs/g1-sdk/bin/activate
python -m pip install -e ~/unitree_sdk2_python
python -m pip check
python -c "from unitree_sdk2py.core.channel import ChannelFactoryInitialize; print('SDK 导入成功')"
```

官方 Python SDK 列出的依赖包括 Python 3.8 及以上和 CycloneDDS 0.10.2。若出现 `Could not locate cyclonedds`，按[官方安装故障说明](https://github.com/unitreerobotics/unitree_sdk2_python#faq)准备兼容的 CycloneDDS，并让 `CYCLONEDDS_HOME` 指向实际安装目录，再重试。不要把随机找到的 DDS 版本或另一架构的库混入环境。

## 第一次通信验证

安装验证只证明库可导入。接下来应按以下顺序验证应用：

1. 确认运行主机、机器人网卡名称和目标 DDS 域。
2. 阅读示例源码，确认目标为 G1，消息类型、关节配置和实际设备一致。
3. 先订阅状态，观察数据是否持续更新；可使用 [ROS2 页的只读命令](ros2.md)。
4. 将需要发布控制命令的程序放到[仿真环境](simulation.md)中验证。
5. 实机运动前落实[安全指南](../getting-started/safety.md)，确认控制权和停止流程。

G1 专用示例集中在 [`example/g1`](https://github.com/unitreerobotics/unitree_sdk2/tree/main/example/g1)。仓库根 README 中的四足运动示例不能直接作为 G1 入门命令。示例名称包含 `state`、`test` 或 `example`，也不代表程序一定只读。

## 记录可复现环境

每次实验至少记录 SDK 提交号、系统架构、编译器、机器人固件、机身自由度和末端执行器型号。Python 项目可额外保存依赖清单：

```bash
python -m pip freeze > g1-python-requirements.txt
```

编译缺头文件时查开发包；链接失败时查架构和库路径；安装成功却收不到数据时查[网络和 DDS](../troubleshooting.md)，不要反复重装 SDK。
