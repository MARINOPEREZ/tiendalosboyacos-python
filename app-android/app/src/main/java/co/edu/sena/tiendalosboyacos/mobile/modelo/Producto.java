package co.edu.sena.tiendalosboyacos.mobile.modelo;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Representa un registro de la tabla PRODUCTO (ver LOSBOYACOS.kkd).
 * Los nombres de los campos del backend (Flask/MariaDB) se respetan
 * tal cual para evitar el desajuste de nombres ya documentado en el
 * proyecto (Vlr_Unitario, no Precio_Unitario; Cant_Stock, no Stock).
 */
public class Producto {

    public final int idProducto;
    public final String nombre;
    public final String descripcion;
    public final double valorUnitario;
    public final int cantidadStock;
    public final double iva;
    public final String imagen;
    public final boolean activo;

    public Producto(int idProducto, String nombre, String descripcion,
                     double valorUnitario, int cantidadStock, double iva,
                     String imagen, boolean activo) {
        this.idProducto = idProducto;
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.valorUnitario = valorUnitario;
        this.cantidadStock = cantidadStock;
        this.iva = iva;
        this.imagen = imagen;
        this.activo = activo;
    }

    /**
     * Construye un Producto a partir del JSON que devuelven
     * GET /api/productos y GET /api/productos/{id} (campo "data").
     * Tolerante a campos opcionales ausentes (Descripcion, Img_Producto
     * pueden ser NULL en la base de datos).
     */
    public static Producto desdeJson(JSONObject json) throws JSONException {
        return new Producto(
                json.getInt("Id_Producto"),
                json.optString("Nom_Producto", ""),
                json.optString("Descripcion", ""),
                json.optDouble("Vlr_Unitario", 0.0),
                json.optInt("Cant_Stock", 0),
                json.optDouble("IVA", 0.0),
                json.isNull("Img_Producto") ? null : json.optString("Img_Producto", null),
                json.optInt("Activo", 1) == 1
        );
    }
}
