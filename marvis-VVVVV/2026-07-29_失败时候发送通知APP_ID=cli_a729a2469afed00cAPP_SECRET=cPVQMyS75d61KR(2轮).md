# 失败时候发送通知APP_ID=cli_a729a2469afed00cAPP_SECRET=cPVQMyS75d61KR

> 会话元信息
> - 时间范围：2026-07-29 15:27 ~ 2026-07-29 15:30
> - 对话轮次：2 轮

---

### [用户 · 2026-07-29 15:27:00]

失败时候发送通知APP_ID = "cli_a729a2469afed00c"
APP_SECRET = "cPVQMyS7***REDACTED***"
GROUP_NAME = "万威, 黄俊文, 肖晓雯"  # 目标群聊名称
MESSAGE = 报错的内容  。参考："""飞书通知模块
通过飞书开放平台 API 向指定群聊发送文本消息。


使用流程：
1. 用 app_id + app_secret 获取 tenant_access_token
2. 根据群名称模糊搜索获取群 chat_id
3. 发送文本消息到该群
"""


import requests
import json



def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取 token 失败: {data.get('msg', '')}")
    return data["tenant_access_token"]



def search_chat_id(token: str, group_name: str) -> str:
    """根据群名称搜索群聊，返回第一个匹配的 chat_id"""
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    params = {"page_size": 20}
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"搜索群聊失败: {data.get('msg', '')}")
    items = data.get("data", {}).get("items", [])
    for chat in items:
        if chat.get("name") and group_name in chat["name"]:
            return chat["chat_id"]
    raise Exception(f"未找到包含关键词 '{group_name}' 的群聊")



def send_text_message(token: str, chat_id: str, text: str) -> dict:
    """向指定群聊发送文本消息"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}),
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"发送消息失败: {data.get('msg', '')}")
    return data



def notify_group(app_id: str, app_secret: str, group_name: str, message: str):
    """向指定群聊发送通知——供外部调用的入口函数"""
    token = get_tenant_access_token(app_id, app_secret)
    chat_id = search_chat_id(token, group_name)
    result = send_text_message(token, chat_id, message)
    print(f"[✓] 已向群聊「{group_name}」发送消息: {message}")
    return result



def notify_groups(app_id: str, app_secret: str, group_names: list[str], message: str):
    """向多个群聊发送通知"""
    token = get_tenant_access_token(app_id, app_secret)
    for name in group_names:
        try:
            chat_id = search_chat_id(token, name)
            send_text_message(token, chat_id, message)
            print(f"[✓] 已向群聊「{name}」发送消息: {message}")
        except Exception as e:
            print(f"[✗] 向群聊「{name}」发送失败: {e}")

### [AI · 2026-07-29 15:27:04]

让我先看看这个脚本的内容。

### [AI · 2026-07-29 15:27:26]

我来看看脚本内容，然后整合失败通知功能。

### [AI · 2026-07-29 15:27:35]

好，第一步完成。现在在工具函数区域添加通知函数。我用 `_ensure_pkg` 函数后面作为插入点。

### [AI · 2026-07-29 15:27:45]

现在修改 `main()` 函数，加上异常捕获和通知逻辑：

### [AI · 2026-07-29 15:27:48]

验证一下文件结尾是否正确：

### [AI · 2026-07-29 15:27:51]

文件结构完整。再确认一下通知函数区域的完整性：

### [AI · 2026-07-29 15:27:59]

改完了，三处改动：

1. **配置区** — 添加 `NOTIFY_GROUP_NAME = "万威, 黄俊文, 肖晓雯"`
2. **工具函数区** — 添加 `search_chat_id()`、`send_text_message()`、`notify_failure()`（复用脚本已有的 `get_feishu_token()`，不重复鉴权）
3. **入口** — `main()` 外层包 try-except，捕获异常后调 `notify_failure()` 发飞书通知

通知消息格式为 `【物流回填脚本异常】\n<完整异常堆栈>`，发送失败时不会影响脚本原有流程，只在控制台打印一条通知失败提示。

```<yyb-product>
[update_dispatch_time.py](<C:\Users\EDY\Desktop\update_dispatch_time.py>)
```

### [用户 · 2026-07-29 15:30:05]

成功后通知APP_ID = "cli_a729a2469afed00c"
APP_SECRET = "cPVQMyS7***REDACTED***"
MESSAGE_ID = "om_x100b553b7f9284b4c3f790e4b13825a"
REPLY_TEXT = "物流状态更新运行完成(这里补充当前日期加上时分秒)"参考"""飞书回复消息模块
通过飞书开放平台 API 回复指定消息。


使用流程：
1. 用 app_id + app_secret 获取 tenant_access_token
2. 调用 reply API 回复消息
"""


import requests
import json



def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取 token 失败: {data.get('msg', '')}")
    return data["tenant_access_token"]



def reply_message(app_id: str, app_secret: str, message_id: str, text: str) -> dict:
    """回复飞书消息"""
    token = get_tenant_access_token(app_id, app_secret)
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "msg_type": "text",
        "content": json.dumps({"text": text}),
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"回复消息失败: {data.get('msg', '')}")
    print(f"[✓] 已回复消息 {message_id}: {text}")
    return data

### [AI · 2026-07-29 15:30:19]

老板这次要求加"成功后通知"——脚本运行成功后，回复一条飞书消息（不是发到群，是回复指定消息）。给出了：
- APP_ID / APP_SECRET（和之前一样）
- MESSAGE_ID = "om_x100b553b7f9284b4c3f790e4b13825a"
- REPLY_TEXT = "物流状态更新运行完成(这里补充当前日期加上时分秒)"

参考代码是飞书回复消息模块（reply_message API，通过 /im/v1/messages/{message_id}/reply 回复）。

需要把成功通知也集成到 update_dispatch_time.py 中。具体来说：
1. 添加 MESSAGE_ID 配置
2. 添加 reply_message 函数
3. 在 main() 执行完成后（try 分支中），调用 reply_message 回复成功通知，带当前日期时间

注意 REPLAY_TEXT 里说"这里补充当前日期加上时分秒"，所以我需要在运行时动态生成带当前时间的内容。

设计：
1. 配置区添加 NOTIFY_MESSAGE_ID = "om_x100b553b7f9284b4c3f790e4b13825a"
2. 在 notify_failure 附近或之后添加 reply_message 函数（复用 get_feishu_token）
3. 在 main() 的 try 分支中，main() 返回后调用 reply_message 发送成功通知

目前入口是：
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        ...
        notify_failure(error_detail)
```

要改造成：
```python
if __name__ == "__main__":
    try:
        main()
        # 成功后通知
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reply_text = f"物流状态更新运行完成{now_str}"
        reply_message(FEISHU_APP_ID, FEISHU_APP_SECRET, NOTIFY_MESSAGE_ID, reply_text)
    except Exception as e:
        ...
        notify_failure(error_detail)
```

但是 reply_message 函数里会再调一次 get_feishu_token，其实可以复用 token。不过为了简单，直接用新写的 reply_message 函数就行，它也调 get_feishu_token。

等等，我看看脚本里已有的函数签名。`get_feishu_token()` 无参，使用脚本顶部的 FEISHU_APP_ID/FEISHU_APP_SECRET。而 reply_message 函数接受 app_id, app_secret, message_id, text。为了复用，可以让 reply_message 直接调用 get_feishu_token()。

或者我直接写一个简单版本：

```python
def reply_success():
    """运行成功后回复消息"""
    try:
        token = get_feishu_token()
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = f"物流状态更新运行完成{now_str}"
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{NOTIFY_MESSAGE_ID}/reply"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"msg_type": "text", "content": json.dumps({"text": text})}
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"回复消息失败: {data.get('msg', '')}")
        print(f"[通知] 已回复消息: {text}")
    except Exception as e:
        print(f"[通知失败] 回复消息时出错: {e}")
```

这样可以复用已有的 get_feishu_token()。

然后在入口处调用。

让我用 edit_file 操作。

两步：
1. 添加 NOTIFY_MESSAGE_ID 配置
2. 添加 reply_success 函数
3. 修改入口的 try 分支

第一步：配置区添加 NOTIFY_MESSAGE_ID。在 NOTIFY_GROUP_NAME 后面添加。

第二步：在 notify_failure 函数后面添加 reply_success 函数。

第三步：修改入口。

开始操作。

### [AI · 2026-07-29 15:30:26]

现在在 notify_failure 后面添加 reply_success 函数。

### [AI · 2026-07-29 15:30:37]

最后在入口的 try 分支中 main() 之后添加 `reply_success()`：

### [AI · 2026-07-29 15:30:43]

验证一下入口和通知函数位置：

### [AI · 2026-07-29 15:30:54]

加好了，两处改动：

1. **配置区** — 添加 `NOTIFY_MESSAGE_ID = "om_x100b553b7f9284b4c3f790e4b13825a"`
2. **工具函数区** — 添加 `reply_success()`，复用 `get_feishu_token()`，回复内容动态拼接当前日期时间（格式如 `物流状态更新运行完成2026-07-29 16:00:00`）
3. **入口** — `main()` 成功后调 `reply_success()`，成功后调 `reply_success()` 也抛异常会自动走失败通知兜底

现在脚本运行流程：
- **成功** → `main()` → `reply_success()` → 回复消息"物流状态更新运行完成{当前时间}"
- **失败** → 捕获异常 → `notify_failure()` → 发群聊通知
