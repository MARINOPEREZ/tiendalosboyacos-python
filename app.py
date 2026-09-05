from flask import Flask, render_template, request, redirect, session
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER_PRODUCTOS = "static/img/productos"
UPLOAD_FOLDER_USUARIOS  = "static/img/usuarios"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_UPLOAD_MB = 6  # Tamaño máximo por archivo en MB

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_imagen(file, carpeta, prefijo):
    """Guarda el archivo y retorna el nombre guardado, o None si no hay archivo."""
    if not file or file.filename == "":
        return None
    if allowed_file(file.filename):
        ext      = file.filename.rsplit(".", 1)[1].lower()
        nombre   = secure_filename(f"{prefijo}_{file.filename}")
        ruta     = os.path.join(carpeta, nombre)
        os.makedirs(carpeta, exist_ok=True)
        file.save(ruta)
        return nombre
    return None
from werkzeug.security import check_password_hash
from functools import wraps
import json

from config.db import get_connection, close_connection
from src.models.producto import Producto
from src.models.usuario import Usuario
from src.controllers.producto_ctrl  import ProductoController
from src.models.venta               import Venta
from src.models.categoria           import Categoria
from src.controllers.venta_ctrl     import VentaController
from src.controllers.usuario_ctrl import UsuarioController
from src.routes.producto_routes import producto_bp
from src.routes.usuario_routes import usuario_bp
from src.services.api_auth import auth_bp

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024  # 6 MB máximo por request
app.secret_key = "losboyacos2026"
app.json.ensure_ascii = False

app.register_blueprint(producto_bp, url_prefix="/api")
app.register_blueprint(usuario_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/api/auth")  # AA5-EV01: /api/auth/registro, /api/auth/login

# ─── DECORADOR: requiere login ───────────────────────────
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "usuario" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorada

# ─── DECORADOR: requiere ser admin ───────────────────────
def admin_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "usuario" not in session:
            return redirect("/login")
        if session["usuario"]["rol"] != "Admin":
            return redirect("/")
        return f(*args, **kwargs)
    return decorada

def domiciliario_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "usuario" not in session:
            return redirect("/login")
        if session["usuario"]["rol"] not in ("Admin", "Domiciliario"):
            return redirect("/")
        return f(*args, **kwargs)
    return decorada

# ─── LOGIN ───────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    mail_previo = ""
    if request.method == "POST":
        mail = request.form["mail"]
        password = request.form["password"]
        mail_previo = mail

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.*, r.Nom_Rol
                FROM USUARIO u
                LEFT JOIN ROLXUSUARIO ru ON u.NumDoc_Usuario = ru.NumDoc_Usuario
                LEFT JOIN ROL r ON ru.Cod_Rol = r.Cod_Rol
                WHERE u.Mail_Usuario = %s
            """, (mail,))
            usuario = cursor.fetchone()
            close_connection(conn)

            if usuario and check_password_hash(usuario["Password"], password):
                session["usuario"] = {
                    "num_doc": usuario["NumDoc_Usuario"],
                    "nombre": f"{usuario['Nom1_Usuario']} {usuario['Ape1_Usuario']}",
                    "mail": usuario["Mail_Usuario"],
                    "rol": usuario["Nom_Rol"] or "Cliente"
                }
                if usuario["Nom_Rol"] == "Admin":
                    return redirect("/admin")
                if usuario["Nom_Rol"] == "Domiciliario":
                    return redirect("/domiciliario")
                return redirect("/")
            else:
                error = "Correo o contraseña incorrectos"

    return render_template("login.html", error=error, mail_previo=mail_previo)

# ─── LOGOUT ──────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ─── ADMIN ───────────────────────────────────────────────
@app.route("/admin")
@admin_requerido
def admin():
    num_doc = session["usuario"]["num_doc"]
    usuario = Usuario.buscar(num_doc)
    return render_template("admin.html", usuario=usuario)

# ─── INICIO (TIENDA) ─────────────────────────────────────
@app.route("/")
def inicio():
    productos_db = Producto.listar()

    def get_emoji(nombre):
        nombre = nombre.lower()
        if any(x in nombre for x in ["tomate","cebolla","papa","zanahoria","aguacate","platano","mango"]): return "🥦"
        if any(x in nombre for x in ["leche","queso","yogurt","mantequilla"]): return "🥛"
        if any(x in nombre for x in ["pollo","carne","cerdo","res","chorizo"]): return "🥩"
        if any(x in nombre for x in ["gaseosa","jugo","agua","cerveza"]): return "🥤"
        if any(x in nombre for x in ["pan","arepa","pandebono","almojabana"]): return "🍞"
        if any(x in nombre for x in ["snack","choco","dulce","papas"]): return "🍿"
        if any(x in nombre for x in ["jabon","fabuloso","detergente","cloro"]): return "🧹"
        if any(x in nombre for x in ["shampoo","crema","desodorante"]): return "🧴"
        if any(x in nombre for x in ["cafe","coffee"]): return "☕"
        if any(x in nombre for x in ["lenteja","garbanzo","frijol","arveja","haba","soya"]): return "🫘"
        if any(x in nombre for x in ["avena","trigo","cebada","maiz","quinua","granola","arroz"]): return "🌾"
        return "📦"

    def get_cat(nombre):
        nombre = nombre.lower()
        if any(x in nombre for x in ["tomate","cebolla","papa","zanahoria","aguacate","platano","mango"]): return "frutas"
        if any(x in nombre for x in ["leche","queso","yogurt","mantequilla"]): return "lacteos"
        if any(x in nombre for x in ["pollo","carne","cerdo","res","chorizo"]): return "carnes"
        if any(x in nombre for x in ["gaseosa","jugo","agua","cerveza"]): return "bebidas"
        if any(x in nombre for x in ["pan","arepa","pandebono","almojabana"]): return "panaderia"
        if any(x in nombre for x in ["snack","choco","dulce","papas"]): return "snacks"
        if any(x in nombre for x in ["jabon","fabuloso","detergente","cloro"]): return "limpieza"
        # Marcas con prioridad sobre categoría genérica
        for marca in ["rexona","dove","head","pantene","gillette","oral-b","colgate","listerine"]:
            if marca in nombre: return "aseo"
        if any(x in nombre for x in ["shampoo","crema","desodorante"]): return "aseo"
        if any(x in nombre for x in ["lenteja","garbanzo","frijol","arveja","haba","soya"]): return "granos"
        if any(x in nombre for x in ["avena","trigo","cebada","maiz","quinua","granola","arroz"]): return "cereales"
        return "todos"

    # Mapa cat → emoji (fuente única de verdad)
    CAT_EMOJI = {
        "frutas":   "🥦", "carnes":   "🥩", "lacteos":  "🥛",
        "bebidas":  "🥤", "panaderia":"🍞", "snacks":   "🍿",
        "limpieza": "🧹", "aseo":     "🧴", "granos":   "🫘",
        "cereales": "🌾", "todos":    "📦",
    }

    # Obtener categoría de BD para cada producto
    from config.db import get_connection, close_connection as _cc
    cat_bd = {}
    try:
        _conn = get_connection()
        if _conn:
            _cur = _conn.cursor(dictionary=True)
            _cur.execute("""
                SELECT cp.Id_Producto, c.Nom_Categoria
                FROM   categoriaxproducto cp
                JOIN   categoria c ON cp.Id_Categoria = c.Id_Categoria
            """)
            CAT_MAP = {
                "Frutas y Verduras":"frutas","Carnes":"carnes",
                "Lácteos":"lacteos","Bebidas":"bebidas",
                "Panadería":"panaderia","Limpieza":"limpieza",
                "Aseo Personal":"aseo","Granos":"granos",
                "Cereales":"cereales","Snacks":"snacks"
            }
            for row in _cur.fetchall():
                cat_bd[row["Id_Producto"]] = CAT_MAP.get(
                    row["Nom_Categoria"], "todos")
            _cc(_conn)
    except Exception:
        pass

    productos_js = json.dumps([{
        "id":    p["Id_Producto"],
        "name":  p["Nom_Producto"],
        "desc":  p["Descripcion"] or "",
        "price": float(p["Vlr_Unitario"]),
        "emoji": CAT_EMOJI.get(cat_bd.get(p["Id_Producto"], get_cat(p["Nom_Producto"])), get_emoji(p["Nom_Producto"])),
        "cat":   cat_bd.get(p["Id_Producto"], get_cat(p["Nom_Producto"])),
        "unidad": "Kg" if cat_bd.get(p["Id_Producto"], get_cat(p["Nom_Producto"])) in ("frutas","carnes","granos","cereales") else "uds",
        "img":    p["Img_Producto"] if p.get("Img_Producto") else None,
        "oferta": p["Cant_Stock"] < 10
    } for p in productos_db], ensure_ascii=False)

    return render_template("index.html",
        productos_js=productos_js,
        usuario_session=session.get("usuario"))

# ─── PRODUCTOS ───────────────────────────────────────────
@app.route("/productos")
@admin_requerido
def vista_productos():
    productos = Producto.listar()

    # ── Leer categoría de cada producto DESDE LA BD ──────────────
    CAT_CONFIG = {
        "Frutas y Verduras": ("frutas",    "🥦", "Kg"),
        "Carnes":            ("carnes",    "🥩", "Kg"),
        "Lácteos":           ("lacteos",   "🥛", "uds"),
        "Bebidas":           ("bebidas",   "🥤", "uds"),
        "Panadería":         ("panaderia", "🍞", "uds"),
        "Limpieza":          ("limpieza",  "🧹", "uds"),
        "Aseo Personal":     ("aseo",      "🧴", "uds"),
        "Granos":            ("granos",    "🫘", "Kg"),
        "Cereales":          ("cereales",  "🌾", "Kg"),
        "Snacks":            ("snacks",    "🍿", "uds"),
    }

    # Consultar categoría y unidad de cada producto desde BD
    from config.db import get_connection, close_connection as _cc
    prod_cat   = {}   # {id_producto: key_cat}
    prod_unidad = {}  # {id_producto: "Kg"/"uds"}
    try:
        _conn = get_connection()
        if _conn:
            _cur = _conn.cursor(dictionary=True)
            _cur.execute("""
                SELECT cp.Id_Producto, c.Nom_Categoria
                FROM   categoriaxproducto cp
                JOIN   categoria c ON cp.Id_Categoria = c.Id_Categoria
            """)
            for row in _cur.fetchall():
                cfg = CAT_CONFIG.get(row["Nom_Categoria"])
                if cfg:
                    prod_cat[row["Id_Producto"]]    = cfg[0]
                    prod_unidad[row["Id_Producto"]] = cfg[2]
            _cc(_conn)
    except Exception:
        pass

    # ── Calcular totales por categoría ───────────────────────────
    totales = {key: {"icon":icon,"label":nom,"unidad":unidad,"total":0}
               for nom,(key,icon,unidad) in CAT_CONFIG.items()}
    totales["otros"] = {"icon":"📦","label":"Otros","unidad":"uds","total":0}

    for p in (productos or []):
        key = prod_cat.get(p["Id_Producto"], "otros")
        if key not in totales:
            key = "otros"
        totales[key]["total"] += int(float(str(p["Cant_Stock"] or 0)))

    stock_cats = [v for v in totales.values() if v["total"] > 0]

    return render_template("productos.html",
                           productos=productos,
                           stock_cats=stock_cats,
                           prod_unidad=prod_unidad)

@app.route("/productos/<int:id>")
@admin_requerido
def vista_producto_detalle(id):
    producto = Producto.buscar(id)
    if not producto:
        return "Producto no encontrado", 404
    return render_template("producto_detalle.html", producto=producto)

@app.route("/productos/nuevo", methods=["GET", "POST"])
@admin_requerido
def producto_nuevo():
    mensaje, exito = None, False
    if request.method == "POST":
        precio_limpio  = request.form["vlr_unitario"].replace(".", "").replace(",", "")
        imagen         = guardar_imagen(request.files.get("imagen"), UPLOAD_FOLDER_PRODUCTOS, "prod")
        ids_categorias = request.form.getlist("categorias")
        resultado = ProductoController.agregar_producto(
            request.form["nom"], request.form["descripcion"],
            precio_limpio, request.form["cant_stock"],
            request.form["fech_vencimiento"], request.form["iva"],
            imagen, ids_categorias or None)
        mensaje = resultado["msg"]
        exito   = resultado["ok"]
    categorias = Categoria.listar()
    return render_template("producto_form.html",
        titulo="Agregar Producto",
        subtitulo="Completa los datos del nuevo producto",
        producto=None, mensaje=mensaje, exito=exito,
        categorias=categorias, cats_producto=[])

@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
@admin_requerido
def producto_editar(id):
    producto = Producto.buscar(id)
    mensaje, exito = None, False
    if request.method == "POST":
        precio_limpio  = request.form["vlr_unitario"].replace(".", "").replace(",", "")
        imagen         = guardar_imagen(request.files.get("imagen"), UPLOAD_FOLDER_PRODUCTOS, f"prod_{id}")
        ids_categorias = request.form.getlist("categorias")
        resultado = ProductoController.editar_producto(
            id, request.form["nom"], request.form["descripcion"],
            precio_limpio, request.form["cant_stock"],
            request.form["fech_vencimiento"], request.form["iva"],
            imagen, ids_categorias or None)
        mensaje = resultado["msg"]
        exito   = resultado["ok"]
        producto = Producto.buscar(id)
    categorias    = Categoria.listar()
    cats_producto = Categoria.categorias_de_producto(id) if producto else []
    cats_ids      = [str(c["Id_Categoria"]) for c in cats_producto]
    return render_template("producto_form.html",
        titulo="Editar Producto",
        subtitulo="Modifica los datos del producto",
        producto=producto, mensaje=mensaje, exito=exito,
        categorias=categorias, cats_producto=cats_ids)

@app.route("/productos/eliminar/<int:id>", methods=["GET", "POST"])
@admin_requerido
def producto_eliminar(id):
    producto = Producto.buscar(id)
    if request.method == "POST":
        # Borrar imagen física antes de eliminar el registro
        if producto and producto.get("Img_Producto"):
            ruta_img = os.path.join(UPLOAD_FOLDER_PRODUCTOS, producto["Img_Producto"])
            if os.path.exists(ruta_img):
                os.remove(ruta_img)
                print(f"🗑️ Imagen eliminada: {ruta_img}")
        ProductoController.eliminar_producto(id)
        return redirect("/productos")
    return render_template("producto_eliminar.html", producto=producto)

# ─── USUARIOS ────────────────────────────────────────────
@app.route("/usuarios")
@admin_requerido
def vista_usuarios():
    usuarios = Usuario.listar()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/usuarios/<num_doc>")
@admin_requerido
def vista_usuario_detalle(num_doc):
    usuario = Usuario.buscar(num_doc)
    if not usuario:
        return "Usuario no encontrado", 404
    return render_template("usuario_detalle.html", usuario=usuario)

@app.route("/usuarios/nuevo", methods=["GET", "POST"])
@admin_requerido
def usuario_nuevo():
    mensaje, exito = None, False
    if request.method == "POST":
        password        = request.form["password"]
        password_confirm = request.form["password_confirm"]
        if password != password_confirm:
            mensaje = "Las contraseñas no coinciden"
            exito   = False
        else:
            foto = guardar_imagen(
                request.files.get("foto"),
                UPLOAD_FOLDER_USUARIOS,
                f"usr_{request.form['num_doc']}")
            id_rol    = request.form.get("rol", "2")
            resultado = UsuarioController.registrar_usuario(
                request.form["num_doc"], request.form["tipo_doc"],
                request.form["nom1"],    request.form.get("nom2",""),
                request.form["ape1"],    request.form.get("ape2",""),
                request.form.get("indicativo","+57"),
                request.form["tel"],  request.form["mail"],
                password, foto, id_rol)
            mensaje = resultado["msg"]
            exito   = resultado["ok"]
    return render_template("usuario_form.html",
        titulo="Registrar Usuario",
        subtitulo="Completa los datos del nuevo usuario",
        usuario=None, mensaje=mensaje, exito=exito)

@app.route("/usuarios/editar/<num_doc>", methods=["GET", "POST"])
@admin_requerido
def usuario_editar(num_doc):
    usuario = Usuario.buscar(num_doc)
    if not usuario:
        return redirect("/usuarios")
    if request.method == "POST":
        foto = guardar_imagen(request.files.get("foto"), UPLOAD_FOLDER_USUARIOS, f"usr_{num_doc}")
        resultado = UsuarioController.editar_usuario(
            num_doc, request.form["nom1"], request.form.get("nom2",""),
            request.form["ape1"], request.form.get("ape2",""),
            request.form.get("indicativo","+57"),
            request.form["tel"], request.form["mail"],
            request.form.get("nueva_password", ""),
            request.form.get("confirmar_password", ""), foto)
        if resultado["ok"]:
            return redirect(f"/usuarios/{num_doc}?msg=editado")
        return render_template("usuario_form.html",
            titulo="Editar Usuario",
            subtitulo="Modifica los datos del usuario",
            usuario=usuario, mensaje=resultado["msg"], exito=False)
    return render_template("usuario_form.html",
        titulo="Editar Usuario",
        subtitulo="Modifica los datos del usuario",
        usuario=usuario, mensaje=None, exito=False)

@app.route("/usuarios/eliminar/<num_doc>", methods=["GET", "POST"])
@admin_requerido
def usuario_eliminar(num_doc):
    usuario = Usuario.buscar(num_doc)
    if request.method == "POST":
        # Borrar foto física antes de eliminar el registro
        if usuario and usuario.get("Foto_Usuario"):
            ruta_foto = os.path.join(UPLOAD_FOLDER_USUARIOS, usuario["Foto_Usuario"])
            if os.path.exists(ruta_foto):
                os.remove(ruta_foto)
                print(f"🗑️ Foto eliminada: {ruta_foto}")
        UsuarioController.eliminar_usuario(num_doc)
        return redirect("/usuarios")
    return render_template("usuario_eliminar.html", usuario=usuario)

# ─── VENTAS ──────────────────────────────────────────────────────────────────

@app.route("/ventas/crear", methods=["POST"])
def venta_crear():
    """Recibe JSON del carrito y crea la venta en BD"""
    from flask import jsonify
    usuario = session.get("usuario")
    if not usuario:
        return jsonify({"ok": False,
                        "msg": "Debes iniciar sesión para confirmar el pedido"})
    try:
        data          = request.get_json(force=True, silent=True) or {}
        items         = data.get("items", [])
        direccion     = data.get("direccion", "")
        observaciones = data.get("observaciones", "")
        metodo_pago   = data.get("metodo_pago", "Efectivo")
        tipo_entrega  = data.get("tipo_entrega", "envio")
        id_qr         = data.get("id_qr", None)
        # Normalizar valor del frontend
        tipo_entrega_bd = "Punto de venta" if tipo_entrega == "punto" else "Envio"

        if not items:
            return jsonify({"ok": False, "msg": "El carrito está vacío"})

        resultado = VentaController.crear_venta(
            usuario["num_doc"], items, direccion,
            observaciones, metodo_pago, tipo_entrega_bd, id_qr)

        # Serializar de forma segura (convertir Decimal, int64, etc.)
        return jsonify({
            "ok":       bool(resultado.get("ok", False)),
            "msg":      str(resultado.get("msg", "")),
            "id_venta": int(resultado["id_venta"]) if resultado.get("id_venta") else None,
            "total":    float(resultado["total"])  if resultado.get("total")    else 0.0
        })
    except Exception as e:
        print(f"❌ venta_crear error: {e}")
        import traceback; traceback.print_exc()
        return jsonify({"ok": False, "msg": f"Error interno: {str(e)}"})

# ─── CONFIGURACIÓN / QR MÚLTIPLES ───────────────────────────────────────────

def _qr_db():
    """Retorna lista de QRs activos desde la BD"""
    from config.db import get_connection, close_connection as _cc
    try:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM qr_pago ORDER BY Id_QR DESC")
        qrs  = cur.fetchall()
        _cc(conn)
        return qrs
    except Exception:
        return []

@app.route("/config/qr")
def get_qr():
    """Devuelve lista de QRs activos para el modal del carrito"""
    from flask import jsonify
    qrs = [q for q in _qr_db() if q.get("Activo")]
    datos = [{"id":     q["Id_QR"],
              "banco":  q["Banco"],
              "cuenta": q["Num_Cuenta"],
              "titular":q.get("Titular",""),
              "img":    f"/static/img/qr/{q['Img_QR']}"}
             for q in qrs]
    return jsonify({"qrs": datos})

@app.route("/admin/config", methods=["GET","POST"])
@admin_requerido
def admin_config():
    """Gestión de múltiples QR de pago"""
    from config.db import get_connection, close_connection as _cc
    mensaje, exito = None, False

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "agregar":
            banco      = request.form.get("banco","").strip()
            num_cuenta = request.form.get("num_cuenta","").strip()
            titular    = request.form.get("titular","").strip()
            archivo_qr = request.files.get("img_qr")
            if not banco or not num_cuenta:
                mensaje = "Banco y número de cuenta son obligatorios"
            elif not archivo_qr or not allowed_file(archivo_qr.filename):
                mensaje = "Selecciona una imagen QR válida (JPG, PNG, WEBP)"
            else:
                import uuid
                ext      = archivo_qr.filename.rsplit(".",1)[1].lower()
                nombre   = f"qr_{uuid.uuid4().hex[:8]}.{ext}"
                os.makedirs("static/img/qr", exist_ok=True)
                archivo_qr.save(os.path.join("static","img","qr", nombre))
                try:
                    conn = get_connection()
                    cur  = conn.cursor()
                    cur.execute("""INSERT INTO qr_pago
                                   (Banco,Num_Cuenta,Titular,Img_QR)
                                   VALUES (%s,%s,%s,%s)""",
                                (banco, num_cuenta, titular or None, nombre))
                    conn.commit()
                    _cc(conn)
                    mensaje = f"QR de {banco} agregado correctamente"
                    exito   = True
                except Exception as e:
                    mensaje = f"Error al guardar: {str(e)}"

        elif accion == "eliminar":
            id_qr = request.form.get("id_qr")
            try:
                conn = get_connection()
                cur  = conn.cursor(dictionary=True)
                cur.execute("SELECT Img_QR FROM qr_pago WHERE Id_QR=%s",(id_qr,))
                row = cur.fetchone()
                if row:
                    ruta_img = os.path.join("static","img","qr", row["Img_QR"])
                    if os.path.exists(ruta_img):
                        os.remove(ruta_img)
                cur.execute("DELETE FROM qr_pago WHERE Id_QR=%s",(id_qr,))
                conn.commit()
                _cc(conn)
                mensaje = "QR eliminado"
                exito   = True
            except Exception as e:
                mensaje = f"Error: {str(e)}"

    qrs = _qr_db()
    return render_template("admin_config.html",
                           qrs=qrs,
                           mensaje=mensaje, exito=exito,
                           usuario_session=session.get("usuario"))

# ─── PANEL DOMICILIARIO ──────────────────────────────────────────────────────

@app.route("/domiciliario")
@domiciliario_requerido
def panel_domiciliario():
    """Panel del domiciliario: pedidos pendientes de entrega (Envío)"""
    from config.db import get_connection, close_connection as _cc
    try:
        conn = get_connection()
        cur  = conn.cursor(dictionary=True)
        # Pedidos de envío que no están entregados ni cancelados
        cur.execute("""
            SELECT v.*, u.Nom1_Usuario, u.Ape1_Usuario,
                   u.Tel_Usuario, u.Indicativo_Usuario
            FROM   venta v
            JOIN   usuario u ON v.NumDoc_Usuario = u.NumDoc_Usuario
            WHERE  v.Tipo_Entrega = 'Envio'
              AND  v.Estado_Venta NOT IN ('Entregado','Cancelado')
            ORDER  BY v.Fech_Venta ASC
        """)
        pendientes = cur.fetchall()
        # Pedidos entregados hoy por este domiciliario (historial del día)
        cur.execute("""
            SELECT v.*, u.Nom1_Usuario, u.Ape1_Usuario
            FROM   venta v
            JOIN   usuario u ON v.NumDoc_Usuario = u.NumDoc_Usuario
            WHERE  v.Tipo_Entrega   = 'Envio'
              AND  v.Estado_Venta   = 'Entregado'
              AND  DATE(v.Fech_Venta) = CURDATE()
            ORDER  BY v.Fech_Venta DESC
        """)
        entregados_hoy = cur.fetchall()
        _cc(conn)
    except Exception as e:
        print(f"❌ panel_domiciliario: {e}")
        pendientes = []
        entregados_hoy = []
    return render_template("panel_domiciliario.html",
                           pendientes=pendientes,
                           entregados_hoy=entregados_hoy,
                           usuario_session=session.get("usuario"))

@app.route("/domiciliario/entregar/<int:id_venta>", methods=["POST"])
@domiciliario_requerido
def domiciliario_entregar(id_venta):
    """Confirmar entrega y método de pago cobrado"""
    metodo_cobro = request.form.get("metodo_cobro", "Efectivo")
    from config.db import get_connection, close_connection as _cc
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            UPDATE venta
            SET Estado_Venta = 'Entregado',
                Metodo_Pago  = %s
            WHERE Id_Venta = %s
              AND Tipo_Entrega = 'Envio'
        """, (metodo_cobro, id_venta))
        conn.commit()
        _cc(conn)
    except Exception as e:
        print(f"❌ domiciliario_entregar: {e}")
    return redirect("/domiciliario")

# Alias: /pedidos redirige a /ventas para compatibilidad
@app.route("/pedidos")
@admin_requerido
def vista_pedidos_alias():
    return redirect("/ventas")

@app.route("/ventas")
@admin_requerido
def vista_ventas():
    try:
        ventas = Venta.listar() or []
    except Exception as e:
        print(f"❌ Error listando ventas: {e}")
        ventas = []
    return render_template("pedidos.html",
                           pedidos=ventas,
                           usuario_session=session.get("usuario"))

@app.route("/ventas/<int:id_venta>")
@admin_requerido
def venta_detalle(id_venta):
    venta = Venta.buscar(id_venta)
    items = Venta.detalle(id_venta) or []
    return render_template("pedido_detalle.html",
                           pedido=venta, items=items,
                           usuario_session=session.get("usuario"))

@app.route("/ventas/<int:id_venta>/estado", methods=["POST"])
@admin_requerido
def venta_estado(id_venta):
    nuevo_estado = request.form.get("estado")
    resultado    = VentaController.cambiar_estado(id_venta, nuevo_estado)
    return redirect(f"/ventas/{id_venta}?msg={resultado['msg']}")

@app.route("/mis-pedidos")
def mis_pedidos():
    usuario = session.get("usuario")
    if not usuario:
        return redirect("/login")
    ventas = Venta.por_cliente(usuario["num_doc"])
    return render_template("mis_pedidos.html", pedidos=ventas,
                           usuario_session=usuario)

@app.route("/mis-pedidos/<int:id_venta>")
def mi_pedido_detalle(id_venta):
    usuario = session.get("usuario")
    if not usuario:
        return redirect("/login")
    venta = Venta.buscar(id_venta)
    if not venta or venta["NumDoc_Usuario"] != usuario["num_doc"]:
        return redirect("/mis-pedidos")
    items = Venta.detalle(id_venta)
    return render_template("pedido_detalle.html",
                           pedido=venta, items=items,
                           usuario_session=usuario)

@app.route("/test-db")
def test_db():
    conn = get_connection()
    if conn:
        close_connection(conn)
        return "✅ Conexión a TIENDALOSBOYACOS exitosa"
    return "❌ Error al conectar"

if __name__ == "__main__":
    app.run(debug=True)