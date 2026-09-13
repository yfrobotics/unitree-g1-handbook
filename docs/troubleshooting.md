# 故障排查

先记录现象，再从供电与状态、网络、通信、应用逐层检查。机器人有失稳、碰撞或明显硬件异常时，先按[安全指南](getting-started/safety.md)处理，再进行软件排查。

## 按现象定位

| 现象 | 首先检查 | 相关页面 |
| --- | --- | --- |
| 无法开机或反复初始化 | 电池、锁扣、起始姿态、App 告警 | [开箱](getting-started/unboxing.md) |
| 遥控器无响应 | 电量、绑定对象、DL 链路、当前控制模式 | [遥控器](getting-started/remote-control.md) |
| ping 不通 | 网线、网卡地址、子网和路由 | [连接机器人](networking/connect-to-robot.md) |
| ping 通但 SSH 失败 | SSH 服务、账户、认证和主机指纹 | 本页 SSH 检查 |
| SSH 正常但 SDK 无数据 | 网卡绑定、DDS 域、消息类型、组播 | [ROS2](development/ros2.md) |
| Wi-Fi 已连接但不能下载 | 默认路由、DNS、代理和系统时间 | [互联网连接](networking/connect-to-internet.md) |
| 编译或导入失败 | 依赖、架构、虚拟环境、库路径 | [SDK 配置](development/sdk-setup.md) |
| 灵巧手单侧无数据 | 末端型号、左右侧名称、状态服务、连接器 | [灵巧手](development/hand-sdk.md) |
| 图像或点云异常 | 驱动、时间、编码、坐标和标定 | [传感器](hardware/sensors.md) |
| 仿真启动失败 | 模型资源、运行目录、显示环境、依赖 | [仿真](development/simulation.md) |

## 网络检查

以下在开发电脑执行，地址替换为实机交付配置：

```bash
ip -br link
ip -br addr
ip route get 192.168.123.164
ping -c 4 192.168.123.164
ip neigh show
```

网口未连接时先换线或检查接口；路由指向 Wi-Fi/VPN 时先修复选路；邻居解析持续失败时核对目标地址、接线和同网段配置。不要把电脑设置成与机器人相同的 IP。

## SSH 连接失败

```bash
ssh -v -o ConnectTimeout=5 unitree@192.168.123.164
```

| 提示 | 含义与下一步 |
| --- | --- |
| `Connection timed out` | 网络路径、防火墙或目标服务无响应，回到网络检查 |
| `Connection refused` | 收到了明确拒绝，检查 SSH 服务是否启用及端口是否正确 |
| `Permission denied` | 已进入认证阶段，核对账户、密码或密钥 |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | 先核实设备身份、重装记录及新指纹，再更新本地记录 |

使用真实账户信息，不反复尝试默认密码。共享调试日志前检查其中的主机名、用户名和本地路径，去掉不需要公开的信息。

## DDS 或 ROS2 无数据

在发生问题的终端检查当前环境：

```bash
printenv RMW_IMPLEMENTATION ROS_DOMAIN_ID ROS_LOCALHOST_ONLY CYCLONEDDS_URI
ros2 topic list -t
```

按顺序核对以下项目：

1. 程序使用的网卡属于**运行程序的主机**，并连接到目标网络。
2. 实机与仿真没有混用域号和接口；本手册的本机仿真采用域 `1`、`lo`。
3. G1 底层消息使用 `unitree_hg`，没有误用四足机型的定义。
4. 状态话题在当前模式确实由设备发布；订阅端类型与设备一致。
5. 发布端和订阅端的 QoS 兼容。
6. 交换机、无线接入点、VPN 或防火墙没有阻断所需发现与数据通信。

话题可见但没有消息时，先用 `ros2 topic info 话题名 --verbose` 查看类型和 QoS。环境修改后可执行 `ros2 daemon stop`，再重新查询。QoS 不兼容可能阻止消息传递，详见[ROS2 官方说明](https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst)。

不要直接关闭整台电脑的防火墙作为长期修复；根据实际网络与服务配置解决具体规则问题。

## SDK 构建和运行失败

| 提示或现象 | 建议处理 |
| --- | --- |
| 缺少头文件 | 按构建日志确认缺失开发包，参考 SDK 依赖列表 |
| 找不到 `unitree_sdk2` | 检查安装前缀和 `CMAKE_PREFIX_PATH` |
| `Exec format error` | 核对程序与主机是 `aarch64` 还是 `x86_64` |
| `Could not locate cyclonedds` | 按 Python SDK 说明安装兼容 DDS 并设置路径 |
| Python 导入不到 SDK | 检查 `python -m pip --version` 是否属于当前虚拟环境 |
| 编译进程被系统终止 | 查看可用内存和系统日志，再降低并行编译数 |

依赖与安装步骤见 [C++ SDK 文档](https://github.com/unitreerobotics/unitree_sdk2)和 [Python SDK 故障说明](https://github.com/unitreerobotics/unitree_sdk2_python#faq)。修复时先保留完整的第一条错误及上下文，最后一行“构建失败”通常不足以定位原因。

## 遥控、关节与电池异常

遥控链路正常却无动作时，先核对模式和 SDK 控制权，不要反复发送启动或模式切换组合键。机器人持续偏移、明显抖动或关节过热时，先结束当前测试，再检查起始姿态、关节映射、多个命令来源和告警。

Unitree Explore 可查看机器状态、温度和告警，可把这些信息用于定位。[官方 App 功能说明](https://www.unitree.com/app/g1/)

电池红灯或充电异常时，记录具体灯位和闪烁方式，并对照匹配型号的说明区分温度、电压及电流保护。不要仅凭“红灯闪”判断必须更换电池，也不要继续尝试使受损电池工作。[官方电池保护说明](https://marketing.unitree.com/article/en/G1/Battery_Charger.html)

## 仿真与感知问题

模型无法加载时检查场景路径和资源文件；没有窗口时检查图形会话及渲染环境。仿真里的机器人倒下，也可能只是没有运行合适的控制器，不能直接认定 SDK 安装失败。

状态正常而图像或点云缺失时，单独核对传感器服务。图像偏色检查编码；深度尺度异常检查单位；点云整体旋转检查坐标变换；运动时重影检查时间同步。具体流程见[传感器页](hardware/sensors.md)。

## 提交可复现的问题报告

建议按以下格式准备材料，再提交给项目维护者或设备支持人员：

```text
设备：型号、机身自由度、末端和计算模块
版本：固件、系统、SDK／ROS2／仿真仓库提交号
运行位置：开发电脑或机器人；CPU 架构
连接方式：网卡、子网、DDS 域
复现步骤：最少必要命令及起始模式
预期行为：
实际行为：完整错误、时间点、频率或告警
已尝试排查：
附件：相关日志、短视频、配置（移除密码和密钥）
```

优先提供只读复现方法。涉及不可预测运动的问题，不应为了补拍视频而反复重现。
