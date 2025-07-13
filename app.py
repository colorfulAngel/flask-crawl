from flask import Flask, make_response, request
import api

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, home!'

@app.route('/about')
def about():
    return 'About'

@app.route('/hello', methods=['GET'])
def hello_world():
    return "Hello, World!"

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
    app.run()