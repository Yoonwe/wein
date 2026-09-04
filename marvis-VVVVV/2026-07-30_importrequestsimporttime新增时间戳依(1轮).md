# importrequestsimporttime新增时间戳依

> 会话元信息
> - 时间范围：2026-07-30 09:03 ~ 2026-07-30 09:03
> - 对话轮次：1 轮

---

### [用户 · 2026-07-30 09:03:01]

import requests
import time  # 新增时间戳依赖


# ===================== 配置 =====================
APP_ID = "cli_a729a2469afed00c"
APP_SECRET = "cPVQMyS7***REDACTED***"
BITABLE_APP_TOKEN = "FZgjbdV1Qa4rl3sr4GTcmbl4nhf"
TABLE_ID = "tbl4FpAG1a5Av0kJ"


# ===================== 自动获取飞书 TOKEN =====================
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    result = res.json()
    return result.get("tenant_access_token", "")


# ===================== 【关键修复】时间自动转时间戳 =====================
# 你原来的运行开始时间（字符串格式）
run_time_str = 运行开始时间


# 转换成飞书必须的 毫秒级时间戳
try:
    # 尝试转换成时间戳（兼容影刀输出）
    time_array = time.strptime(run_time_str, "%Y-%m-%d %H:%M:%S")
    run_stamp = int(time.mktime(time_array)) * 1000  # 飞书需要毫秒
except:
    run_stamp = int(time.time() * 1000)  # 失败就用当前时间


# ===================== 数据 =====================
data = {
    "应用名称": 应用名称,
    "账号名称": 账号名称,
    "应用UUID": 应用UUID,
    "运行开始时间": run_stamp,  # 这里传时间戳，不再传字符串
    "运行结束时间": "",
    "运行方式": 触发类型,
    "运行状态": 运行状态
}


# ===================== 核心：创建/更新 =====================
def write_feishu(data, status, action, record_id=None):
    if status == "运行中" and "运行结束时间" in data:
        del data["运行结束时间"]
    data["运行状态"] = status


    token = get_feishu_token()
    if not token:
        return {}


    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"fields": data}


    if action == "create":
        response = requests.post(url, headers=headers, json=payload)
    elif action == "update" and record_id:
        response = requests.put(f"{url}/{record_id}", headers=headers, json=payload)
    else:
        return {}


    result = response.json()
    print("📤 飞书返回:", result)
    return result


# ===================== 执行创建 =====================
result = write_feishu(data, 运行状态, "create")


try:
    影刀记录表ID = result["data"]["record"]["record_id"]
    print("✅ 飞书记录ID：", 影刀记录表ID)
except Exception as e:
    print("❌ 获取ID失败:", e)报错 HTTPSConnectionPool(host='open.feishu.cn', port=443): Max retries exceeded with url: /open-apis/auth/v3/tenant_access_token/internal (Caused by ProxyError('Unable to connect to proxy', OSError(0, 'Error')))

### [AI · 2026-07-30 09:03:10]

飞书请求报的是代理错误。当前系统代理拦截了 `open.feishu.cn` 的请求。在调用飞书 API 前先关闭代理：

在 `get_feishu_token` 和 `write_feishu` 中的 `requests.post` / `requests.put` 加上 `proxies={"http": None, "https": None}`：

```python
# 在文件顶部新增一个禁止代理的配置
NO_PROXY = {"http": None, "https": None}
```

然后将所有 `requests.post(...)` 和 `requests.put(...)` 都加上 `proxies=NO_PROXY`：

```python
# get_feishu_token 中
res = requests.post(url, json={...}, proxies=NO_PROXY)

# write_feishu 中
response = requests.post(url, headers=headers, json=payload, proxies=NO_PROXY)
response = requests.put(f"{url}/{record_id}", headers=headers, json=payload, proxies=NO_PROXY)
```

如果影刀环境支持，更彻底的方式是在脚本最前面加：

```python
import os
os.environ["NO_PROXY"] = "open.feishu.cn"
```

需要我直接帮你改好的完整代码，还是你自己改？
