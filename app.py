from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
from datetime import date
from functools import wraps

app = Flask(__name__)
app.secret_key = "clave_secreta_sistema_gastos"

# ==========================================
# BASE DE DATOS SQLITE
# ==========================================

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


# ==========================================
# DISEÑO CSS - AZUL ELEGANTE
# ==========================================

estilo = """
<style>
* {
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Arial, sans-serif;
    margin: 0;
    min-height: 100vh;
    color: #193454;
    background: linear-gradient(
        135deg,
        #071b35 0%,
        #124b85 48%,
        #65b9e8 100%
    );
    background-attachment: fixed;
}

header {
    background: linear-gradient(
        90deg,
        #06162d,
        #123c70,
        #1769a6
    );
    color: white;
    padding: 32px 15px;
    text-align: center;
    box-shadow: 0 5px 20px #0004;
}

header h1 {
    margin: 0 0 10px;
    letter-spacing: 1px;
}

header p {
    color: #c8e8ff;
    margin: 0;
}

nav {
    background: rgba(5, 23, 48, 0.95);
    padding: 18px;
    text-align: center;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 8px 14px;
    font-weight: 600;
    display: inline-block;
    transition: 0.3s;
}

nav a:hover {
    color: #69d5ff;
    transform: translateY(-2px);
}

.contenedor {
    max-width: 1000px;
    margin: 40px auto;
    background: rgba(255, 255, 255, 0.97);
    padding: 35px;
    border-radius: 18px;
    box-shadow: 0 15px 40px #0005;
}

h2 {
    color: #103e75;
    border-bottom: 3px solid #35a9e0;
    padding-bottom: 12px;
}

input {
    width: 100%;
    padding: 13px;
    margin: 9px 0 18px;
    border: 1px solid #b9d2e6;
    border-radius: 9px;
    font-size: 15px;
    background: #f5faff;
}

input:focus {
    outline: 2px solid #4daee7;
}

button {
    width: 100%;
    padding: 14px;
    margin-top: 10px;
    background: linear-gradient(
        90deg,
        #07529c,
        #1c91d2
    );
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: 0.3s;
}

button:hover {
    background: linear-gradient(
        90deg,
        #083d77,
        #0875b8
    );
    transform: translateY(-2px);
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th {
    background: #103d70;
    color: white;
    padding: 14px;
}

td {
    padding: 13px;
    border-bottom: 1px solid #dce8f3;
}

tr:nth-child(even) {
    background: #edf6fd;
}

tr:hover {
    background: #dcefff;
}

.total {
    background: linear-gradient(
        90deg,
        #d9efff,
        #a9d9fa
    );
    padding: 25px;
    border-left: 6px solid #0876bd;
    border-radius: 12px;
    font-size: 23px;
    font-weight: bold;
    color: #073b70;
}

/* BIENVENIDA */

.welcome {
    padding: 22px;
    border-radius: 14px;
    background: linear-gradient(
        120deg,
        #e3f3ff,
        #f5fbff
    );
    border-left: 5px solid #168bc9;
    margin-bottom: 25px;
}

/* TARJETAS DEL PANEL */

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 22px;
    margin: 25px 0;
}

.stat-card {
    padding: 25px;
    border-radius: 16px;
    color: white;
    background: linear-gradient(
        135deg,
        #103e75,
        #2196d2
    );
    box-shadow: 0 8px 20px #123b6540;
    transition: 0.3s;
}

.stat-card:nth-child(2) {
    background: linear-gradient(
        135deg,
        #087eaa,
        #38c5d9
    );
}

.stat-card:hover {
    transform: translateY(-5px);
}

.stat-card h3 {
    margin: 8px 0;
}

.stat-card p {
    color: #e3f5ff;
}

.stat-icon {
    font-size: 35px;
    margin-bottom: 12px;
}

.stat-number {
    font-size: 30px;
    font-weight: bold;
    margin-top: 10px;
}

/* ACCESOS RAPIDOS */

.quick-actions {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-top: 20px;
}

.action-link {
    display: block;
    padding: 20px;
    text-align: center;
    text-decoration: none;
    color: #104879;
    background: #e8f5ff;
    border: 1px solid #c3e4fa;
    border-radius: 12px;
    font-weight: bold;
    transition: 0.3s;
}

.action-link:hover {
    background: #cceaff;
    transform: translateY(-3px);
}

/* FORMULARIOS */

.form-card {
    background: #f4f9ff;
    padding: 22px;
    border-radius: 14px;
}

/* TABLAS RESPONSIVAS */

.table-wrap {
    width: 100%;
    overflow-x: auto;
}

/* IMPRESION */

@media print {
    body {
        background: white;
    }

    header, nav, button {
        display: none !important;
    }

    .contenedor {
        margin: 0;
        box-shadow: none;
        max-width: 100%;
    }
}

/* DISEÑO PARA CELULARES */

@media (max-width: 600px) {
    .contenedor {
        margin: 20px 12px;
        padding: 20px;
    }

    .dashboard-grid,
    .quick-actions {
        grid-template-columns: 1fr;
    }

    header h1 {
        font-size: 23px;
    }

    nav a {
        margin: 7px;
    }
}
</style>
"""


# ==========================================
# PLANTILLA GENERAL
# ==========================================

def pagina(contenido, titulo="Sistema de Gastos"):
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1">

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
            <a href="/">🏠 Inicio</a>
            <a href="/registrar">➕ Registrar gasto</a>
            <a href="/gastos">📋 Mis gastos</a>
            <a href="/reporte">📊 Reporte</a>
            <a href="/salir">🚪 Cerrar sesión</a>
        </nav>

        {% endif %}

        <div class="contenedor">
            {{contenido|safe}}
        </div>

    </body>
    </html>
    """, contenido=contenido, titulo=titulo)


# ==========================================
# PROTEGER LAS RUTAS
# ==========================================

def requiere_login(funcion):

    @wraps(funcion)
    def verificar(*args, **kwargs):

        if "usuario" not in session:
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return verificar


# ==========================================
# ACCESO AL SISTEMA
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    mensaje = ""

    if request.method == "POST":

        usuario = request.form.get("usuario", "")
        clave = request.form.get("clave", "")

        if usuario == "admin" and clave == "123":

            session["usuario"] = usuario

            return redirect(url_for("inicio"))

        mensaje = """
        <p style='color:red'>
            Usuario o contraseña incorrectos.
        </p>
        """

    contenido = f"""
    <h2>🔐 Iniciar sesión</h2>

    {mensaje}

    <form method="POST">

        <label>Usuario</label>

        <input
            name="usuario"
            required
            placeholder="Ingrese usuario">

        <label>Contraseña</label>

        <input
            type="password"
            name="clave"
            required
            placeholder="Ingrese contraseña">

        <button type="submit">
            Ingresar al sistema
        </button>

    </form>
    """

    return pagina(contenido, "Acceso al sistema")


# ==========================================
# CERRAR SESION
# ==========================================

@app.route("/salir")
def salir():

    session.clear()

    return redirect(url_for("login"))


# ==========================================
# PANEL PRINCIPAL
# ==========================================

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

    <div class="welcome">

        <h2>¡Bienvenido, administrador! 👋</h2>

        <p>
            Este es tu panel de control de gastos personales.
        </p>

        <p>
            Administra tus movimientos de manera sencilla
            y organizada.
        </p>

    </div>

    <h2>📊 Resumen general</h2>

    <div class="dashboard-grid">

        <div class="stat-card">

            <div class="stat-icon">💰</div>

            <h3>Total de gastos</h3>

            <div class="stat-number">
                S/ {total:.2f}
            </div>

            <p>Dinero registrado</p>

        </div>

        <div class="stat-card">

            <div class="stat-icon">📋</div>

            <h3>Registros realizados</h3>

            <div class="stat-number">
                {cantidad}
            </div>

            <p>Gastos registrados</p>

        </div>

    </div>

    <h2>⚡ Accesos rápidos</h2>

    <div class="quick-actions">

        <a class="action-link" href="/registrar">
            ➕ Registrar nuevo gasto
        </a>

        <a class="action-link" href="/gastos">
            📋 Consultar mis gastos
        </a>

        <a class="action-link" href="/reporte">
            📈 Ver reporte
        </a>

        <a class="action-link" href="/salir">
            🚪 Cerrar sesión
        </a>

    </div>

    """

    return pagina(contenido, "Panel principal")


# ==========================================
# REGISTRAR GASTOS
# ==========================================

@app.route("/registrar", methods=["GET", "POST"])
@requiere_login
def registrar():

    mensaje = ""

    if request.method == "POST":

        fecha = request.form.get("fecha", "")
        descripcion = request.form.get(
            "descripcion", ""
        ).strip()

        try:

            monto = float(request.form.get("monto", ""))

            if not fecha or not descripcion or monto <= 0:
                raise ValueError

            conexion = conectar()

            conexion.execute(
                """
                INSERT INTO gastos
                (fecha, descripcion, monto)
                VALUES (?, ?, ?)
                """,
                (fecha, descripcion, monto)
            )

            conexion.commit()
            conexion.close()

            return redirect(url_for("gastos"))

        except ValueError:

            mensaje = """
            <p style='color:red'>
                Ingrese datos válidos y un monto mayor que cero.
            </p>
            """

    contenido = f"""

    <h2>➕ Registrar nuevo gasto</h2>

    <div class="form-card">

        {mensaje}

        <form method="POST">

            <label>Fecha:</label>

            <input
                type="date"
                name="fecha"
                value="{date.today()}"
                required>

            <label>Descripción:</label>

            <input
                type="text"
                name="descripcion"
                required
                placeholder="Descripción del gasto">

            <label>Monto (S/):</label>

            <input
                type="number"
                name="monto"
                min="0.01"
                step="0.01"
                required
                placeholder="Ejemplo: 50.00">

            <button type="submit">
                💾 Guardar gasto
            </button>

        </form>

    </div>

    """

    return pagina(contenido, "Registrar gasto")


# ==========================================
# LISTAR GASTOS
# ==========================================

@app.route("/gastos")
@requiere_login
def gastos():

    conexion = conectar()

    registros = conexion.execute(
        """
        SELECT * FROM gastos
        ORDER BY fecha DESC, id DESC
        """
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

    <h2>📋 Listado de gastos</h2>

    <p>
        Consulta todos los gastos registrados en el sistema.
    </p>

    <div class="table-wrap">

        <table>

            <tr>
                <th>Fecha</th>
                <th>Descripción</th>
                <th>Monto</th>
            </tr>

            {filas if filas else
            '<tr><td colspan="3">No hay gastos registrados.</td></tr>'}

        </table>

    </div>

    """

    return pagina(contenido, "Mis gastos")


# ==========================================
# REPORTE DE GASTOS
# ==========================================

@app.route("/reporte")
@requiere_login
def reporte():

    conexion = conectar()

    registros = conexion.execute(
        """
        SELECT * FROM gastos
        ORDER BY fecha DESC
        """
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

    <h2>📈 Reporte de gastos</h2>

    <div class="total">

        💰 Total acumulado: S/ {total:.2f}

    </div>

    <div class="table-wrap">

        <table>

            <tr>
                <th>Fecha</th>
                <th>Descripción</th>
                <th>Monto</th>
            </tr>

            {filas if filas else
            '<tr><td colspan="3">Sin registros.</td></tr>'}

        </table>

    </div>

    <br>

    <button onclick="window.print()">
        🖨️ Imprimir reporte
    </button>

    """

    return pagina(contenido, "Reporte de gastos")


# ==========================================
# EJECUTAR APLICACION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)
