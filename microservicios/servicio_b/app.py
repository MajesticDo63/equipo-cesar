# Servicio B — Tarea pesada: generación de alertas de reposición
# No contiene rutas HTML, solo procesa alertas

import os
import time
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de BD desde variables de entorno
def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )

# Ruta única — procesar alerta de reposición (tarea pesada)
@app.route("/alerta", methods=["POST"])
def generar_alerta():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        print(f"[Servicio B] Procesando alerta para {data['nombre']}...")

        # Tarea pesada — simula proceso costoso de notificación
        time.sleep(5)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alertas (producto_id, mensaje)
            VALUES (%s, %s)
        """, (data["producto_id"],
              f"Stock bajo: {data['nombre']} tiene {data['stock_actual']} unidades (mínimo: {data['stock_minimo']})"))
        conn.commit()
        print(f"[Servicio B] Alerta guardada para {data['nombre']}")
        return jsonify({"mensaje": "Alerta generada correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
