import re
import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8647240736:AAEGXuwmtZkUvAfbURX2BcyyuoWD-TekP_0"

# -------- استخراج الروابط --------
def extract_links(file_path):
    links = set()
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        for word in content.split():
            if word.startswith("http://") or word.startswith("https://"):
                word = word.strip().strip(",;()[]{}<>")
                links.add(word)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    for word in cell.split():
                        if word.startswith("http://") or word.startswith("https://"):
                            word = word.strip().strip(",;()[]{}<>")
                            links.add(word)
    except:
        pass
    return list(links)

# -------- تجاهل المواقع المحمية --------
def has_protection(text):
    text = text.lower()
    return any(x in text for x in ["cloudflare", "cf-ray", "captcha", "recaptcha", "hcaptcha"])

# -------- تحقق كلمات الهدف --------
def is_target(html):
    text = html.lower()
    keywords = ["give", "donate", "donation", "support"]
    return any(k in text for k in keywords)

# -------- استخراج الفورم النهائي للتبرع --------
def extract_donation_link(soup, link):
    # الفورم الأساسي
    for f in soup.find_all("form"):
        action = f.get("action") or ""
        if action:
            if action.startswith("http"):
                return action
            else:
                return link.rstrip("/") + "/" + action.lstrip("/")
    # iframe
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if src and "http" in src:
            return src
    return None

# -------- فحص الموقع --------
async def check_site(session, link):
    try:
        async with session.get(link) as r:
            if r.status != 200:
                return None
            html = await r.text()
            if has_protection(html):
                return None
            if not is_target(html):
                return None
            soup = BeautifulSoup(html, "html.parser")
            donation_link = extract_donation_link(soup, link)
            return donation_link if donation_link else link
    except:
        return None

# -------- معالجة الملف وإرسال النتائج --------
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    input_path = "input_file"
    output_path = "result.txt"
    await file.download_to_drive(input_path)
    await update.message.reply_text("🔥 جاري الفحص...")

    links = extract_links(input_path)
    results = []

    connector = aiohttp.TCPConnector(limit=200)
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [check_site(session, link) for link in links]
        for future in asyncio.as_completed(tasks):
            res = await future
            if res:
                results.append(res)

    # إزالة التكرار
    results = list(set(results))

    # حفظ النتائج
    with open(output_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(r + "\n")

    # إرسال رسالة مع عدد الروابط
    await update.message.reply_text(f"✅ الفحص خلص! تم استخراج {len(results)} رابط 🔥")

    # إرسال الملف
    await update.message.reply_document(InputFile(output_path))

# -------- تشغيل البوت --------
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
print("🤖 BOT RUNNING...🔥")
app.run_polling()
