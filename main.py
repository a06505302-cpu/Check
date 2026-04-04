import asyncio
from bs4 import BeautifulSoup
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright
import csv

TOKEN = "8647240736:AAEGXuwmtZkUvAfbURX2BcyyuoWD-TekP_0"

# -------- استخراج الروابط من TXT/CSV --------
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

# -------- استخراج الفورم النهائي --------
def extract_donation_link(soup, link):
    for f in soup.find_all("form"):
        action = f.get("action") or ""
        if action:
            if action.startswith("http"):
                return action
            else:
                return link.rstrip("/") + "/" + action.lstrip("/")
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if src and "http" in src:
            return src
    return None

# -------- فحص الرابط باستخدام Playwright --------
async def check_site(link, browser):
    try:
        page = await browser.new_page()
        await page.goto(link, timeout=30000)
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        donation_link = extract_donation_link(soup, link)
        await page.close()
        return donation_link if donation_link else link
    except:
        return link

# -------- التعامل مع الملف وإرسال النتائج --------
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    input_path = "input_file"
    output_path = "result.txt"
    await file.download_to_drive(input_path)
    await update.message.reply_text("🔥 جاري الفحص بالـ Playwright...")

    links = extract_links(input_path)
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [check_site(link, browser) for link in links]
        for future in asyncio.as_completed(tasks):
            res = await future
            if res:
                results.append(res)
        await browser.close()

    # إزالة التكرار مع الحفاظ على الترتيب
    results = list(dict.fromkeys(results))

    # حفظ النتائج
    with open(output_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(r + "\n")

    # إرسال رسالة وعدد الروابط
    await update.message.reply_text(f"✅ الفحص خلص! تم استخراج {len(results)} رابط 🔥")

    # إرسال الملف
    await update.message.reply_document(InputFile(output_path))

# -------- تشغيل البوت --------
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
print("🤖 BOT RUNNING...🔥")
app.run_polling()
