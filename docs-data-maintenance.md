# world 数据维护说明

## 这份文档解决什么问题

这个项目的数据不是纯静态手填，而是由：

- 手工基础国家/模型数据
- OpenRouter 抓取候选模型
- 清洗与家族聚合脚本

共同组成。

这意味着：如果厂商归属规则写得不严，某个国家的数据会被大面积污染。

2026-03-28 已经修过一次中国模型归属问题。后续维护必须按这份说明做。

---

## 本次踩坑总结

之前中国页面出问题，不是前端 bug，核心是数据层污染：

1. `scripts/fetch_models.py` 对厂商识别过于粗糙
2. 只靠 `model_id` 的部分前缀识别厂商
3. 遇到不规范名字/旧数据时，很多模型被错误塞进中国/阿里云
4. 历史脏数据已经写进 `data/countries.json`，不是重新抓一次就会自动消失

最终表现为：

- OpenAI / Google / Anthropic / Microsoft / Amazon / Perplexity / Mistral / xAI 等模型混入中国
- 中国页面模型数量虚高
- 家族摘要失真
- 同名 free / 非 free 版本重复展示

---

## 当前数据文件

### 1. `data/countries.json`
主数据源。

包含：
- 国家基本信息
- `models[]`
- `model_count`
- `verified_model_count`
- `pending_model_count`
- 家族摘要相关字段

前端展示主要依赖这个文件。

### 2. `data/company_country_map.json`
厂商 -> 国家映射表。

这是最关键的数据质量控制点。

如果这里不完整：
- 模型会被错误归国
- 国家页会混入无关模型
- 后续汇总都会一起出错

### 3. `data/model_candidates.json`
抓取候选模型的中间产物。

它不是最终展示源，但它会并入 `countries.json`。

### 4. `data/validation_report.json`
已验证 / 待验证统计。

### 5. `data/family_summary.json`
按国家聚合后的模型家族摘要。

---

## 相关脚本

### `scripts/fetch_models.py`
作用：
- 从 OpenRouter 抓模型
- 推断厂商
- 根据厂商映射到国家
- 将候选模型并入 `countries.json`
- 输出 `model_candidates.json`

注意：
- 这里是第一道归属关口
- 如果厂商识别错，后面全会跟着错

### `scripts/validate_models.py`
作用：
- 统计已验证 / 待验证数量

### `scripts/clean_models.py`
作用：
- 生成 `display_name`
- 推断 `family`
- 做展示层清洗

### `scripts/aggregate_families.py`
作用：
- 根据 `family` 生成国家级摘要

---

## 正确维护顺序

每次更新模型数据，按这个顺序跑：

```bash
python3 scripts/fetch_models.py
python3 scripts/validate_models.py
python3 scripts/clean_models.py
python3 scripts/aggregate_families.py
```

如果你刚改过映射表或做过手工清理，也要重新跑一遍这四个脚本。

---

## 后续维护原则

## 1. 先补映射表，再抓数据

如果新增模型厂商出现了：

- 不要先把它硬塞进某个国家
- 先更新 `data/company_country_map.json`
- 再重跑脚本

### 原则
- 能明确归属的厂商，必须进映射表
- 不确定国别时，不要默认归中国
- 不要默认归阿里云
- 不要因为名称看着像中文能力就归中国

---

## 2. 不信任历史桶

如果某个国家页面明显异常：

- 不要只改前端
- 不要只看 `model_count`
- 先检查 `countries.json` 里模型本身是不是已经脏了

尤其是这种情况：
- 中国页突然比预期多很多
- 出现 OpenAI / Anthropic / Google / Microsoft / Mistral 之类国外厂商
- 家族统计明显不合理

这时优先怀疑：
- 厂商识别逻辑
- `company_country_map.json`
- 历史脏数据未清理

---

## 3. free / 非 free 要避免重复展示

像这类：
- `xxx`
- `xxx (free)`

如果展示名相同，默认应视为同一模型的不同供应形态。

当前处理原则：
- 同公司 + 同 family + 同 display_name
- 优先保留：
  1. `verified=true`
  2. 非 free 版本
  3. 更规范的 `source_id`

---

## 4. 手工模型优先级高于自动候选

像这些手工主模型：
- 通义千问
- 文心大模型
- 混元
- 豆包大模型
- 讯飞星火
- GLM
- DeepSeek
- DeepSeek-R1

如果自动抓取结果和手工条目冲突：
- 优先保留手工条目
- 不要让自动候选覆盖基础认知

---

## 5. 看到下面这些信号，说明又脏了

### 国家归属脏数据信号
- 中国页出现 OpenAI / Google / Anthropic / Microsoft / Amazon / Perplexity / xAI / Mistral 等
- 美国页模型数量异常少，中国页异常多
- 法国 / 加拿大 / 韩国 / 日本等国家页模型被吸走

### 展示脏数据信号
- 同名模型重复出现两次
- `family` 同时出现公司名和产品家族名，例如：
  - `阿里云`
  - `Qwen`
- 家族摘要明显不符合常识

---

## 建议的维护动作

### 小改动
只新增少量厂商：
1. 改 `data/company_country_map.json`
2. 跑四个脚本
3. 抽查中国/美国/法国页面

### 中等改动
涉及清洗规则或 family：
1. 改脚本
2. 跑四个脚本
3. 检查 `countries.json` 是否出现异常膨胀/骤减
4. 抽查重复项

### 大改动
如果再次发生国家级污染：
1. 先备份当前 `countries.json`
2. 修映射表和抓取逻辑
3. 重新分桶
4. 必要时手工剔除历史污染项
5. 再跑四个脚本

---

## 这台机器就是线上

当前机器就是线上环境。

所以在这里改数据文件后：
- 变更会直接影响线上展示
- 不要把未验证的大规模脏数据写回主文件
- 每次大改后至少抽查一次中国和美国页面数据是否合理

---

## 2026-03-28 本次修复结论

这次已经做过的修复包括：

- 修正 `fetch_models.py` 的厂商识别逻辑
- 扩充 `company_country_map.json`
- 把国外大厂从中国区清出去
- 去掉 free / 非 free 重复展示
- 清理历史污染进中国区的旧模型
- 恢复中国核心模型的正确归属

后续如无新污染，中国页应该维持在一个更合理的规模，而不是异常膨胀。

---

## 最后一句

以后看到国家页模型异常，先查数据归属，不要先怀疑前端。