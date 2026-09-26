# BrainCo2（Revo2）灵巧手

本实验室配置为 G1 EDU 29-DoF 与 BrainCo2 双手。本页按宇树官方 Revo2 串口转 DDS 服务整理，供核对驱动与数据接口；设备铭牌、固件、串口身份和实机动作仍需现场验收。BrainCo2 不适用 Dex3 的七关节弧度命令。

## 接口与单位

宇树 [BrainCo 服务](https://github.com/unitreerobotics/brainco_hand_service/tree/d71996b6999edb2f838a3dca3d9621429a2ef966)明确面向第二代 Revo2，每手 6 个控制通道，通过 USB 转串口连接。机身与手的通道分别计数，不应把“29+12”直接写成模型的可动关节数。

| 项目 | 此服务中的定义 |
| --- | --- |
| 左手命令/状态 | `rt/brainco/left/cmd` / `rt/brainco/left/state` |
| 右手命令/状态 | `rt/brainco/right/cmd` / `rt/brainco/right/state` |
| 消息类型 | `unitree_go::msg::dds_::MotorCmds_` / `MotorStates_` |
| 通道 0—5 | 拇指、拇指辅助、食指、中指、无名指、小指 |
| 位置 `q`、命令速度 `dq` | 归一化到 `[0,1]`，不是 rad 与 rad/s |

上述定义来自固定版本的 [README](https://github.com/unitreerobotics/brainco_hand_service/blob/d71996b6999edb2f838a3dca3d9621429a2ef966/README_zh-CN.md)及[转换实现](https://github.com/unitreerobotics/brainco_hand_service/blob/d71996b6999edb2f838a3dca3d9621429a2ef966/main.cpp)。不要把 SDK 字段名称相同理解为物理单位相同，也不要用渲染模型所有从动关节的数量决定消息维度。

## 检查与编译

在机器人开发计算单元 PC2 检查当前服务和串口。先确认是否已预装，避免两个进程同时访问同一只手：

```bash
ls -l /dev/serial/by-id/
ps -ef | rg 'brainco|stark'
systemctl list-units --type=service | rg -i 'brainco|hand'
```

没有 `/dev/serial/by-id/` 不代表一定没有串口；结合交付资料检查 `/dev/ttyUSB*` 和服务日志。记录左右手序列号与设备路径，不按插入顺序推断左右。

如需新建服务副本，先完成 [C++ SDK 安装](sdk-setup.md)，再编译：

```bash
sudo apt install libspdlog-dev libfmt-dev
git clone https://github.com/unitreerobotics/brainco_hand_service.git ~/brainco_hand_service_lab
git -C ~/brainco_hand_service_lab checkout --detach d71996b6999edb2f838a3dca3d9621429a2ef966
cmake -S ~/brainco_hand_service_lab -B ~/brainco_hand_service_lab/build \
  -DCMAKE_CXX_FLAGS="-I/opt/unitree_robotics/include -I/opt/unitree_robotics/include/ddscxx" \
  -DCMAKE_EXE_LINKER_FLAGS="-L/opt/unitree_robotics/lib -Wl,-rpath,/opt/unitree_robotics/lib"
cmake --build ~/brainco_hand_service_lab/build --parallel 2
```

厂商库架构必须与 PC2 一致。该固定版本源码扫描串口并使用 460800 波特率；这属于服务实现，其他驱动不一定相同。

此服务的 CMake 直接链接 SDK 库，未使用 `find_package(unitree_sdk2)`，所以安装在 `/opt` 时显式提供头文件与库路径；安装在其他目录时同步替换。现场编译还需使用 SDK 页面列出的 Boost、yaml-cpp 等依赖。

## 服务启动不是只读操作

该版本服务在工作线程中持续调用位置/速度写入函数，初始命令位置为零；没有外部命令发布器时也不能把启动服务视为只读。首次启动前，双手空载、周围无物体夹持，机身与手臂处于确认过的支撑状态。

完成上述检查后，由设备操作者在 PC2 启动，`eth0` 替换为 PC2 的实际 DDS 网卡：

```bash
cd ~/brainco_hand_service_lab/bin
sudo ./brainco_hand_server --network_interface eth0
```

参数名以该版本[参数定义](https://github.com/unitreerobotics/brainco_hand_service/blob/d71996b6999edb2f838a3dca3d9621429a2ef966/include/param.h)为准。官方 `test_brainco_hand_server` 会反复握拳和张开，不用作首次状态测试。本手册不自动设置开机启动。

## 只读验收

在已运行服务的前提下，开发电脑加载 [ROS2 环境](ros2.md)，查找实际状态话题：

```bash
ros2 topic list -t
ros2 interface show unitree_go/msg/MotorStates
ros2 topic info /brainco/left/state --verbose
ros2 topic echo /brainco/left/state --once --qos-reliability best_effort
ros2 topic echo /brainco/right/state --once --qos-reliability best_effort
```

两侧应分别有 6 个通道。确认读数有限、服务持续刷新、左右身份与实物一致。部分状态字段与手厂商接口并不一一等价，应阅读服务中的字段赋值，不把电流或温度猜作力/力矩。

## 与 Quest 3、学习数据的关系

固定版本 `xr_teleoperate` 使用 `--ee brainco`，同时支持手势或手柄输入。先走[遥操作检查流程](teleoperation.md)，再执行单指、小范围、空载操作与正常退出。关闭控制端并不保证服务释放或停止重复最后目标，应将断连行为纳入现场验收。

双臂 14 个弧度通道加双手 12 个归一化通道构成该配置的 26 维操作向量。训练时记录每段的顺序和单位，不使用 Dex3 的 28 维配置；单目相机适配见[数据采集](../learning/data-collection.md)。
