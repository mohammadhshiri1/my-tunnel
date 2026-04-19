#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
پروکسی بیلدر شخصی‌سازی شده - خواندن تنظیمات از settings.json و ساخت کانفیگ بر اساس IPهای تمیز وارد شده توسط کاربر
"""

import os
import json
import base64
import urllib.request
import shutil
from datetime import datetime

# ======================== خواندن تنظیمات سفارشی ========================
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "uuid": "b3e5e5b8-0e1d-4f8a-8e5c-6f2e5a1b9c8d",
    "ips": ["104.18.0.0:443", "104.16.0.0:443"],
    "sni": "www.microsoft.com",
    "security": "tls",
    "network": "tcp",
    "port": "443"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS

settings = load_settings()
UUID = settings.get("uuid", DEFAULT_SETTINGS["uuid"])
IPS = settings.get("ips", DEFAULT_SETTINGS["ips"])
SNI = settings.get("sni", DEFAULT_SETTINGS["sni"])
SECURITY = settings.get("security", DEFAULT_SETTINGS["security"])
NETWORK = settings.get("network", DEFAULT_SETTINGS["network"])
PORT = settings.get("port", DEFAULT_SETTINGS["port"])

# ======================== پوشه‌های خروجی ========================
WORK_DIR = "public"
CONFIG_DIR = "configs"
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# ======================== تولید کانفیگ با IPهای وارد شده ========================
def generate_configs():
    vless_list = []
    vmess_list = []
    trojan_list = []

    for ip in IPS:
        addr = ip.split(":")[0]
        port = ip.split(":")[1] if ":" in ip else PORT

        # کانفیگ VLESS
        if SECURITY == "tls":
            vless = f"vless://{UUID}@{addr}:{port}?encryption=none&security=tls&sni={SNI}&type={NETWORK}#Custom-{addr}"
        elif SECURITY == "reality":
            vless = f"vless://{UUID}@{addr}:{port}?encryption=none&security=reality&sni={SNI}&pbk=...&sid=...&type={NETWORK}#Custom-{addr}"
        else:
            vless = f"vless://{UUID}@{addr}:{port}?encryption=none&security=none&type={NETWORK}#Custom-{addr}"
        vless_list.append(vless)

        # کانفیگ Trojan
        trojan = f"trojan://{UUID}@{addr}:{port}?security={SECURITY}&sni={SNI}#Custom-{addr}"
        trojan_list.append(trojan)

        # کانفیگ VMESS
        vmess_obj = {
            "v": "2",
            "ps": f"Custom-{addr}",
            "add": addr,
            "port": port,
            "id": UUID,
            "aid": "0",
            "net": NETWORK,
            "type": "none",
            "host": SNI,
            "path": "/",
            "tls": SECURITY if SECURITY != "none" else ""
        }
        vmess = "vmess://" + base64.b64encode(json.dumps(vmess_obj).encode()).decode()
        vmess_list.append(vmess)

    # ذخیره فایل‌ها
    with open(f"{CONFIG_DIR}/vless.txt", "w") as f:
        f.write("\n".join(vless_list))
    with open(f"{CONFIG_DIR}/vmess.txt", "w") as f:
        f.write("\n".join(vmess_list))
    with open(f"{CONFIG_DIR}/trojan.txt", "w") as f:
        f.write("\n".join(trojan_list))

    all_configs = vless_list + vmess_list + trojan_list
    sub_b64 = base64.b64encode("\n".join(all_configs).encode()).decode()
    with open(f"{CONFIG_DIR}/subscription.txt", "w") as f:
        f.write(sub_b64)

    # کپی به ریشه
    shutil.copy(f"{CONFIG_DIR}/subscription.txt", "subscription.txt")
    shutil.copy(f"{CONFIG_DIR}/vless.txt", "vless.txt")
    shutil.copy(f"{CONFIG_DIR}/vmess.txt", "vmess.txt")
    shutil.copy(f"{CONFIG_DIR}/trojan.txt", "trojan.txt")

    return {"vless": vless_list, "vmess": vmess_list, "trojan": trojan_list}

# ======================== ساخت پنل HTML استاتیک (اختیاری) ========================
def build_static_panel():
    ip_rows = ""
    for ip in IPS:
        addr = ip.split(":")[0]
        port = ip.split(":")[1] if ":" in ip else PORT
        ip_rows += f"<tr><td>{addr}</td><td>{port}</td><td>✅ فعال</td></tr>"

    html = f"""<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <title>پنل پروکسی - وضعیت فعلی</title>
    <style>
        body {{ font-family: sans-serif; background: #0a0f1e; color: #eee; padding: 20px; }}
        .container {{ max-width: 800px; margin: auto; background: #151e2c; border-radius: 15px; padding: 20px; }}
        a {{ color: #60a5fa; }}
    </style>
</head>
<body>
<div class="container">
    <h1>📡 کانفیگ‌های فعال</h1>
    <p>UUID: {UUID} | SNI: {SNI} | پروتکل: {SECURITY}</p>
    <h2>🌐 IPهای تمیز</h2>
    <table border="1" cellpadding="5"><tr><th>IP</th><th>پورت</th><th>وضعیت</th></tr>{ip_rows}</table>
    <h2>🔗 لینک سابسکریپشن</h2>
    <a href="subscription.txt">subscription.txt</a>
</div>
</body>
</html>"""
    with open(f"{WORK_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    shutil.copy(f"{WORK_DIR}/index.html", "index.html")

# ======================== اجرای اصلی ========================
def main():
    print("🚀 شروع ساخت کانفیگ با تنظیمات سفارشی...")
    print(f"UUID: {UUID}")
    print(f"تعداد IPهای تمیز: {len(IPS)}")
    for ip in IPS:
        print(f"  - {ip}")
    print(f"SNI: {SNI}, Security: {SECURITY}, Network: {NETWORK}")
    generate_configs()
    build_static_panel()
    print("✅ کانفیگ‌ها ساخته شدند و در ریشه مخزن و پوشه configs/ ذخیره شدند.")

if __name__ == "__main__":
    main()
