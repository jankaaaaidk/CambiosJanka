from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"mensaje": "Backend funcionando :v🚀", "endpoint": "/precio"})

@app.route("/precio")
def precio():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

        # ARS
        data_ars = {
            "asset": "USDT",
            "fiat": "ARS",
            "tradeType": "SELL",
            "page": 1,
            "rows": 10
        }

        r1 = requests.post(url, json=data_ars).json()
        precios_ars = [float(i["adv"]["price"]) for i in r1["data"]][1:4]
        promedio_ars = sum(precios_ars) / 3

        # USD
        data_usd = {
            "asset": "USDT",
            "fiat": "USD",
            "tradeType": "SELL",
            "page": 1,
            "rows": 10,
            "payTypes": ["Banco Pichincha"]
        }

        r2 = requests.post(url, json=data_usd).json()
        precios_usd = [float(i["adv"]["price"]) for i in r2["data"]][1:4]
        promedio_usd = sum(precios_usd) / 3

        ajuste = max(0, promedio_usd - 1)
        tipo_final = promedio_ars * (1 - ajuste)

        
        return jsonify({
        "tipo": tipo_final,
        "debug": {
        "usd_raw": [i["adv"]["price"] for i in r2["data"][:5]],
        "usd_usados": precios_usd,
        "promedio_usd": promedio_usd,
        "ars_usados": precios_ars,
        "promedio_ars": promedio_ars,
        "ajuste": ajuste
        }})

    except Exception as e:
        return jsonify({"error": str(e)})



# 🔥 IMPORTANTE PARA RENDER
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
