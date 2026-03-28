from flask import Flask, request, Response
import requests
import random
import time
import os

app = Flask(__name__)

# قائمة الـ User Agents عشوائية لزيادة التمويه
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Linux; Android 11)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
]

def get_headers(url):
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": url.split("/give")[0],
        "Referer": url
    }

@app.route("/donate", methods=["POST"])
def donate():
    data = request.json
    url = data.get("url")
    amount = data.get("amount")
    name = data.get("name")
    country = data.get("country")
    card = data.get("card")  # مفروض يكون string مفصول بـ "|"

    # التحقق من وجود جميع البيانات
    if not all([url, amount, name, country, card]):
        return Response("Missing parameters", status=400)

    try:
        number, month, year, cvv = card.split("|")
        session = requests.Session()
        headers = get_headers(url)

        try:
            # محاولة واحدة فقط، يمكن تكرارها أو تعديلها حسب الحاجة
            page = session.get(url, headers=headers, timeout=15)

            # تجهيز بيانات الطلب
            payload = {
                "amount": amount,
                "name": name,
                "country": country,
                "card_number": number,
                "card_exp_month": month,
                "card_exp_year": year,
                "card_cvc": cvv
            }

            # عنوان الـ AJAX الخاص بالموقع
            ajax_url = url.split("/give")[0] + "/wp-admin/admin-ajax.php"

            # إرسال الطلب
            resp = session.post(
                ajax_url,
                data=payload,
                headers=headers,
                timeout=15
            )

            # إعادة الرد كما هو
            return Response(
                resp.text,
                status=resp.status_code,
                content_type=resp.headers.get("Content-Type", "text/plain")
            )

        except Exception as e:
            return Response(str(e), status=500)

    except Exception as e:
        return Response(str(e), status=500)

if __name__ == "__main__":
    # تحديد البورت من البيئة، أو 8080 بشكل افتراضي
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
