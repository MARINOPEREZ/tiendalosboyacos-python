# VERIFICACIÓN DEL ESTADO REAL — TIENDA LOS BOYACOS
### Contraste entre `INFORME_CONTEXTO_PROYECTO_PARA_COWORK.md` y el sistema de archivos real (2026-09-13)

Verificado directamente sobre `C:\xampp\htdocs\PROYECTOS\tiendalosboyacos-python` con acceso al sistema de archivos y al repositorio Git local. **No fue posible conectar a MariaDB en vivo** desde este entorno (la VM Linux usada para la verificación no tiene cliente `mysql` instalado ni red hacia el servicio de Windows/XAMPP), así que el estado de la base de datos se infiere del propio código y de los archivos de migración, no de una consulta directa a `information_schema`.

---

## 1. RESUMEN EJECUTIVO

El proyecto está en buen estado y bastante más avanzado de lo que el informe sugiere en su sección de pendientes. Los puntos marcados como "por confirmar" en el informe (§8, §9) ya están resueltos y documentados en el propio repositorio. Se encontraron algunas discrepancias menores de nomenclatura, una capa de código no documentada en el informe, y un archivo de pruebas desactualizado. No se encontró ningún residuo de `PEDIDO`/`DETALLE_PEDIDO` ni mezcla con la evidencia de React descartada — ambos puntos quedaron limpios.

---

## 2. ESTRUCTURA DE ARCHIVOS

### 2.1 Coincide con lo documentado
- `app.py`, `config/db.py`, `src/models/{producto,usuario,venta,categoria}.py`, `src/controllers/{producto_ctrl,usuario_ctrl,venta_ctrl}.py`, `src/services/api_auth.py`.
- Las 16 plantillas Jinja2 descritas existen tal cual (el informe dice "17 vistas"; solo son 16, incluyendo `panel_domiciliario.html`, que sí está correctamente ubicado — el `TemplateNotFound` de la sesión anterior quedó resuelto).
- `static/img/{productos,usuarios,qr,default}` con los SVG por defecto.

### 2.2 Diferencias encontradas

| Elemento | Informe dice | Estado real |
|---|---|---|
| Carpeta de seed | `seeds/seed_roles.py` | La carpeta se llama **`seed/`** (singular), no `seeds/`. El propio `LEAME.txt` también tiene este desajuste. |
| Capa de rutas API | No se menciona en absoluto | Existe **`src/routes/`** (`producto_routes.py`, `usuario_routes.py`) con Blueprints Flask **registrados en `app.py`** bajo `/api` — ver sección 3. |
| Carpetas adicionales | No mencionadas | `public/assets/`, `logs/`, `tmp/` (vacías) y `tests/test_modelos.py` existen y no están en el informe ni en `LEAME.txt`. |
| `src/api/` (evidencia AA5-EV03) | Se documenta como entregada aparte, "aún no integrada" | **Confirmado: no existe en este repositorio.** Coincide con lo que el propio informe ya advertía — es evidencia en ZIP separado, no parte de este proyecto. |

---

## 3. HALLAZGO PRINCIPAL: capa REST no documentada en `src/routes/`

`app.py` importa y registra tres blueprints:

```python
app.register_blueprint(producto_bp, url_prefix="/api")
app.register_blueprint(usuario_bp, url_prefix="/api")
app.register_blueprint(auth_bp,    url_prefix="/api/auth")
```

- **`producto_bp`** (`src/routes/producto_routes.py`): `GET /api/productos`, `GET /api/productos/<id>`, `POST /api/productos/agregar`, `PUT /api/productos/editar/<id>`, `DELETE /api/productos/eliminar/<id>` — CRUD completo, reutiliza `ProductoController`.
- **`usuario_bp`** (`src/routes/usuario_routes.py`): `GET /api/usuarios`, `GET /api/usuarios/<num_doc>`, `POST /api/usuarios/registrar`.
- **`auth_bp`** = `src/services/api_auth.py` (AA5-EV01), bajo `/api/auth/registro` y `/api/auth/login`, con los mensajes exactos "Autenticación satisfactoria" / "Error en la autenticación".

El informe (§5) solo menciona *"GET /api/productos, GET /api/categorias (creados para una evidencia de React descartada)"*. La realidad es más completa: hay CRUD real de productos y un endpoint de registro/listado de usuarios, ya integrados y funcionando en `app.py`. **No existe** un endpoint `/api/categorias`. Vale la pena decidir si esta capa se documenta formalmente como parte de otra evidencia (se parece a lo que pedía AA5-EV03, pero implementada de forma distinta y más simple que los 16 endpoints/4 blueprints que describe esa evidencia en `src/api/`).

---

## 4. RESIDUOS Y LIMPIEZA (§ del informe que preguntaba por esto)

- **`PEDIDO`/`DETALLE_PEDIDO`**: no se encontró ninguna referencia en código SQL, Python ni HTML. El historial de Git lo confirma: commit `929501f — chore: eliminar codigo muerto de PEDIDO y corregir migracion obsoleta`. Punto cerrado.
- **Evidencia de React (`AA4-EV03`, proyecto Vite)**: no hay ningún archivo ni carpeta relacionada mezclada con `tiendalosboyacos-python`. Tampoco se encontró en el nivel superior de la carpeta de proyectos. Punto cerrado.

---

## 5. MIGRACIONES SQL — mucho más resuelto de lo que el informe indica

El informe (§8) lista 13 migraciones individuales (`migracion_indicativo.sql`, `migracion_imagenes.sql`, etc.) y pide confirmar cuáles se aplicaron. **Ninguno de esos 13 archivos existe** en el repositorio real. En su lugar hay un único archivo consolidado:

`migraciones/2026_08_09_fix_esquema.sql`

Este archivo trae en su propio encabezado un estado verificado el **2026-09-04 contra la BD real vía `information_schema`**:

- Secciones 1–4 (FKs de `rolxusuario`, `categoriaxproducto`, `detalle`, `venta`): **ya aplicadas**.
- Sección 6 (CHAR → VARCHAR/TEXT): **ya aplicada**.
- Sección 7 (nulabilidad de nombres/apellidos en `usuario`): **ya aplicada**.
- Sección 5 (FK de `cuenta` a `usuario`): aplicada, pero **obsoleta en el diseño de `Password`** — terminó viviendo en `usuario`, no en `cuenta` (coincide con lo que hace `seed/seed_roles.py` y con lo que lee `app.py`/`api_auth.py` en el login).
- **Sección 8 — pendiente real, sin resolver**: la redundancia entre `producto.Cant_Stock` e `inventario` sigue abierta. El propio archivo recomienda la Opción A (que `Cant_Stock` sea una caché actualizada en cada movimiento de `inventario`, dejando a `inventario` como fuente de verdad) y señala que requeriría tocar `src/controllers/producto_ctrl.py`.

Es decir: de todos los pendientes que el informe marcaba como "no confirmados", **el único que sigue realmente abierto es la redundancia de stock**. No se pudo verificar esto contra la BD en vivo desde este entorno, pero el propio archivo de migración ya lo documenta con fecha de verificación reciente (2026-09-04), así que es razonable confiar en esa nota salvo que se quiera reconfirmar manualmente en phpMyAdmin.

---

## 6. `requirements.txt`

El informe (§9) esperaba una versión **sin** `cffi`/`cryptography` explícitos por conflicto de compilación en Windows. El archivo real **sí los incluye explícitamente**:

```
cryptography==45.0.5
cffi==1.17.1
```

junto con `Flask==3.1.3`, `Werkzeug==3.1.8`, `Jinja2==3.1.6`, `mysql-connector-python==9.6.0`, `reportlab==4.4.1`, `pypdf==5.4.0`, etc. Si en su momento hubo un conflicto de compilación en Windows con estas dos, ya no está reflejado en el archivo actual — parece resuelto o nunca llegó a bloquear la instalación final.

---

## 7. HALLAZGO SUELTO: `tests/test_modelos.py` desactualizado

Este archivo no está documentado en el informe, pero existe y **está roto** frente al código actual:

```python
Usuario.registrar("123456", "CC", "Juan", "Carlos",
                   "Pérez", "García", "3001234567",
                   "juan@email.com")
```

La firma real de `Usuario.registrar` en `src/models/usuario.py` es:

```python
def registrar(num_doc, tipo_doc, nom1, nom2,
              ape1, ape2, indicativo, tel, mail,
              password, foto=None, id_rol="2"):
```

El test le pasa 8 argumentos posicionales cuando la función exige al menos 10 (`indicativo`, `tel`, `mail` y `password` no tienen valor por defecto) — al ejecutarlo hoy lanzaría `TypeError` por argumentos faltantes. Si este archivo se sigue usando como prueba manual, necesita actualizarse.

---

## 8. GIT

- 6 commits en `main`, historial limpio y coherente con lo narrado en el informe (incluye el commit de limpieza de `PEDIDO` y el de `AA5-EV01`).
- Árbol de trabajo limpio, salvo `REPOSITORIO.txt` (nuevo, sin trackear — documenta la evidencia AA5-EV01 y aún no se ha hecho `git add`).
- Remoto: `https://github.com/MARINOPEREZ/tiendalosboyacos-python.git`, rama `main` al día con `origin/main`.

---

## 9. PRÓXIMOS PASOS SUGERIDOS

1. Decidir si `REPOSITORIO.txt` se agrega al repo (`git add` + commit) o se deja fuera de control de versiones.
2. Documentar formalmente la capa `src/routes/` (producto/usuario) en el informe o en `LEAME.txt`, ya que existe, funciona y no está descrita en ningún lado.
3. Arreglar o eliminar `tests/test_modelos.py` para que refleje la firma actual de `Usuario.registrar`.
4. Resolver la redundancia `producto.Cant_Stock` vs `inventario` (Sección 8 de la migración) — es el único pendiente técnico real que queda abierto.
5. Si se quiere una confirmación 100% en vivo del esquema de la base de datos, se necesitaría acceso directo a MariaDB (por ejemplo, activando el uso del computador/phpMyAdmin en esta sesión, o instalando un cliente `mysql` accesible desde aquí) — desde este entorno solo se pudo verificar por inspección de código y del archivo de migración.
6. Unificar el nombre de la carpeta de seed (`seed/` real vs `seeds/` en el informe y en `LEAME.txt`) para evitar confusiones futuras.
