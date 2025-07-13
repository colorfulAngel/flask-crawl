from flask import Flask, make_response, request
import api
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, home!'

@app.route('/about')
def about():
    return 'About'

@app.route('/hello', methods=['GET'])
def hello_world():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"Flask API is alive. Time: {now}"

@app.route('/get-big-trend', methods=['POST'])
def getBigTrend():
    content = request.json
    target_stock = content["target_stock"]
    fetch_years = content["fetch_years"]

    print(f"[getBigTrend] target_stock:{target_stock}, fetch_years:{fetch_years}")
    status_code, df = api.getBigTrend(target_stock, fetch_years)

    # df.to_json('df.json', orient='records', lines=True)
    res = df.to_json(orient='records')
    return make_response(res, status_code)

@app.route('/get-five', methods=['POST'])
def getFive():
    content = request.json
    target_stock = content["target_stock"]
    fetch_years = content["fetch_years"]

    print(f"[getFive] target_stock:{target_stock}, fetch_years:{fetch_years}")
    status_code, df = api.getFive(target_stock, fetch_years)

    # df.to_json('df.json', orient='records', lines=True)
    res = df.to_json(orient='records')
    return make_response(res, status_code)

if __name__ == '__main__':
    # app.run()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)