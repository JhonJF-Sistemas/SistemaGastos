from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = "clave_secreta_sistema_gastos"

# BASE DE DATOS SQLITE
def conectar():
    conexion = sqlite3.connect("gastos.db")
    conexion.row_factory = sqlite3.Row
    return conexion

def crear_tabla():
    conexion = conectar()
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()

crear_tabla()

# DISEÑO HTML
estilo = """
<style>
body {
    font-family: Arial;
    background: #eef2f7;
    margin: 0;
    color: #263449;
}
header {
    background: #17365d;
    color: white;
    padding: 22px;
    text-align: center;
}
nav {
    background: #244b78;
    padding: 15px;
    text-align: center;
}
nav a {
    color: white;
    text-decoration: none;
    margin: 12px;
}
.contenedor {
    max-width: 900px;
    margin: 35px auto;
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 3px 12px #0002;
}
input, button {
    padding: 12px;
    margin: 8px 0;
    width: 100%;
    box-sizing: border-box;
}
button {
    background: #1769aa;
    color: white;
    border: 0;
    cursor: pointer;
    border-radius: 5px;
}
table {
    width: 100%;
    border-collapse: collapse;
}
td, th {
    border: 1px solid #ddd;
    padding: 12px;
}
th {
    background: #17365d;
    color: white;
}
.total {
    background: #e0f2fe;
    padding: 20px;
    font-size: 22px;
    font-weight: bold;
}
</style>
"""

def pagina(contenido, titulo="Sistema de Gastos"):
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{titulo}}</title>
        """ + estilo + """
    </head>
    <body>
        <header>
            <h1>SISTEMA DE CONTROL DE GASTOS</h1>
            <p>Administración de gastos personales</p>
        </header>
        {% if session.get('usuario') %}
        <nav>
            <a href="/">Inicio</a>
            <a href="/registrar">Registrar gasto</a>
            <a href="/gastos">Mis gastos</a>
            <a href="/reporte">Reporte</a>
            <a href="/salir">Cerrar sesión</a>
        </nav>
        {% endif %}
        <div class="contenedor">{{contenido|safe}}</div>
    </body>
    </html>
    """, contenido=contenido, titulo=titulo)

# PROTEGER LAS RUTAS
def requiere_login(funcion):
    @wraps(funcion)
    def verificar(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return funcion(*args, **kwargs)
    return verificar

# ACCESO AL SISTEMA
@app.route("/login", methods=["GET", "POST"])
def login():
    mensaje = ""
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        clave = request.form.get("clave", "")

        if usuario == "admin" and clave == "123":
            session["usuario"] = usuario
            return redirect(url_for("inicio"))
        mensaje = "<p style='color:red'>Usuario o contraseña incorrectos.</p>"

    contenido = f"""
    <h2>Iniciar sesión</h2>
    {mensaje}
    <form method="POST">
        <label>Usuario</label>
        <input name="usuario" required placeholder="Ingrese usuario">
        <label>Contraseña</label>
        <input type="password" name="clave" required placeholder="Ingrese contraseña">
        <button type="submit">Ingresar</button>
    </form>
    """
    return pagina(contenido, "Acceso")

@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("login"))

# INICIO
@app.route("/")
@requiere_login
def inicio():
    conexion = conectar()
    cantidad = conexion.execute(
        "SELECT COUNT(*) FROM gastos"
    ).fetchone()[0]
    total = conexion.execute(
        "SELECT COALESCE(SUM(monto),0) FROM gastos"
    ).fetchone()[0]
    conexion.close()

    contenido = f"""
    <h2>Panel principal</h2>
    <p>Bienvenido, administrador.</p>
    <div class="total">Total de gastos: S/ {total:.2f}</div>
    <h3>Registros realizados: {cantidad}</h3>
    <p>Utilice el menú para registrar gastos y generar reportes.</p>
    """
    return pagina(contenido)

# REGISTRAR GASTOS
@app.route("/registrar", methods=["GET", "POST"])
@requiere_login
def registrar():
    mensaje = ""

    if request.method == "POST":
        fecha = request.form.get("fecha", "")
        descripcion = request.form.get("descripcion", "").strip()

        try:
            monto = float(request.form.get("monto", ""))
            if not fecha or not descripcion or monto <= 0:
                raise ValueError

            conexion = conectar()
            conexion.execute(
                "INSERT INTO gastos (fecha, descripcion, monto) VALUES (?, ?, ?)",
                (fecha, descripcion, monto)
            )
            conexion.commit()
            conexion.close()

            return redirect(url_for("gastos"))

        except ValueError:
            mensaje = "<p style='color:red'>Ingrese datos válidos y un monto mayor que cero.</p>"

    contenido = f"""
    <h2>Registrar nuevo gasto</h2>
    {mensaje}
    <form method="POST">
        <label>Fecha:</label>
        <input type="date" name="fecha" value="{date.today()}" required>
        <label>Descripción:</label>
        <input type="text" name="descripcion" required placeholder="Descripción del gasto">
        <label>Monto (S/):</label>
        <input type="number" name="monto" min="0.01" step="0.01" required>
        <button type="submit">Guardar gasto</button>
    </form>
    """
    return pagina(contenido)

# LISTAR GASTOS
@app.route("/gastos")
@requiere_login
def gastos():
    conexion = conectar()
    registros = conexion.execute(
        "SELECT * FROM gastos ORDER BY fecha DESC, id DESC"
    ).fetchall()
    conexion.close()

    filas = ""
    for g in registros:
        filas += f"""
        <tr>
            <td>{g['fecha']}</td>
            <td>{g['descripcion']}</td>
            <td>S/ {g['monto']:.2f}</td>
        </tr>
        """

    contenido = f"""
    <h2>Listado de gastos</h2>
    <table>
        <tr><th>Fecha</th><th>Descripción</th><th>Monto</th></tr>
        {filas if filas else '<tr><td colspan="3">No hay gastos registrados.</td></tr>'}
    </table>
    """
    return pagina(contenido)

# REPORTE
@app.route("/reporte")
@requiere_login
def reporte():
    conexion = conectar()
    registros = conexion.execute(
        "SELECT * FROM gastos ORDER BY fecha DESC"
    ).fetchall()
    total = conexion.execute(
        "SELECT COALESCE(SUM(monto),0) FROM gastos"
    ).fetchone()[0]
    conexion.close()

    filas = ""
    for g in registros:
        filas += f"""
        <tr>
            <td>{g['fecha']}</td>
            <td>{g['descripcion']}</td>
            <td>S/ {g['monto']:.2f}</td>
        </tr>
        """

    contenido = f"""
    <h2>Reporte de gastos</h2>
    <div class="total">Total acumulado: S/ {total:.2f}</div>
    <table>
        <tr><th>Fecha</th><th>Descripción</th><th>Monto</th></tr>
        {filas if filas else '<tr><td colspan="3">Sin registros.</td></tr>'}
    </table>
    <br>
    <button onclick="window.print()">Imprimir reporte</button>
    """
    return pagina(contenido)

if __name__ == "__main__":
    app.run(debug=True)