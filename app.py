import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/check')
def check():
    data = request.args.get('data')
    return jsonify({"status": "ok", "input": data})

port = int(os.environ.get("PORT", 5500))
app.run(host="0.0.0.0", port=port)
