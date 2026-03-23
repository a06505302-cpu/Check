from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/check', methods=['GET'])
def check():
    data = request.args.get('data')
    return jsonify({
        "status": "ok",
        "input": data
    })

app.run(host="0.0.0.0", port=5500)
