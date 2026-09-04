# 更新失败code1254064,msgDatetimeFieldConvFail,errormessageInvalid

> 会话元信息
> - 时间范围：2026-07-29 10:48 ~ 2026-07-29 10:48
> - 对话轮次：1 轮

---

### [用户 · 2026-07-29 10:48:14]

  更新失败: {'code': 1254064, 'msg': 'DatetimeFieldConvFail', 'error': {'message': "Invalid request parameter: 'fields.发出时间.fieldValue./.fieldName.发出时间'. Correct format : the value of 'Date' must be a unix timestamp. Please check and modify accordingly.", 'log_id': '202607291031285FA3C1D87BBC0E980A71', 'troubleshooter': '排查建议查看(Troubleshooting suggestions): https://open.feishu.cn/search?from=openapi&log_id=202607291031285FA3C1D87BBC0E980A71&code=1254064&method_id=6965347212289474562'}}这个是什么问题，我日期的格式

### [AI · 2026-07-29 10:48:24]

飞书多维表格的「发出时间」字段要求传入 **Unix 时间戳（毫秒）**，但你传的值不是时间戳格式。

常见原因：

1. **传了日期字符串**（如 `"2026-07-29"` / `"2026-07-29 10:30:00"`）——必须转成毫秒级时间戳。
2. **传了秒级时间戳**——飞书要求毫秒，少三个零。
3. **传了空字符串或非数字值**。

正确的格式类似：`"fields.发出时间": 1752211200000`

如果你用的是 Python，转换示例：

```python
import time
from datetime import datetime

# 方式一：从字符串转
dt = datetime.strptime("2026-07-29 10:31:28", "%Y-%m-%d %H:%M:%S")
timestamp_ms = int(dt.timestamp() * 1000)  # 1752210688000

# 方式二：当前时间
timestamp_ms = int(time.time() * 1000)
```
