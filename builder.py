#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
پروکسی بیلدر خودکار - اسکن IP تمیز، تولید کانفیگ، ساخت پنل HTML
خروجی: پوشه public/ (پنل) و configs/ (فایل‌های کانفیگ) و همچنین کپی فایل‌ها در ریشه
"""

import os
import json
import base64
import urllib.request
import shutil
from datetime import datetime

# ======================== تنظیمات ========================
UUID = os.environ.get("UUID", "b3e5e5b8-0e1d-4f8a-8e5c-6f2e5a1b9c8d")
WORK_DIR = "public"
CONFIG_DIR = "configs"

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# ======================== ۱. دریافت IPهای تمیز ========================
def get_clean_ips():
    """دریافت IPهای تمیز کلاودفلیر از منابع مختلف"""
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
                    ip_list.extend(ips[:30])
                    break
        except Exception:
            continue

    if not ip_list:
        ip_list = [
            "104.18.0.0:443", "104.16.0.0:443", "104.20.0.0:443",
            "172.67.0.0:443", "188.114.96.0:443"
        ]
    
    # تست ساده اتصال
    good_ips = []
    for ip in ip_list[:15]:
        addr = ip.split(":")[0]
        try:
            urllib.request.urlopen(f"https://{addr}", timeout=2)
            good_ips.append(ip)
        except Exception:
            pass
    return good_ips if good_ips else ip_list[:10]

# ======================== ۲. تولید کانفیگ‌ها ========================
def generate_configs(ips):
    """تولید کانفیگ VLESS، VMESS، Trojan و سابسکریپشن base64"""
    vless_list = []
    vmess_list = []
    trojan_list = []

    for ip in ips:
        addr = ip.split(":")[0]
        port = ip.split(":")[1] if ":" in ip else "443"

        vless = f"vless://{UUID}@{addr}:{port}?encryption=none&security=tls&sni=www.microsoft.com&type=tcp&flow=xtls-rprx-vision#Clean-{addr}"
        vless_list.append(vless)

        trojan = f"trojan://{UUID}@{addr}:{port}?security=tls&sni=www.bing.com#Clean-{addr}"
        trojan_list.append(trojan)

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

    # کپی فایل‌های مهم به ریشه برای دسترسی راحت
    shutil.copy(f"{CONFIG_DIR}/subscription.txt", "subscription.txt")
    shutil.copy(f"{CONFIG_DIR}/vless.txt", "vless.txt")
    shutil.copy(f"{CONFIG_DIR}/vmess.txt", "vmess.txt")
    shutil.copy(f"{CONFIG_DIR}/trojan.txt", "trojan.txt")

    return {"vless": vless_list, "vmess": vmess_list, "trojan": trojan_list}

# ======================== ۳. ساخت پنل HTML ========================
def build_html_panel(ips):
    """ایجاد فایل index.html برای نمایش اطلاعات و لینک‌های دانلود"""
    ip_rows = ""
    for ip in ips:
        addr = ip.split(":")[0]
        port = ip.split(":")[1]
        ip_rows += f"<tr><td>{addr}</td><td>{port}</td><td>✅ فعال</td></td>"

    html = f"""<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>پنل پروکسی خودکار</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0f1e; color: #e0e0e0; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: auto; background: #151e2c; border-radius: 15px; padding: 20px; }}
        h1, h2 {{ color: #3b82f6; text-align: center; }}
        .card {{ background: #1e2a3a; border-radius: 12px; padding: 15px; margin: 15px 0; }}
        .config-box {{ background: #0f172a; padding: 12px; border-radius: 8px; font-family: monospace; word-break: break-all; }}
        a {{ color: #60a5fa; text-decoration: none; }}
        button {{ background: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: center; border-bottom: 1px solid #334155; }}
        .footer {{ text-align: center; font-size: 12px; color: #6b7280; margin-top: 20px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 پنل مدیریت پروکسی خودکار</h1>
    <p>تاریخ بروزرسانی: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="card">
        <h2>📥 لینک‌های مستقیم کانفیگ (روی لینک کلیک کنید)</h2>
        <div class="config-box">
            🔹 <strong>VLESS</strong> – <a href="vless.txt" target="_blank">vless.txt</a><br>
            🔹 <strong>VMESS</strong> – <a href="vmess.txt" target="_blank">vmess.txt</a><br>
            🔹 <strong>Trojan</strong> – <a href="trojan.txt" target="_blank">trojan.txt</a><br>
            🔄 <strong>سابسکریپشن (Base64)</strong> – <a href="subscription.txt" target="_blank">subscription.txt</a>
        </div>
        <p>⚠️ برای استفاده در کلاینت، لینک سابسکریپشن را در قسمت Subscription وارد کنید.</p>
    </div>

    <div class="card">
        <h2>🌐 IPهای تمیز فعال</h2>
        <table>
            <thead><tr><th>IP</th><th>پورت</th><th>وضعیت</th></tr></thead>
            <tbody>{ip_rows}</tbody>
        </table>
    </div>

    <div class="card">
        <h2>⚙️ UUID جاری</h2>
        <p><code>{UUID}</code></p>
        <p>برای تغییر، در مخزن گیت‌هاب به <code>Settings → Secrets → UUID</code> مراجعه کنید.</p>
    </div>

    <div class="footer">
        ساخته شده با ❤️ توسط GitHub Actions | بروزرسانی خودکار هر ۶ ساعت
    </div>
</div>
</body>
</html>"""
    with open(f"{WORK_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    # کپی index.html به ریشه
    shutil.copy(f"{WORK_DIR}/index.html", "index.html")

# ======================== ۴. اجرای اصلی ========================
def main():
    print("🚀 شروع فرآیند ساخت پروکسی...")
    ips = get_clean_ips()
    print(f"✅ {len(ips)} IP تمیز پیدا شد.")
    generate_configs(ips)
    build_html_panel(ips)
    print("✅ همه فایل‌ها با موفقیت ساخته شدند.")
    print("📁 فایل‌های زیر در ریشه مخزن و پوشه configs/ قرار دارند:")
    print("   - index.html (پنل)")
    print("   - subscription.txt (سابسکریپشن)")
    print("   - vless.txt, vmess.txt, trojan.txt")

if __name__ == "__main__":
    main()
