# div[contains(class,card)][contains(string(),询单挽回or付款提醒or付款引导

> 会话元信息
> - 时间范围：2026-08-12 17:16 ~ 2026-08-12 17:16
> - 对话轮次：1 轮

---

### [用户 · 2026-08-12 17:16:04]

//div[contains(@class ,"card")][contains(string(),"询单挽回" or "付款提醒" or "付款引导" or "客户回访")]//table//tr/*[not(contains(@class ,"gutter"))]xpath表达式

### [AI · 2026-08-12 17:16:15]

这个表达式有个语法错误：`contains(string(),"询单挽回" or "付款提醒"...)` 中 `contains()` 的第二个参数必须是单个字符串，不能写 `or` 表达式。正确写法是把 `or` 提到外层，每个 `contains()` 独立判断：

```xpath
//div[contains(@class, "card")][contains(string(), "询单挽回") or contains(string(), "付款提醒") or contains(string(), "付款引导") or contains(string(), "客户回访")]//table//tr/*[not(contains(@class, "gutter"))]
```

两个补充说明：

1. **语义等价性**：修正后的表达式保持你的筛选意图不变——先定位 class 含 `card` 的 div，再匹配文本中包含任一关键词的 div，然后取其下 table 中所有 tr 内不含 `gutter` class 的单元格。
2. **潜在性能问题**：`contains(string(), ...)` 会遍历 div 的全部后代文本节点做拼接，页面较大时较慢。若关键词只出现在特定子元素（如 `.title` 或 `.text`），建议缩小范围，例如：

```xpath
//div[contains(@class, "card")][.//*[contains(@class, "title") and (contains(string(), "询单挽回") or contains(string(), "付款提醒"))]]//table//tr/*[not(contains(@class, "gutter"))]
```

如果这是用于影刀 RPA 的表达式，建议先在元素检查里验证一下 `card` 和 `gutter` 的 class 匹配是否准确，避免因空格分隔的 class 名匹配不完全导致漏选。
