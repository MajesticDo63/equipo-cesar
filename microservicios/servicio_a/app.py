# Servicio A — Rutas principales del inventario
# No contiene time.sleep (tarea pesada está en Servicio B)

import os
import requests
import mysql.connector
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Configuración de BD desde variables de entorno
def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Inventario — Microservicios</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }
        h1 { color: #185FA5; }
        h2 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
        form { background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        input, select { padding: 8px; margin: 5px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 8px 16px; background: #185FA5; color: white; border: none; border-radius: 4px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background: #185FA5; color: white; }
        .alerta { background: #fff3cd; padding: 10px; border-radius: 4px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Sistema de Inventario — Microservicios</h1>

    <h2>Registrar Producto</h2>
    <form id="formProducto">
        <input type="text" id="nombre" placeholder="Nombre del producto" required>
        <input type="text" id="categoria" placeholder="Categoría" required>
        <input type="number" id="precio" placeholder="Precio" step="0.01" required>
        <input type="number" id="stock_actual" placeholder="Stock inicial" required>
        <input type="number" id="stock_minimo" placeholder="Stock mínimo" required>
        <button type="button" onclick="registrarProducto()">Registrar</button>
    </form>

    <h2>Registrar Movimiento</h2>
    <form id="formMovimiento">
        <input type="number" id="producto_id" placeholder="ID del producto" required>
        <select id="tipo">
            <option value="entrada">Entrada</option>
            <option value="salida">Salida</option>
        </select>
        <input type="number" id="cantidad" placeholder="Cantidad" required>
        <input type="text" id="descripcion" placeholder="Descripción">
        <button type="button" onclick="registrarMovimiento()">Registrar</button>
    </form>

    <h2>Stock Actual</h2>
    <button onclick="verStock()">Ver Stock</button>
    <div id="tablaStock"></div>

    <h2>Productos Bajo Stock Mínimo</h2>
    <button onclick="verBajoStock()">Ver Alertas</button>
    <div id="alertas"></div>

    <script>
        async function registrarProducto() {
            const data = {
                nombre: document.getElementById('nombre').value,
                categoria: document.getElementById('categoria').value,
                precio: document.getElementById('precio').value,
                stock_actual: document.getElementById('stock_actual').value,
                stock_minimo: document.getElementById('stock_minimo').value
            };
            const r = await fetch('/productos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const res = await r.json();
            alert(res.mensaje || res.error);
        }

        async function registrarMovimiento() {
            const data = {
                producto_id: document.getElementById('producto_id').value,
                tipo: document.getElementById('tipo').value,
                cantidad: document.getElementById('cantidad').value,
                descripcion: document.getElementById('descripcion').value
            };
            const r = await fetch('/movimiento', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const res = await r.json();
            alert(res.mensaje || res.error);
        }

        async function verStock() {
            const r = await fetch('/productos');
            const res = await r.json();
            let html = '<table><tr><th>ID</th><th>Nombre</th><th>Categoría</th><th>Precio</th><th>Stock</th><th>Stock Mínimo</th></tr>';
            res.productos.forEach(p => {
                html += `<tr><td>${p.id}</td><td>${p.nombre}</td><td>${p.categoria}</td><td>$${p.precio}</td><td>${p.stock_actual}</td><td>${p.stock_minimo}</td></tr>`;
            });
            html += '</table>';
            document.getElementById('tablaStock').innerHTML = html;
        }

        async function verBajoStock() {
            const r = await fetch('/bajostock');
            const res = await r.json();
            let html = '';
            res.productos.forEach(p => {
                html += `<div class="alerta">⚠ ${p.nombre} — Stock: ${p.stock_actual} / Mínimo: ${p.stock_minimo}</div>`;
            });
            document.getElementById('alertas').innerHTML = html || '<p>No hay productos bajo stock mínimo.</p>';
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/productos", methods=["POST"])
def registrar_producto():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, categoria, precio, stock_actual, stock_minimo)
            VALUES (%s, %s, %s, %s, %s)
        """, (data["nombre"], data["categoria"], data["precio"],
              data["stock_actual"], data["stock_minimo"]))
        conn.commit()
        return jsonify({"mensaje": "Producto registrado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/productos", methods=["GET"])
def consultar_stock():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        productos = cursor.fetchall()
        return jsonify({"productos": productos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/movimiento", methods=["POST"])
def registrar_movimiento():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT stock_actual, stock_minimo, nombre FROM productos WHERE id = %s",
                      (data["producto_id"],))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        stock_actual, stock_minimo, nombre = producto
        cantidad = int(data["cantidad"])

        if data["tipo"] == "entrada":
            nuevo_stock = stock_actual + cantidad
        else:
            if cantidad > stock_actual:
                return jsonify({"error": "Stock insuficiente"}), 400
            nuevo_stock = stock_actual - cantidad

        cursor.execute("""
            INSERT INTO movimientos (producto_id, tipo, cantidad, descripcion)
            VALUES (%s, %s, %s, %s)
        """, (data["producto_id"], data["tipo"], cantidad, data.get("descripcion", "")))

        cursor.execute("UPDATE productos SET stock_actual = %s WHERE id = %s",
                      (nuevo_stock, data["producto_id"]))
        conn.commit()

        # Si el stock queda bajo, llamar al Servicio B para la alerta
        if data["tipo"] == "salida" and nuevo_stock < stock_minimo:
            try:
                # Llama a Servicio B usando nombre de contenedor
                requests.post("http://servicio_b:5001/alerta", json={
                    "producto_id": data["producto_id"],
                    "nombre": nombre,
                    "stock_actual": nuevo_stock,
                    "stock_minimo": stock_minimo
                }, timeout=15)
                return jsonify({"mensaje": f"Salida registrada. ALERTA enviada a Servicio B para {nombre}"})
            except Exception as e:
                # Si B está apagado, igual guarda el movimiento
                return jsonify({"mensaje": f"Salida registrada. Servicio B no disponible: {str(e)}"})

        return jsonify({"mensaje": "Movimiento registrado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route("/bajostock", methods=["GET"])
def bajo_stock():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM productos
            WHERE stock_actual < stock_minimo
            ORDER BY stock_actual ASC
        """)
        productos = cursor.fetchall()
        return jsonify({"productos": productos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
