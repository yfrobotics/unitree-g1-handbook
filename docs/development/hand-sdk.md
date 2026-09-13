# 灵巧手 SDK 与操作

先确认末端执行器的具体型号。本页围绕宇树 Dex3 三指灵巧手说明开发流程；其他品牌的五指手、夹爪或固定假手需要使用各自的驱动和配置。

## 确认硬件与接口

检查交付清单和实物，记录左右手型号、固件、连接方式、是否安装触觉传感器。手指关节和手腕关节是不同的控制对象，不能仅凭机身“29 自由度”等标记推断手部配置。

宇树 C++ SDK 提供 [`example/g1/dex3`](https://github.com/unitreerobotics/unitree_sdk2/tree/main/example/g1/dex3)。它使用 `HandCmd` 发送手部电机命令，使用 `HandState` 接收状态。状态消息包含电机、压力传感器、供电和错误字段；字段存在不意味着对应传感器一定已安装或已发布有效值。[HandState 定义](https://github.com/unitreerobotics/unitree_ros2/blob/master/cyclonedds_ws/src/unitree/unitree_hg/msg/HandState.msg)

## 先读源码，再运行示例

完成 [SDK 编译](sdk-setup.md)后，在仓库中查看：

```bash
cd ~/unitree_sdk2
less example/g1/dex3/g1_dex3_example.cpp
```

核对时的官方示例在初始化后自动进入 `ROTATE` 状态并发送运动命令。因此，**它不能当作只读连接测试运行**。代码还区分左右手关节范围；不要把一侧的目标角度直接复制给另一侧。[示例源码](https://github.com/unitreerobotics/unitree_sdk2/blob/main/example/g1/dex3/g1_dex3_example.cpp)

## 先建立状态订阅

使用 [ROS2 环境](ros2.md)时，可以先列出已有话题：

```bash
ros2 topic list -t
```

以下名称来自核对时的 SDK 示例，DDS 名称和 ROS2 显示名称应分别检查：

| 用途 | 示例中的 DDS 名称 |
| --- | --- |
| 左手控制 | `rt/dex3/left/cmd` |
| 右手控制 | `rt/dex3/right/cmd` |
| 左手低频状态 | `rt/lf/dex3/left/state` |
| 右手低频状态 | `rt/lf/dex3/right/state` |

该版本在选择左右手后订阅低频状态，具体实现见[示例初始化代码](https://github.com/unitreerobotics/unitree_sdk2/blob/main/example/g1/dex3/g1_dex3_example.cpp)。如果 ROS2 实际列出了 `/lf/dex3/left/state`，可只读检查：

```bash
ros2 topic info /lf/dex3/left/state --verbose
ros2 topic echo /lf/dex3/left/state --once --qos-reliability best_effort
```

若设备发布的是其他名称或只有普通频率状态，使用实际列表中的名称。不要因为收不到某个预设话题就直接更改手部固件。

## 从单关节到抓取

以下为本手册建议的调试顺序，具体限位、增益和速度采用匹配型号的官方配置：

1. 在机身和手臂稳定、手部周围无障碍物的条件下读取左右手状态。
2. 对照模型确认关节编号、正方向、角度单位以及有效范围。
3. 在仿真中从当前关节角开始生成连续目标，验证单关节的小幅运动。
4. 实机测试时逐步验证单指、多指空载开合，并记录命令与反馈。
5. 选择轻、软、易释放的物体测试抓取，再加入手臂移动。

不要以自己的手指测试夹持力。左右手均需单独确认限位和方向；也不要用提高增益来补偿接线、关节映射或通信错误。

## 与手臂协同

一次抓取通常分为：确定目标位姿、规划手臂接近、对齐手掌、闭合手指、确认接触、抬起和释放。手部 SDK 只解决其中部分执行接口，不能代替视觉定位、逆运动学、碰撞检查和机身平衡控制。

建议将目标位姿、手指目标、实际关节反馈和图像时间戳一起记录。出现物体滑落时，先判断定位误差、接触姿态、目标范围还是控制延迟，再调整抓取策略。

需要手臂和末端的遥操作或数据采集，可进一步参考宇树 [`xr_teleoperate`](https://github.com/unitreerobotics/xr_teleoperate)及其支持的具体配置。先在[仿真环境](simulation.md)验证，遇到无状态、单侧无响应或温度异常时参阅[故障排查](../troubleshooting.md)。
