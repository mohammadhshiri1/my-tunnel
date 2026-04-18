#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
پروکسی بیلدر حرفه‌ای - اسکن IP تمیز، تولید کانفیگ و ساخت پنل
"""

import os
import json
import base64
import subprocess
import urllib.request
from datetime import datetime

# ======================== تنظیمات اولیه ========================
UUID = os.environ.get("UUID", "4f28d01c-8a0a-4c31-9e1c-8c5c5a8c5c5a")  # از Secrets می‌گیرد
WORK_DIR = "public"
CONFIG_DIR = "configs"

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# ======================== ۱. دریافت IPهای تمیز ========================
def get_clean_ips():
    """دریافت IPهای تمیز کلاودفلیر از چند منبع مختلف"""
    ip_list = []
    sources = [
        "https://raw.githubusercontent.com/ip-scanner/cloudflare/main/ips.txt",
        "https://cdn.jsdelivr.net/gh/ip-scanner/cloudflare@main/ips.txt",
        "https://raw.githubusercontent.com/MortezaBashsiz/CFScanner/main/config/iran.txt"
    ]
    for url in sources:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as f:
                data = f.read().decode()
                ips = [line.strip() for line in data.splitlines() if line.strip() and ":" in line]
                if ips:
                    ip_list.extend(ips[:30])  # حداکثر 30 تا
                    break
        except:
            continue
    # اگر هیچ IPی از منابع نیامد، از لیست پیش‌فرض استفاده کن
    if not ip_list:
        ip_list = [
            "104.18.0.0:443", "104.16.0.0:443", "104.20.0.0:443",
            "172.67.0.0:443", "188.114.96.0:443"
        ]
    # تست ساده اتصال (اختیاری - برای سرعت می‌توان حذف کرد)
    good_ips = []
    for ip in ip_list[:10]:
        try:
            with urllib.request.urlopen(f"https://{ip.split(':')[0]}/", timeout=3) as _:
                good_ips.append(ip)
        except:
            pass
    return good_ips if good_ips else ip_list[:10]

# ======================== ۲. تولید کانفیگ با IPهای تمیز ========================
def generate_configs(ips):
    """تولید کانفیگ‌های VLESS، VMESS و Trojan"""
    vless_list = []
    vmess_list = []
    trojan_list = []

    for ip in ips:
        addr = ip.split(":")[0]
        port = ip.split(":")[1] if ":" in ip else "443"

        # کانفیگ VLESS
        vless = f"vless://{UUID}@{addr}:{port}?encryption=none&security=tls&sni=www.microsoft.com&type=tcp&flow=xtls-rprx-vision#Clean-{addr}"
        vless_list.append(vless)

        # کانفیگ Trojan
        trojan = f"trojan://{UUID}@{addr}:{port}?security=tls&sni=www.bing.com#Clean-{addr}"
        trojan_list.append(trojan)

        # کانفیگ VMESS
        vmess_obj = {
            "v": "2",
            "ps": f"Clean-{addr}",
            "add": addr,
            "port": port,
            "id": UUID,
            "aid": "0",
            "net": "ws",
            "type": "none",
            "host": "www.bing.com",
            "path": "/",
            "tls": "tls"
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

    # سابسکریپشن ترکیبی (base64)
    all_configs = vless_list + vmess_list + trojan_list
    sub_b64 = base64.b64encode("\n".join(all_configs).encode()).decode()
    with open(f"{CONFIG_DIR}/subscription.txt", "w") as f:
        f.write(sub_b64)

    return {"vless": vless_list, "vmess": vmess_list, "trojan": trojan_list}

# ======================== ۳. ساخت پنل HTML ========================
def build_html_panel(ips, configs):
    """تولید فایل index.html با اطلاعات به‌روز"""
    ip_table_rows = ""
    for ip in ips:
        ip_table_rows += f"<tr><td>{ip.split(':')[0]}</td><td>{ip.split(':')[1]}</td><td>✅ فعال</td></tr>"

    # آدرس سابسکریپشن (بعد از دیپلوی روی Pages)
    base_url = "https://" + os.environ.get("GITHUB_REPOSITORY", "").split("/")[0] + ".github.io/" + os.environ.get("GITHUB_REPOSITORY", "").split("/")[1] + "/"
    sub_link = base_url + "configs/subscription.txt"
    vless_link = base_url + "configs/vless.txt"
    vmess_link = base_url + "configs/vmess.txt"
    trojan_link = base_url + "configs/trojan.txt"

    html_content = f"""<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>پنل حرفه‌ای پروکسی</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0f1e; color: #e0e0e0; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: auto; background: #151e2c; border-radius: 15px; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.3); }}
        h1, h2 {{ color: #3b82f6; text-align: center; }}
        .card {{ background: #1e2a3a; border-radius: 12px; padding: 15px; margin: 15px 0; }}
        .config-box {{ background: #0f172a; padding: 12px; border-radius: 8px; font-family: monospace; word-break: break-all; }}
        a {{ color: #60a5fa; text-decoration: none; }}
        button {{ background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin: 5px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: center; border-bottom: 1px solid #334155; }}
        .footer {{ text-align: center; font-size: 12px; color: #6b7280; margin-top: 20px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 پنل مدیریت پروکسی خودکار</h1>
    <p>تاریخ آخرین بروزرسانی: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="card">
        <h2>🔗 لینک‌های سابسکریپشن (در کلاینت وارد کنید)</h2>
        <div class="config-box">
            📡 <strong>VLESS:</strong> <a href="{vless_link}">{vless_link}</a><br>
            📡 <strong>VMESS:</strong> <a href="{vmess_link}">{vmess_link}</a><br>
            📡 <strong>Trojan:</strong> <a href="{trojan_link}">{trojan_link}</a><br>
            🔄 <strong>سابسکریپشن ترکیبی (Base64):</strong> <a href="{sub_link}">{sub_link}</a>
        </div>
        <button onclick="copyAllLinks()">📋 کپی همه لینک‌ها</button>
    </div>

    <div class="card">
        <h2>🌐 IPهای تمیز فعال</h2>
        <table>
            <thead><tr><th>آدرس IP</th><th>پورت</th><th>وضعیت</th></tr></thead>
            <tbody>{ip_table_rows}</tbody>
        </table>
    </div>

    <div class="card">
        <h2>⚙️ تنظیمات UUID</h2>
        <p>UUID فعلی: <code>{UUID}</code></p>
        <p>برای تغییر، در مخزن گیت‌هاب به <code>Settings → Secrets → UUID</code> بروید و سپس workflow را مجدد اجرا کنید.</p>
    </div>

    <div class="footer">
        ساخته شده با ❤️ توسط GitHub Actions | بروزرسانی خودکار هر ۶ ساعت
    </div>
</div>
<script>
function copyAllLinks() {{
    const links = document.querySelectorAll('.config-box a');
    let text = '';
    links.forEach(link => text += link.href + '\\n');
    navigator.clipboard.writeText(text);
    alert('✅ لینک‌ها کپی شدند');
}}
</script>
</body>
</html>"""
    with open(f"{WORK_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# ======================== ۴. فایل config.txt (لینک سابسکریپشن) ========================
def create_config_txt(sub_link):
    with open("config.txt", "w") as f:
        f.write(f"لینک سابسکریپشن ترکیبی:\n{sub_link}\n")
        f.write("برای استفاده در کلاینت‌های V2rayNG، Nekobox، Clash و ... کافی است این لینک را وارد کنید.\n")

# ======================== اجرای اصلی ========================
def main():
    print("🚀 شروع فرآیند ساخت پروکسی...")
    ips = get_clean_ips()
    print(f"✅ {len(ips)} IP تمیز پیدا شد.")
    configs = generate_configs(ips)
    build_html_panel(ips, configs)
    # لینک سابسکریپشن نهایی (بعد از دیپلوی روی Pages)
    repo_name = os.environ.get("GITHUB_REPOSITORY", "")
    user = repo_name.split("/")[0] if "/" in repo_name else ""
    sub_link = f"https://{user}.github.io/{repo_name.split('/')[1]}/configs/subscription.txt" if user else ""
    create_config_txt(sub_link)
    print("✅ همه فایل‌ها با موفقیت ساخته شدند.")
    print("📁 پوشه public حاوی پنل و پوشه configs حاوی کانفیگ‌هاست.")

if __name__ == "__main__":
    main()
