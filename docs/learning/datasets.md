# 开源数据集集合

本页汇集机器人操作学习的数据入口，优先列出与 G1 相关的资源，再介绍跨机型数据和仿真基准。资源核对日期为 2026-09-13；以下是官方资料整理，尚未在本实验室完整下载、训练或复现实机效果。

2026-09-26 新增人体动作、G1 重定向数据与全身学习数据流程。选资源时先确定要学习的是视觉操作、身体运动，还是两者的配合。

## 按学习目标选择数据

| 目标 | 优先需要的数据 | 常见缺口 |
| --- | --- | --- |
| 桌面操作与 VLA 微调 | 同步的相机、语言、机器人状态与动作轨迹 | 只有视频或任务文字，缺少可执行动作标签 |
| 全身运动跟踪 | 根节点与关节参考、骨架定义、时间信息 | 人体骨架尚未映射到 G1，或参考动作不满足接触条件 |
| 语言到运动 | 与动作片段对齐的描述和运动轨迹 | 描述动作风格，却没有物体视觉与交互标签 |
| 行走与操作结合 | 任务观测、身体控制接口、手部动作及交互结果 | 固定机位操作数据不包含移动后的视角与平衡变化 |

本表是本手册的选用建议。训练集格式统一后，仍需处理机型、动作含义与任务覆盖差异。

## G1 官方数据

| 数据集 | 内容与配置 | 建议用途 |
| --- | --- | --- |
| [G1 Dex3 ToastedBread](https://huggingface.co/datasets/unitreerobotics/G1_Dex3_ToastedBread_Dataset) | 宇树发布的 G1／Dex3 操作数据，提供状态、动作及视频；也是 Unitree LeRobot 的加载示例 | 熟悉 G1 操作数据结构和离线可视化 |
| [G1 Dex1 Stack Block](https://huggingface.co/datasets/unitreerobotics/G1_Dex1_Stack_Block) | 积木堆叠任务，包含双臂、夹爪等观测与动作字段 | 研究桌面操作、双臂数据映射 |
| [G1 Dex1 Fold Towel](https://huggingface.co/datasets/unitreerobotics/G1_Dex1_Fold_Towel) | G1／Dex1 折毛巾任务 | 研究柔性物体操作与较长动作序列 |

下载入口和字段以各数据集页面为准。名称相近的数据也可能使用不同末端、相机布局和字段组织，不能默认共用一个动作转换器。

更多资源可从[宇树官方 Hugging Face 数据集目录](https://huggingface.co/unitreerobotics/datasets)查找。宇树的 [UnifoLM-VLA 项目](https://github.com/unitreerobotics/unifolm-vla)列出了积木、收纳、清洁、折毛巾等任务的数据入口；部分旧名称会重定向到带末端型号的新名称，应记录最终仓库 ID。

## 跨机型数据与仿真基准

下表的“与 G1 的关系”是本手册根据数据来源和任务作出的选用建议，不代表这些资源已适配 G1。

| 资源 | 数据内容与官方入口 | 与 G1 的关系 |
| --- | --- | --- |
| Open X-Embodiment（OXE） | [项目主页与数据入口](https://robotics-transformer-x.github.io/)；汇集多种机器人平台的真实操作轨迹 | 适合了解跨机型预训练；混合使用前需统一观测和动作语义 |
| DROID | [项目主页、可视化与快速入门](https://droid-dataset.github.io/)；基于 Franka Panda 的真实操作数据，含外部与腕部视角、状态、动作和语言信息 | 可用于研究场景多样性与迁移；Franka 动作不能直接发送到 G1 |
| BridgeData V2 | [官方项目与下载](https://rail-berkeley.github.io/bridgedata/)；提供多任务、多环境的操作轨迹及语言标注 | 适合理解 OpenVLA 等路线的数据处理；需重新适配 G1 动作和观测 |
| LIBERO | [官方仓库及演示数据下载](https://github.com/Lifelong-Robot-Learning/LIBERO#datasets)；提供语言条件操作任务与仿真演示 | 适合先复现 VLA 训练和闭环评测；成绩反映该基准表现 |
| robomimic 数据资源 | [官方数据集总览](https://robomimic.github.io/docs/datasets/overview.html)；提供操作学习的数据资源及使用说明 | 适合建立模仿学习基线；逐项确认所选数据的语言标注、机型和格式 |

OXE 是多个数据集的集合，LeRobot 是数据与训练工具体系，LIBERO 同时包含环境和基准任务。选资源时要明确需要的是训练轨迹、数据格式还是评测环境。

## 人体动作与 G1 重定向数据 {#motion-datasets}

| 资源 | 提供什么 | G1 学习时如何使用 |
| --- | --- | --- |
| [BONES-SEED](https://huggingface.co/datasets/bones-studio/seed) | 人体动作、语言描述与时间分段；提供 SOMA BVH 和 G1 MuJoCo 兼容 CSV | 可研究动作检索、语言到运动和跟踪；按 SONIC 所选配置转换参考数据 |
| [AMASS](https://amass.is.tue.mpg.de/) | 统一人体模型表示的多来源动作捕捉集合 | 可作为人体运动来源；需要兼容的人体模型处理与 G1 重定向 |
| [LAFAN1](https://github.com/ubisoft/ubisoft-laforge-animation-dataset) | BVH 动作序列及动画研究的评测代码 | 适合从较小动作库理解骨架与运动处理；原始数据不是机器人控制记录 |
| [LAFAN1 Retargeting Dataset](https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset) | 已重定向到机器人模型的 LAFAN1 数据；BeyondMimic 文档提供此入口 | 选择 G1 子集，核对机器人模型、采样率和关节排列后再转入训练器 |

BONES-SEED 数据卡列出 142,220 条动作，其中包含镜像扩增，总时长约 288 小时。这个发布集合不应当作 SONIC 论文全部训练数据的同义词，也不应把镜像版本计作独立采集示范。[数据卡](https://huggingface.co/datasets/bones-studio/seed)

这些数据通常不能直接替代 VLA 的相机—动作示范。G1 CSV 表示参考运动，不代表实机传感器记录，也不证明轨迹在自己的场景中可执行。人体数据若包含坐椅子、攀爬等动作，还需要相应支撑物与接触建模。

下载前分别查看数据和人体模型的使用条件。LAFAN1 官方仓库列出 CC BY-NC-ND 4.0；重定向版本仍需追溯原始来源与条款。[LAFAN1 原始说明](https://github.com/ubisoft/ubisoft-laforge-animation-dataset)

### 从动作库到训练样本

1. **保留来源。** 记录原始动作 ID、人物／会话、镜像关系、文件校验值和许可。
2. **检查表示。** 明确人体模型或机器人骨架、根节点、坐标轴、长度单位和旋转约定。
3. **完成重定向。** 可参考 [GMR](https://github.com/YanjieZe/GMR)，检查脚底、手腕、关节限位及身体比例；已重定向的数据也需回放。
4. **处理时间。** 保存原始帧率、目标帧率和重采样方法；改变时间尺度时需重新计算速度等派生量。
5. **转换训练格式。** 例如 SONIC 使用 motion_lib 表示，BeyondMimic 提供 CSV 到 NPZ 的处理流程；同一 CSV 不能假设被所有训练器直接读取。[SONIC 数据处理](https://nvlabs.github.io/GR00T-WholeBodyControl/user_guide/training.html) · [BeyondMimic 处理流程](https://github.com/HybridRobotics/whole_body_tracking)
6. **按来源划分。** 同一动作的重定向、裁剪和镜像版本放在同一集合，避免测试集包含训练片段的近似副本。

训练与评测路线见 [SONIC 与全身运动学习](whole-body.md)。

## 选数据前先看什么

先选择一个小任务和少量完整轨迹，确认以下内容，再决定是否下载整个集合：

| 检查项 | 需要回答的问题 |
| --- | --- |
| 机身与末端 | 单臂还是双臂？夹爪还是灵巧手？是否包含腰部或移动基座？ |
| 观测 | 哪些相机视角？是否有机器人状态？图像与状态如何同步？ |
| 动作 | 关节目标还是末端位姿？绝对量还是增量？单位、顺序和坐标系是什么？ |
| 时间 | 数据采样率、实际控制频率、延迟和动作分段如何定义？ |
| 语言 | 是完整指令、任务标签还是没有标注？语言与动作段是否对应？ |
| 质量 | 成功与失败如何标记？是否有停顿、截断、丢帧和操作者接管？ |
| 开放条件 | 数据集卡是否给出许可、下载条件和引用要求？ |

“公开可下载”并不表示每个条目具有相同许可。数据、训练代码和模型权重分别查对应说明；OXE 的组成数据也应逐项记录来源和许可。

## LeRobot 格式与 G1 数据转换

LeRobotDataset v3 使用 Parquet 存储逐帧数据、视频文件存储视觉观测，并通过元数据描述字段、轨迹边界和时间位置。文件可能包含多条轨迹，不能再假设“一条轨迹等于一个文件”。[官方格式说明](https://huggingface.co/docs/lerobot/lerobot-dataset-v3)

宇树提供 [Unitree LeRobot](https://github.com/unitreerobotics/unitree_lerobot)，覆盖数据转换、训练与部署衔接。使用时固定仓库与子模块版本，并检查所选策略支持的数据格式版本。旧教程使用的 LeRobot v2.x 与 v3 的目录布局和加载代码可能不同。

本手册建议按以下顺序准备数据：

1. 阅读数据集卡，记录仓库 ID、revision、格式版本与许可。
2. 用对应版本的官方查看器打开一条完整轨迹，确认图像、指令和动作内容。
3. 对照字段说明列出 G1 的状态与动作映射，明确左右臂、末端和单位。
4. 画出动作随时间变化的曲线，检查跳变、缺失值和图像时间对应关系。
5. 按完整轨迹及采集场景划分训练、验证与测试集，避免相邻帧跨集合泄漏。
6. 确认格式转换后仍保留轨迹边界、任务文本和必要标定信息，再开始训练。

格式转换只改变数据组织；把 Franka 的数据写成 LeRobot 格式，并不会自动解决 G1 的运动学、动作维度或视角适配。

### 采集用于 SONIC 的 VLA 数据

使用控制器潜在动作训练 VLA 时，除通用字段外，本手册建议保存：运动 token 对应的控制器检查点与观测配置、独立手部动作、观测与目标时间戳、执行状态，以及终止／接管原因。token 的维度相同不能证明两个版本具有相同语义。

SONIC 官方采集工具可同步记录机器人状态、人体遥操作姿态和图像；后续训练使用配套导出与处理流程。先检查一条完整轨迹的元数据和动作字段，再决定是否迁移格式。[官方采集说明](https://nvlabs.github.io/GR00T-WholeBodyControl/tutorials/data_collection.html)

### 数据量应如何报告

本手册建议同时报告原始轨迹数、有效时长、任务数、物体／场景覆盖、采集会话数，以及清洗后保留量。复制片段、镜像和重采样增加的是样本数量，不一定增加独立经验。先按会话预留评测数据，归一化统计只从训练划分计算；优先补采反复失败的条件，再判断是否需要扩大数据规模。

## 自采数据应该记录什么

使用 [xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate)等工具采集 G1 演示时，建议将以下信息与数据一起保存：

```text
数据集名称、版本、采集日期与负责人
机身自由度、左右末端、额外载荷
固件、SDK、采集程序提交号
相机型号、视角、内外参、分辨率
状态字段、动作字段、单位、坐标系、关节顺序
采样率、控制频率、时间戳来源、同步方式
任务指令、初始条件、结束条件、成功与失败标签
操作者接管、异常、数据清洗与裁剪记录
训练／验证／测试划分和归一化统计来源
数据许可、原始来源与引用
```

初次采集可先做单个桌面任务，覆盖不同物体位置，并保留失败原因和停止记录。传感器同步见[传感器与感知](../hardware/sensors.md)，训练与部署路线继续阅读 [VLA](vla.md)。
