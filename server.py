from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"mensaje": "Backend funcionando 🚀", "endpoint": "/precio"})

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

        # más caros primero
        precios_ars.sort(reverse=True)
        precios_ars = precios_ars[:3]

        promedio_ars = sum(precios_ars) / len(precios_ars)

        # ======================
        # USD (buscar Pichincha en varias páginas)
        # ======================
        precios_usd = []

        for page in range(1, 6):  # buscar hasta 5 páginas
            data_usd = {
                "asset": "USDT",
                "fiat": "USD",
                "tradeType": "SELL",
                "page": page,
                "rows": 10
            }

            r2 = requests.post(url, json=data_usd, timeout=10).json()

            for i in r2.get("data", []):
                metodos = [m["tradeMethodName"] for m in i["adv"]["tradeMethods"]]

                if any("pichincha" in m.lower() for m in metodos):
                    precios_usd.append(float(i["adv"]["price"]))

            # parar si ya tenemos suficientes datos
            if len(precios_usd) >= 4:
                break

        if not precios_usd:
            promedio_usd = 1
        else:
            # ordenar de mayor a menor
            precios_usd.sort(reverse=True)

            # quitar el más alto (outlier tipo 1.090)
            precios_usd = precios_usd[1:]

            # tomar los siguientes 3 más altos
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
