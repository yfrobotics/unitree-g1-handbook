# 第一个 SDK 程序：只读状态

本页使用仓库自带的 Python 与 C++ 示例读取 G1 状态，不创建命令发布器，也不切换运控模式。完成后应能区分“库已安装”“消息已到达”和“设备数据正在更新”。本地编译与测试范围见[配置与验证记录](../hardware/validated-configurations.md)。

## 准备与版本

先完成 [SDK 配置](sdk-setup.md)。下面假设本手册克隆在 `~/unitree-g1-handbook`，所有命令在开发电脑执行。源代码位于 [examples/read_state.py](https://github.com/yfrobotics/unitree-g1-handbook/blob/main/examples/read_state.py) 与 [examples/cpp](https://github.com/yfrobotics/unitree-g1-handbook/tree/main/examples/cpp)。

示例依据 Python SDK `814556d15970dd2ecf1c9984e845ca02ab07e206` 的 [ChannelSubscriber](https://github.com/unitreerobotics/unitree_sdk2_python/blob/814556d15970dd2ecf1c9984e845ca02ab07e206/unitree_sdk2py/core/channel.py) 和 C++ SDK `63096d0ac0c5d2dec9d6e0c22cd5233410ca2f36` 的 [G1 状态类型](https://github.com/unitreerobotics/unitree_sdk2/blob/63096d0ac0c5d2dec9d6e0c22cd5233410ca2f36/include/unitree/idl/hg/LowState_.hpp)编写。新建工作副本时可用 `git checkout --detach 提交号` 固定版本；不要覆盖机器人已有部署。

## Python：先连接本机仿真

按[仿真页](simulation.md)启动 G1，使用域 `1`、网卡 `lo`。另开终端：

```bash
source ~/venvs/g1-sdk/bin/activate
cd ~/unitree-g1-handbook
python examples/read_state.py --interface lo --domain 1 --joint 0 --seconds 10 --freshness arrival
```

程序每 0.25 秒打印一次最新状态；这是终端显示频率，不是机器人发布频率。`--joint` 是 DDS 数组槽位，先对照[关节映射](../hardware/joint-mapping.md)，不能填写模型的 `qpos` 地址。

固定版本 MuJoCo Python 桥接器没有递增 `LowState.tick`，所以仿真使用 `--freshness arrival` 只检查消息到达间隔；它不能证明设备采样时间更新。实机默认 `tick` 模式同时检查接收与 tick 变化，先确认固件定义。桥接实现见[发布函数](https://github.com/unitreerobotics/unitree_mujoco/blob/1eb6642e3f3fdfb7fb13a9794fd6a2dd93ea0e7d/simulate_python/unitree_sdk2py_bridge.py)。

```text
OK received=... tick=... q=... dq=... quat_wxyz=[...]
```

以上是输出格式示意。`q` 为弧度，`dq` 为弧度每秒，四元数按 `w,x,y,z` 输出。计数是当前进程收到的消息数；不要把 `tick` 当作 Unix 时间或跨主机同步时钟。

## 实机只读检查

确认[有线连接](../networking/connect-to-robot.md)与设备的 DDS 域，再将网卡替换为电脑实际接口：

```bash
python examples/read_state.py --interface enp3s0 --domain 0 --joint 0 --seconds 10
```

不需要停止官方运控服务。保持机器人当前受控状态；如果系统使用不同域，按交付配置替换。退出脚本仅停止订阅，不改变机器人的状态。

## C++：构建和运行

在已安装 C++ SDK 的电脑上：

```bash
cd ~/unitree-g1-handbook
cmake -S examples/cpp -B build/read-state -DCMAKE_PREFIX_PATH=/opt/unitree_robotics
cmake --build build/read-state --parallel 2
./build/read-state/read_state lo 1 arrival
```

程序固定监测槽位 0，运行 10 秒。实机连接使用 `./build/read-state/read_state enp3s0 0`。如果安装前缀不同，修改 CMake 路径；找不到动态库时先检查 SDK 安装是否包含 DDS 库，不要混用另一套 DDS 二进制文件。

## 判断结果

| 输出 | 含义 | 下一步 |
| --- | --- | --- |
| `WAITING` | 初始化后尚无消息，仍在超时窗口内 | 等待第一次状态 |
| `OK` | 消息到达且 tick 最近有变化 | 核对姿态、关节槽位与单位 |
| `NO_MESSAGES` | 超过默认 1 秒未收到状态 | 查网卡、域、发布服务和消息定义 |
| `FROZEN_TICK` | 消息还在到达，但 tick 长时间不变 | 核对固件对 tick 的定义与发布服务 |
| `NONFINITE` | 被观察的关节或 IMU 含 NaN/Inf | 保存日志，停止后续控制调试 |

Python 可用 `--timeout` 修改诊断阈值。阈值属于本示例的接收端检查，不是实机看门狗参数。出现过异常或始终没有消息时退出码为 `2`，正常结束为 `0`；参数错误也会返回非零。tick 回绕或重启时变化仍会被识别，不对其差值换算频率。

本例只检查选中的一个关节和四元数，不承担整机健康诊断。下一步在[手臂运动学实验](arm-control.md)中处理目标与模型，或使用 [ROS2](ros2.md)录制原始状态。
