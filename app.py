from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

@app.route('/check')
def check():
    card = request.args.get('card')

    # تجربة (تقدر تغيرها لاحقًا)
    result = random.choice(["approved", "live", "declined"])

    return jsonify({
        "card": card,
        "result": result,
        "message": f"{result.upper()} - processed",
        "time": int(time.time())
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
