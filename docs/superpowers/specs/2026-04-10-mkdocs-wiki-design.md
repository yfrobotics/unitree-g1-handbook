# MkDocs Wiki 搭建方案

## 概述

为宇树 G1 使用手册仓库搭建基于 MkDocs Material 的 Wiki，并通过 GitHub Actions 部署到 GitHub Pages。

## 网站结构

```
docs/
├── index.md                    （首页：手册简介）
├── getting-started/
│   ├── unboxing.md             （开箱与首次开机）
│   ├── remote-control.md       （遥控器使用）[占位页]
│   └── safety.md               （安全指南）[占位页]
├── networking/
│   ├── connect-to-robot.md     （SSH、IP 配置）
│   ├── connect-to-internet.md  （通过路由器访问互联网）[占位页]
├── development/
│   ├── sdk-setup.md            （下载并编译 SDK）
│   ├── hand-sdk.md             （灵巧手 SDK 与操作）[占位页]
│   ├── ros2.md                 （ROS2 集成）[占位页]
│   └── simulation.md           （Isaac Sim、Gazebo）[占位页]
├── hardware/
│   ├── specs.md                （硬件规格与组件）[占位页]
│   └── sensors.md              （传感器数据与感知）[占位页]
└── troubleshooting.md          （常见问题与故障排查）[占位页]
```

## 配置

- **主题：** 使用 Material for MkDocs，支持深色与浅色模式切换以及搜索。
- **导航：** 在 `mkdocs.yml` 中显式定义，按学习路径排序。
- **部署：** 向 `main` 分支推送时触发 GitHub Actions 工作流，部署到 GitHub Pages。

## 内容迁移

- 将现有 README 中的“入门指南 > G1 开箱”部分移至 `docs/getting-started/unboxing.md`。
- 将现有“连接机器人”部分移至 `docs/networking/connect-to-robot.md`。
- 将现有“下载并编译 SDK”部分移至 `docs/development/sdk-setup.md`。
- 更新 README.md，使其指向 Wiki 网站。
- 占位页包含简短的主题说明和“内容编写中”提示。

## 待创建文件

- `mkdocs.yml`：MkDocs 配置。
- `requirements.txt`：Python 依赖（mkdocs-material）。
- `.github/workflows/deploy-wiki.yml`：GitHub Actions 工作流。
- 上面列出的所有 `docs/**/*.md` 页面。
