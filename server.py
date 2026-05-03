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

        # ======================
        # ARS
        # ======================
        data_ars = {
            "asset": "USDT",
            "fiat": "ARS",
            "tradeType": "SELL",
            "page": 1,
            "rows": 10
        }

        r1 = requests.post(url, json=data_ars, timeout=10).json()
        precios_ars = [float(i["adv"]["price"]) for i in r1.get("data", [])]

        if not precios_ars:
            return jsonify({"error": "No hay precios ARS"})

        precios_ars.sort(reverse=True)  # 👈 más caros primero
        precios_ars = precios_ars[:3]

        promedio_ars = sum(precios_ars) / len(precios_ars)

        # ======================
        # USD (Pichincha)
        # ======================
        data_usd = {
            "asset": "USDT",
            "fiat": "USD",
            "tradeType": "SELL",
            "page": 1,
            "rows": 10
        }

        r2 = requests.post(url, json=data_usd, timeout=10).json()

        precios_usd = []

        for i in r2.get("data", []):
            metodos = [m["tradeMethodName"] for m in i["adv"]["tradeMethods"]]

            if any("Pichincha" in m for m in metodos):
                precios_usd.append(float(i["adv"]["price"]))

        if not precios_usd:
            promedio_usd = 1
        else:
            # 👇 ordenar de mayor a menor
            precios_usd.sort(reverse=True)

            # ❌ quitar el más caro (outlier tipo 1.090)
            precios_usd = precios_usd[1:]

            # ✅ tomar los siguientes 3 más caros
            precios_usd = precios_usd[:3]

            if not precios_usd:
                promedio_usd = 1
            else:
                promedio_usd = sum(precios_usd) / len(precios_usd)

        # ======================
        # CALCULO FINAL
        # ======================
        ajuste = max(0, promedio_usd - 1)
        tipo_final = promedio_ars * (1 - ajuste)

        return jsonify({
            "tipo": tipo_final,
            "debug": {
                "ars_usados": precios_ars,
                "promedio_ars": promedio_ars,
                "usd_filtrados_pichincha": precios_usd,
                "promedio_usd": promedio_usd,
                "ajuste": ajuste
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# 🔥 IMPORTANTE PARA RENDER
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
