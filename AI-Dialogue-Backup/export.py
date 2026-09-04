# -*- coding: utf-8 -*-
"""
AI 对话记录导出器
按统一规范将 AI 助手本地 SQLite 聊天记录导出为 Markdown 沉淀文件：
  目录名: <AiName>-<HostName>
  文件名: <开始日期>_<主要主题>(<对话轮次>).md
内置敏感凭据打码，供推送 GitHub 前脱敏。
用法:
  python export.py --db <sqlite路径> --out <输出根目录> --name <marvis-VVVVV>
"""
import argparse
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

UTC8 = timezone(timedelta(hours=8))

# ---------- 敏感凭据打码 ----------
# 固定已知凭据（按需追加，值为曾经明文出现过的真实 secret）
FIXED_SECRETS = [
    "cPVQMyS75d61KRcpNMxXygaBxhMv4gsH",
    "PAitb54Juasknxs80xjcL7fWnEs",
    "SYTXbct3uasLcSsfVD0cMgP0nVh",
    "sk-ai-v1-191e4cd1707ada8c4c2d6be224ef68d483aed1c9deca18e9429",
    "8bb40c9d447d25b94ba28ef97e6ccbcc822d36e2a67ac8e38d3fce9e9538",
]
# 通用模式：GitHub PAT / ghp / sk- / AKIA / JWT / PEM 私钥 / 常见 key=value 赋值
PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|app[_-]?secret|client[_-]?secret|password|passwd|secret|access[_-]?token)\s*[:=]\s*[\"']?([A-Za-z0-9_\-\./+]{16,})"),
]

def redact(text: str) -> str:
    for s in FIXED_SECRETS:
        text = text.replace(s, s[:8] + "***REDACTED***")
    for p in PATTERNS:
        text = p.sub(lambda m: (m.group(0)[:8] + "***REDACTED***") if len(m.group(0)) > 12 else m.group(0), text)
    return text


# ---------- 工具 ----------
def detect_columns(cursor, table):
    """探测表列名，返回按语义归类的列。"""
    cols = [r[1] for r in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
    lower = {c.lower(): c for c in cols}
    def pick(*keys):
        for k in keys:
            if k in lower:
                return lower[k]
        return None
    return {
        "cols": cols,
        "id": pick("id", "conversation_id", "chat_id", "session_id"),
        "title": pick("title", "name", "summary"),
        "created": pick("created_at", "create_time", "created", "start_time", "timestamp", "time"),
        "conversation": pick("conversation_id", "chat_id", "session_id", "conv_id"),
        "role": pick("role", "sender_type", "sender", "author"),
        "content": pick("content", "text", "message", "body", "payload"),
    }

def parse_time(v):
    """兼容 int/float/str 的时间表示，返回 UTC+8 datetime 或 None。"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        ts = float(v)
        if ts > 1e12:  # 毫秒
            ts /= 1000.0
        if ts > 1e15:  # 微秒
            ts /= 1e6
        try:
            return datetime.fromtimestamp(ts, UTC8)
        except Exception:
            return None
    s = str(v)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:26], fmt).replace(tzinfo=UTC8)
        except Exception:
            continue
    return None

def clean_title(title, fallback):
    """取会话主题用于文件名：清理非法文件字符、压缩空白、截断 60 字、去尾部标点。"""
    t = (title or fallback or "未命名").strip()
    t = re.sub(r"\s+", "", t)
    t = re.sub(r'[\\/:*?"<>|#%&\{\}\$!@`\']', "", t)
    t = re.sub(r"[。，,.\s_\-]+$", "", t)
    if not t:
        t = "未命名"
    return t[:60]

def safe_filename(day, topic, turns):
    return f"{day}_{topic}({turns}轮).md"


# ---------- 导出 ----------
def export(db_path, out_root, folder_name):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cc = detect_columns(cur, "conversations")
    mc = detect_columns(cur, "messages")
    if not (cc["id"] and cc["created"] and mc["conversation"] and mc["role"] and mc["content"]):
        raise RuntimeError(f"表结构无法识别: conv_cols={cc} msg_cols={mc}")

    convs = cur.execute(
        f"SELECT {cc['id']}, {cc['title'] or 'NULL'}, {cc['created']} FROM conversations"
    ).fetchall()

    out_dir = os.path.join(out_root, folder_name)
    os.makedirs(out_dir, exist_ok=True)

    written = 0
    used_names = set()  # 本次批次内已生成文件名，用于同日同名去重
    for cid, title, created in convs:
        if cid is None:
            continue
        # 取首条用户消息做兜底主题；按用户消息数计轮次
        rows = cur.execute(
            f"SELECT {mc['role']}, {mc['content']}, {mc['created']} FROM messages "
            f"WHERE {mc['conversation']}=? ORDER BY rowid",
            (cid,),
        ).fetchall()
        user_msgs = [r for r in rows if str(r[0]).lower() in ("user", "human", "用户", "0")]
        if not user_msgs:
            continue
        first_dt = parse_time(user_msgs[0][2]) or parse_time(created)
        if first_dt is None:
            continue
        topic = clean_title(title, user_msgs[0][1])
        day = first_dt.strftime("%Y-%m-%d")
        turns = len(user_msgs)

        body = []
        body.append(f"# {topic}\n")
        times = [parse_time(r[2]) for r in rows]
        times = [t for t in times if t]
        if times:
            body.append("> 会话元信息")
            body.append(f"> - 时间范围：{min(times).strftime('%Y-%m-%d %H:%M')} ~ {max(times).strftime('%Y-%m-%d %H:%M')}")
            body.append(f"> - 对话轮次：{turns} 轮")
        body.append("")
        body.append("---")
        body.append("")
        for role, content, ts in rows:
            r = str(role).lower()
            if r not in ("user", "assistant", "human", "ai", "bot", "用户", "助手"):
                continue
            speaker = "用户" if r in ("user", "human", "用户") else "AI"
            tstr = parse_time(ts).strftime("%Y-%m-%d %H:%M:%S") if parse_time(ts) else ""
            c = redact(str(content or ""))
            body.append(f"### [{speaker} · {tstr}]")
            body.append("")
            body.append(c)
            body.append("")

        fn = safe_filename(day, topic, turns)
        # 同批次同名自动去重：追加 -2/-3 序号
        if fn in used_names:
            base = fn[:-3]  # 去掉 .md
            idx = 2
            while f"{base}-{idx}.md" in used_names:
                idx += 1
            fn = f"{base}-{idx}.md"
        used_names.add(fn)
        with open(os.path.join(out_dir, fn), "w", encoding="utf-8") as f:
            f.write("\n".join(body))
        written += 1

    con.close()
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True, help="目录名，如 marvis-VVVVV")
    a = ap.parse_args()
    n = export(a.db, a.out, a.name)
    print(f"EXPORT_OK files={n} dir={os.path.join(a.out, a.name)}")
