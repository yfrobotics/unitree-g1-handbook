# 设备与实验记录模板

同一台 G1 在更换手部、固件、模型或相机位置后，可能需要新的配置记录。本页提供可复制的设备与实验模板，未确认字段使用 `null` 或“未核对”，避免把参考配置写成实测结果。

## 可下载模板

| 文件 | 用途 |
| --- | --- |
| [设备清单 JSON](../_static/templates/device-manifest.json) | 机身、BrainCo2、Quest 3、传感器、计算模块、版本和核对状态 |
| [实验报告 Markdown](../_static/templates/experiment-report.txt) | 前置条件、命令、数据划分、指标、失败和验证边界 |
| [演示元数据 JSON Schema](../_static/templates/episode-metadata.schema.json) | 采集会话、成功标签、动作语义和时间来源 |
| [页面写作模板](../_static/templates/page-template.txt) | 新增教程的统一骨架 |

模板复制到本地实验目录后填写，不将序列号、私有网络信息、账户或密钥提交到公开仓库。JSON Schema 描述的是随演示保存的 `metadata.json`，不是上游 `data.json` 的完整格式。

## 什么算验证完成

“资料核对”只表示阅读了固定上游代码或文档。“本地离线验证”表示命令在所列 CPU、依赖和数据上执行过。“实机验证”需要记录具体硬件、固件、场景、操作者和结果。不能因为上游视频展示了任务就填“本实验室验证通过”。

## 一次实验的交付物

```text
run-日期-任务/
  device-manifest.json
  metadata.json
  report.md
  commands.txt
  requirements.txt
  source-revisions.txt
  calibration/
  metrics/
  logs/
```

保存训练使用的数据划分、归一化统计、策略检查点、执行配置和失败片段。截图可以帮助理解现象，但不能替代原始数值与命令。数据量较大时，在报告中记录存储位置、revision 和校验值即可。

## 向手册贡献记录

先确认记录适合公开，标出能独立复现的最小步骤，再按[贡献指南](../contributing.md)提交。设备配置表见[验证记录](../hardware/validated-configurations.md)。
