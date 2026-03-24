# world.unxai.top

全球国家与大模型图谱站点。当前已经从静态展示页升级为带有国家归属、模型候选发现、验证状态分层、模型家族聚合的可扩展数据站。

## 当前能力

- 按国家展示已收录的大模型
- 支持按大洲筛选、按中文国家名搜索、按模型数量排序
- 国家详情支持按模型家族分组查看
- 区分 `已验证` 与 `待验证` 候选模型
- 支持 `只看已验证` 过滤
- 自动生成模型家族摘要

## 当前数据结构

```text
data/countries.json            # 前端主数据源
  ├─ country basic info
  ├─ verified_model_count
  ├─ pending_model_count
  ├─ family_summary
  └─ models[]

data/company_country_map.json  # 厂商 -> 国家映射
 data/model_candidates.json     # 自动发现的候选模型
 data/validation_report.json    # 验证状态统计
 data/family_summary.json       # 各国家模型家族摘要
```

## 脚本说明

- `scripts/fetch_models.py`
  - 从 OpenRouter 拉取模型候选
  - 根据映射表自动归属国家
  - 以 `verified: false` 方式并入国家数据

- `scripts/validate_models.py`
  - 统计已验证 / 待验证数量
  - 输出验证报告

- `scripts/clean_models.py`
  - 清洗候选模型展示名
  - 生成 `display_name` 与 `family`

- `scripts/aggregate_families.py`
  - 基于 `family` 生成国家级模型家族摘要

## 运行顺序

```bash
python3 scripts/fetch_models.py
python3 scripts/validate_models.py
python3 scripts/clean_models.py
python3 scripts/aggregate_families.py
```

## 当前判断

这个项目目前已经不是“静态页面样板”，而是一个可持续扩充的数据产品雏形。接下来最重要的不是继续堆功能，而是提高数据质量。

## 后续建议

1. 做更细的候选去重和版本归并
2. 补人工验证工作流，而不只是 `verified: false`
3. 增加数据更新时间自动写入页面
4. 增加来源链接和验证依据说明
5. 为重点国家做更干净的家族级汇总展示
