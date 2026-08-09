-- =====================================================================
-- Migración: corrección de problemas de esquema — Tienda Los Boyacos
-- Fecha: 2026-08-09
-- Base de datos: tiendalosboyacos (MariaDB)
--
-- Corrige los hallazgos pendientes documentados en el informe de
-- estado del proyecto: tablas intermedias sin llaves foráneas
-- explícitas, FKs faltantes en DETALLE y VENTA, CUENTA sin campo de
-- contraseña, uso de CHAR en vez de VARCHAR y nulabilidad
-- inconsistente en nombres de USUARIO.
--
-- CÓMO EJECUTAR:
--   1. Haz un respaldo primero: mysqldump -u root tiendalosboyacos > respaldo_2026_08_09.sql
--   2. Ejecuta este archivo completo en phpMyAdmin (pestaña SQL) o con:
--        mysql -u root tiendalosboyacos < migraciones/2026_08_09_fix_esquema.sql
--   3. Revisa los mensajes de error de cada sección: si alguna tabla ya
--      tiene una columna o índice con el mismo nombre, esa sentencia
--      puntual fallará mientras el resto de la migración continúa.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. ROLXUSUARIO — tabla intermedia sin llaves foráneas explícitas
--    Actualmente solo tiene su propio Cod_RolUsuario (SERIAL): no
--    puede representar ninguna relación Rol<->Usuario tal como está.
-- ---------------------------------------------------------------------
ALTER TABLE ROLXUSUARIO
    ADD COLUMN Cod_Rol CHAR(10) NOT NULL AFTER Cod_RolUsuario,
    ADD COLUMN NumDoc_Usuario CHAR(15) NOT NULL AFTER Cod_Rol;

ALTER TABLE ROLXUSUARIO
    ADD CONSTRAINT fk_rolxusuario_rol
        FOREIGN KEY (Cod_Rol) REFERENCES ROL(Cod_Rol)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_rolxusuario_usuario
        FOREIGN KEY (NumDoc_Usuario) REFERENCES USUARIO(NumDoc_Usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT;

-- Evita duplicar el mismo rol para el mismo usuario
ALTER TABLE ROLXUSUARIO
    ADD CONSTRAINT uq_rolxusuario UNIQUE (Cod_Rol, NumDoc_Usuario);


-- ---------------------------------------------------------------------
-- 2. CATEGORIAXPRODUCTO — mismo problema: sin FKs a CATEGORIA/PRODUCTO
-- ---------------------------------------------------------------------
ALTER TABLE CATEGORIAXPRODUCTO
    ADD COLUMN Id_Categoria CHAR(15) NOT NULL AFTER Cod_CategoriaProducto,
    ADD COLUMN Id_Producto CHAR(30) NOT NULL AFTER Id_Categoria;

ALTER TABLE CATEGORIAXPRODUCTO
    ADD CONSTRAINT fk_categoriaxproducto_categoria
        FOREIGN KEY (Id_Categoria) REFERENCES CATEGORIA(Id_Categoria)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    ADD CONSTRAINT fk_categoriaxproducto_producto
        FOREIGN KEY (Id_Producto) REFERENCES PRODUCTO(Id_Producto)
        ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE CATEGORIAXPRODUCTO
    ADD CONSTRAINT uq_categoriaxproducto UNIQUE (Id_Categoria, Id_Producto);


-- ---------------------------------------------------------------------
-- 3. DETALLE — sin FK a VENTA ni a PRODUCTO (no se puede saber a qué
--    venta ni a qué producto corresponde cada línea de detalle)
-- ---------------------------------------------------------------------
ALTER TABLE DETALLE
    ADD COLUMN Id_Venta CHAR(30) NOT NULL AFTER Id_Detalle,
    ADD COLUMN Id_Producto CHAR(30) NOT NULL AFTER Id_Venta;

ALTER TABLE DETALLE
    ADD CONSTRAINT fk_detalle_venta
        FOREIGN KEY (Id_Venta) REFERENCES VENTA(Id_Venta)
        ON UPDATE CASCADE ON DELETE CASCADE,
    ADD CONSTRAINT fk_detalle_producto
        FOREIGN KEY (Id_Producto) REFERENCES PRODUCTO(Id_Producto)
        ON UPDATE CASCADE ON DELETE RESTRICT;


-- ---------------------------------------------------------------------
-- 4. VENTA — sin FK a USUARIO (no se puede saber quién hizo la venta)
-- ---------------------------------------------------------------------
ALTER TABLE VENTA
    ADD COLUMN NumDoc_Usuario CHAR(15) NOT NULL AFTER Id_Venta;

ALTER TABLE VENTA
    ADD CONSTRAINT fk_venta_usuario
        FOREIGN KEY (NumDoc_Usuario) REFERENCES USUARIO(NumDoc_Usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT;


-- ---------------------------------------------------------------------
-- 5. CUENTA — sin campo de contraseña, y sin FK explícita a USUARIO
--    (el modelo relaciona USUARIO 1---N CUENTA)
-- ---------------------------------------------------------------------
ALTER TABLE CUENTA
    ADD COLUMN NumDoc_Usuario CHAR(15) NOT NULL AFTER Cod_Cuenta,
    ADD COLUMN Password VARCHAR(255) NOT NULL AFTER Nom_Cuenta;

ALTER TABLE CUENTA
    ADD CONSTRAINT fk_cuenta_usuario
        FOREIGN KEY (NumDoc_Usuario) REFERENCES USUARIO(NumDoc_Usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT;


-- ---------------------------------------------------------------------
-- 6. CHAR -> VARCHAR en columnas de texto de longitud variable
--    (CHAR reserva espacio fijo y rellena con espacios; los nombres,
--    descripciones y direcciones varían mucho en longitud real)
-- ---------------------------------------------------------------------
ALTER TABLE USUARIO
    MODIFY COLUMN TipoDoc_Usuario   VARCHAR(10),
    MODIFY COLUMN Nom1_Usuario      VARCHAR(15),
    MODIFY COLUMN Nom2_Usuario      VARCHAR(15),
    MODIFY COLUMN Ape1_Usuario      VARCHAR(15),
    MODIFY COLUMN Ape2_Usuario      VARCHAR(15),
    MODIFY COLUMN Indicativo_Usuario VARCHAR(10),
    MODIFY COLUMN Tel_Usuario       VARCHAR(15),
    MODIFY COLUMN Mail_Usuario      VARCHAR(30);

ALTER TABLE PRODUCTO
    MODIFY COLUMN Nom_Producto  VARCHAR(30),
    MODIFY COLUMN Descripcion   VARCHAR(100);   -- 30 caracteres es muy poco para una descripción real

ALTER TABLE VENTA
    MODIFY COLUMN Direccion     VARCHAR(255),
    MODIFY COLUMN Observaciones VARCHAR(500);

ALTER TABLE CATEGORIA
    MODIFY COLUMN Nom_Categoria VARCHAR(30);

ALTER TABLE CUENTA
    MODIFY COLUMN Nom_Cuenta VARCHAR(50);

ALTER TABLE QR_PAGO
    MODIFY COLUMN Banco   VARCHAR(100),
    MODIFY COLUMN Titular VARCHAR(100);


-- ---------------------------------------------------------------------
-- 7. Nulabilidad inconsistente en USUARIO
--    Estado actual (invertido / inconsistente):
--      Nom1_Usuario  permite NULL   <- debería ser obligatorio
--      Nom2_Usuario  NOT NULL       <- el segundo nombre SÍ debería ser opcional
--      Ape1_Usuario  permite NULL   <- debería ser obligatorio
--      Ape2_Usuario  NOT NULL       <- el segundo apellido SÍ debería ser opcional
-- ---------------------------------------------------------------------
ALTER TABLE USUARIO
    MODIFY COLUMN Nom1_Usuario VARCHAR(15) NOT NULL,
    MODIFY COLUMN Nom2_Usuario VARCHAR(15) NULL,
    MODIFY COLUMN Ape1_Usuario VARCHAR(15) NOT NULL,
    MODIFY COLUMN Ape2_Usuario VARCHAR(15) NULL;


-- ---------------------------------------------------------------------
-- 8. Redundancia PRODUCTO.Cant_Stock vs. INVENTARIO
--    NO se resuelve automáticamente en esta migración porque implica
--    una decisión de diseño y puede romper código que ya lee
--    Cant_Stock directamente. Elegir una opción y aplicarla aparte:
--
--    Opción A (recomendada): PRODUCTO.Cant_Stock pasa a ser una
--      columna calculada/cache que se actualiza cada vez que se
--      inserta un registro en INVENTARIO; INVENTARIO queda como la
--      fuente de verdad del historial de movimientos de stock.
--
--    Opción B: eliminar INVENTARIO y manejar el stock únicamente en
--      PRODUCTO.Cant_Stock, perdiendo el historial de movimientos.
--
--    Opción A es la que preserva más información; requiere ajustar
--    src/controllers/producto_ctrl.py para que cada movimiento de
--    inventario también actualice PRODUCTO.Cant_Stock en la misma
--    transacción.
-- ---------------------------------------------------------------------
