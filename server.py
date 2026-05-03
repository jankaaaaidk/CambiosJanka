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

        r1 = requests.post(url, json=data_ars).json()

        precios_ars = [float(i["adv"]["price"]) for i in r1.get("data", [])]

        # eliminar outliers (ej: anuncios comerciales absurdos)
        if precios_ars:
            min_ars = min(precios_ars)
            precios_ars = [p for p in precios_ars if p < min_ars * 1.02]

        precios_ars = precios_ars[:3]

        if not precios_ars:
            return jsonify({"error": "No hay precios ARS"})

        promedio_ars = sum(precios_ars) / len(precios_ars)

        # ======================
        # USD (SIN payTypes)
        # ======================
        data_usd = {
            "asset": "USDT",
            "fiat": "USD",
            "tradeType": "SELL",
            "page": 1,
            "rows": 10
        }

        r2 = requests.post(url, json=data_usd).json()

        precios_usd = []

        for i in r2.get("data", []):
            metodos = [m["tradeMethodName"] for m in i["adv"]["tradeMethods"]]

            # filtrar solo Pichincha
            if any("Pichincha" in m for m in metodos):
                precios_usd.append(float(i["adv"]["price"]))

        # eliminar outliers
        if precios_usd:
            min_usd = min(precios_usd)
            precios_usd = [p for p in precios_usd if p < min_usd * 1.02]

        precios_usd = precios_usd[:3]

        # fallback si no hay datos
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
