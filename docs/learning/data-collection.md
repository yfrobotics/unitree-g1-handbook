# 采集、检查与转换一条演示

本页把 G1 EDU 29-DoF、BrainCo2 双手和原装单 RGB 相机的遥操作输出转换为可检查的数据。先完成[Quest 3 遥操作](../development/teleoperation.md)。本页的离线检查工具不连接机器人，不会回放控制命令。

## 定义第一条任务

先录制空载伸手和回位：从固定起始姿态，将左手移动到桌面标记上方再返回。记录标记位置、动作范围和结束条件。首次验收只要求整条轨迹完整、图像可解码、左右映射与数据一致；它不代表已经收集到抓取训练数据。

按 `s` 开始/结束录制后等待保存完成，得到类似目录：

```text
g1_raw/
  reach_open_hand/
    episode_0000/
      data.json
      colors/
      depths/
      audios/
```

文件夹编号以实际输出为准。`data.json` 包含 `info`、`text`、`data`；帧内有 `idx`、`colors`、`states`、`actions` 等字段。[上游写入器](https://github.com/unitreerobotics/xr_teleoperate/blob/817fb00c63cde15e5f24a0f8fa08e1e33ed89d3b/teleop/utils/episode_writer.py)采用异步保存，不在写入未完成时复制或转换。

## 先检查完整性

在本手册仓库根目录使用 Python 3.10 或更新版本：

```bash
python3 examples/inspect_episode.py \
  ~/datasets/g1_raw/reach_open_hand/episode_0000/data.json \
  --csv /tmp/g1-episode-0000.csv
```

工具检查帧索引、有限数值、维度一致、每帧相机键与图像路径存在，并输出状态/动作 CSV。默认依次检查左臂、右臂、左手、右手。预期各侧维度为 `7,7,6,6`；单 RGB 图像键为 `color_0`。缺文件、NaN、帧断号或维度变化会报错；CSV 已存在时拒绝覆盖。

图像存在并不证明可解码或与动作同步。用对应版本的查看器检查整条演示，再画状态与目标曲线。离线检视不使用 `replay_robot.py`，后者属于执行流程。

## 时间与标签不能从帧号猜测

固定版本写入器记录帧索引及配置帧率，但没有为每帧提供完整的相机采样、状态采样、命令发送时间。因此检查工具明确报告 `timing: NOT_VERIFIED`。用 `idx / 30` 只能构造名义时间轴，无法证明真实 30 Hz 或跨传感器同步。

正式采集应扩展记录以保存各来源时间戳、接收端单调时钟、丢帧计数和控制器版本。参考[实验清单模板](../maintenance/records.md)，至少为每条演示补充成功/失败、接管、停止原因和采集会话；不要用剪掉失败片段来伪造成功标签。

## 配置 26 维动作与单相机

| 索引 | 内容 | 单位 |
| --- | --- | --- |
| 0—6 | 左臂：肩 pitch/roll/yaw、肘、腕 roll/pitch/yaw | rad |
| 7—13 | 右臂，同序 | rad |
| 14—19 | 左手：拇指、拇指辅助、食指、中指、无名指、小指 | `[0,1]` |
| 20—25 | 右手，同序 | `[0,1]` |

这里是**学习数据的拼接顺序**，不是机身 DDS 槽位。[上游 BrainCo 配置](https://github.com/unitreerobotics/unitree_lerobot/blob/41c2805742de879ddab2d8d6beaeaf215f876395/unitree_lerobot/utils/constants.py)使用相同动作分组，但预设左右头部和左右腕部四路相机。本手册的 `convert_brainco2.py` 注册 `G1_29_BrainCo2_RGB`，仅保留 `color_0 → observation.images.cam_head`，不为缺失相机复制或补黑图。

## 安装固定转换环境

在训练电脑安装，和遥操作环境分开：

```bash
git clone https://github.com/unitreerobotics/unitree_lerobot.git ~/unitree_lerobot_lab
cd ~/unitree_lerobot_lab
git checkout --detach 41c2805742de879ddab2d8d6beaeaf215f876395
git submodule update --init --recursive
conda create -n g1-data python=3.10
conda activate g1-data
conda install -c conda-forge pinocchio ffmpeg=7.1.1
python -m pip install -e ./unitree_lerobot/lerobot
python -m pip install -e .
git submodule status
```

此提交的 LeRobot 子模块位于 `unitree_lerobot/lerobot`，实际提交为 `a5b29d430105f5235eb05bbf2db5a0d747a869d6`；以 gitlink 为准，不以 README 中的旧提交提示为准。[固定转换源码](https://github.com/unitreerobotics/unitree_lerobot/blob/41c2805742de879ddab2d8d6beaeaf215f876395/unitree_lerobot/utils/convert_unitree_json_to_lerobot.py)默认 30 fps。不同采样率必须先确认重采样规则并修改对应实现，不能仅改元数据。

## 本地转换

保留原始录制，整理副本为“根目录/任务/episode”两级布局。选择一个未使用的本地数据集名称：

```bash
cd ~/unitree-g1-handbook
python examples/convert_brainco2.py \
  --raw-dir ~/datasets/g1_raw \
  --repo-id local/g1_brainco2_rgb_run01
```

包装器要求 30 fps 名义配置、单路 `color_0`、可解码的 640×480 RGB 图像、7+7+6+6 维状态与动作，并检查手部归一化范围。发现目标数据集已存在会拒绝转换，因为上游创建函数原本会删除同名输出。它调用上游创建/填充函数后显式 `finalize()` 写完 v3 文件，仅写入本地缓存，不调用上传接口。元数据 sidecar 保存在原始录制树之外，转换目录只放任务与 episode。

先只检查输入时，在上述命令末尾加 `--check-only`，无需加载 LeRobot。仓库的 `examples/data/synthetic` 提供三帧合成格式样例，可用于工具自检；它没有真实图像或机器人示范，不用于训练。

得到输出路径后，核对 `meta/info.json` 的字段维度、视频键、格式版本和 episode 数，并用相同 LeRobot 版本的查看器打开：

```bash
python ~/unitree_lerobot_lab/unitree_lerobot/lerobot/src/lerobot/scripts/lerobot_dataset_viz.py \
  --repo-id local/g1_brainco2_rgb_run01 --episode-index 0
```

转换保留原始数据语义的责任仍在采集者：确认动作是控制目标而非下一帧测量值、检查颜色编码和左右顺序，保留标定文件与会话清单。此转换器已核对接口及静态检查，但尚未使用本实验室真实录制跑通；完成后将记录补入[验证表](../hardware/validated-configurations.md)。

继续阅读：[第一个学习实验](first-policy.md) · [数据集格式与划分](datasets.md)
