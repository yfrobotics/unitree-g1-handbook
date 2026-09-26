# 参与完善

请阅读[贡献指南](docs/contributing.md)与[实验记录模板](docs/maintenance/records.md)。新增教程需注明配置、执行主机、固定版本、预期结果、来源和实际验证范围。

提交前在文档环境执行：

```bash
mkdocs build --strict
python scripts/check_seo.py
python -m unittest discover -s examples/tests -v
git diff --check
```
