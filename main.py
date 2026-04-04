import re
import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8647240736:AAEGXuwmtZkUvAfbURX2BcyyuoWD-TekP_0"

url_pattern = re.compile(r'https?://[^\s",]+')

# -------- استخراج الروابط --------
def extract_links(file_path):
    links = set()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        found = url_pattern.findall(content)
        for link in found:
            links.add(link.strip())

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    found = url_pattern.findall(cell)
                    for link in found:
                        links.add(link.strip())
    except:
        pass

    return list(links)

# -------- كشف حماية --------
def has_protection(text):
    text = text.lower()
    keywords = ["cloudflare", "cf-ray", "captcha", "recaptcha", "hcaptcha"]
    return any(k in text for k in keywords)

# -------- تحقق GiveWP + WordPress --------
def is_givewp_wp(html):
    text = html.lower()

    is_wp = "wp-content" in text or "wordpress" in text
    is_give = "givewp" in text or "give-form" in text or "plugins/give" in text

    return is_wp and is_give

# -------- فحص الموقع --------
async def check_site(session, link):
    try:
        async with session.get(link) as r:
            if r.status != 200:
                return None, None

            html = await r.text()

            if has_protection(html):
                return None, None

            if is_givewp_wp(html):
                return link, "TOP"  # نحطه فوق

            return link, "NORMAL"

    except:
        return None, None

# -------- عند استلام ملف --------
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    input_path = "input_file"
    output_path = "result.txt"

    await file.download_to_drive(input_path)
    await update.message.reply_text("🔥 جاري الفحص...")

    links = extract_links(input_path)
    await update.message.reply_text(f"📊 عدد المواقع: {len(links)}")

    top_links = []
    normal_links = []

    connector = aiohttp.TCPConnector(limit=200)
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [check_site(session, link) for link in links]

        for future in asyncio.as_completed(tasks):
            link, status = await future

            if not link:
                continue

            if status == "TOP":
                top_links.append(link)
            else:
                normal_links.append(link)

    # دمج (GiveWP فوق)
    final_list = list(set(top_links)) + list(set(normal_links))

    with open(output_path, "w", encoding="utf-8") as f:
        for r in final_list:
            f.write(r + "\n")

    await update.message.reply_document(InputFile(output_path))

# -------- تشغيل --------
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

print("🤖 BOT RUNNING...")
app.run_polling()
