package co.edu.sena.tiendalosboyacos.mobile.datos;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

import co.edu.sena.tiendalosboyacos.mobile.modelo.Categoria;
import co.edu.sena.tiendalosboyacos.mobile.modelo.Producto;

/**
 * Capa de acceso a datos del catálogo: traduce las respuestas JSON de
 * /api/productos* a objetos de dominio (Producto, Categoria) y filtra
 * lo que a la UI no le corresponde decidir (p. ej. productos inactivos).
 *
 * Patron de diseño: Repository.
 */
public class ProductoRepository {

    public void listar(final Callback<List<Producto>> callback) {
        ApiClient.getInstancia().get("productos", new Callback<JSONObject>() {
            @Override
            public void onExito(JSONObject respuesta) {
                if (!respuesta.optBoolean("ok", false)) {
                    callback.onError(respuesta.optString("msg", "No hay productos registrados"));
                    return;
                }
                try {
                    List<Producto> productos = new ArrayList<>();
                    JSONArray datos = respuesta.getJSONArray("data");
                    for (int i = 0; i < datos.length(); i++) {
                        Producto p = Producto.desdeJson(datos.getJSONObject(i));
                        if (p.activo) {
                            productos.add(p);
                        }
                    }
                    callback.onExito(productos);
                } catch (Exception e) {
                    callback.onError("Respuesta inesperada del servidor");
                }
            }

            @Override
            public void onError(String mensaje) {
                callback.onError(mensaje);
            }
        });
    }

    public void buscarPorId(int idProducto, final Callback<Producto> callback) {
        ApiClient.getInstancia().get("productos/" + idProducto, new Callback<JSONObject>() {
            @Override
            public void onExito(JSONObject respuesta) {
                if (!respuesta.optBoolean("ok", false)) {
                    callback.onError(respuesta.optString("msg", "Producto no encontrado"));
                    return;
                }
                try {
                    callback.onExito(Producto.desdeJson(respuesta.getJSONObject("data")));
                } catch (Exception e) {
                    callback.onError("Respuesta inesperada del servidor");
                }
            }

            @Override
            public void onError(String mensaje) {
                callback.onError(mensaje);
            }
        });
    }

    /**
     * Categorías asignadas a un producto (GET /api/productos/{id}/categorias,
     * modulo agregado en AA2-EV02). Son informacion secundaria en la
     * pantalla de detalle: si la consulta falla, no bloqueamos la
     * pantalla, simplemente se muestra sin categorías.
     */
    public void categoriasDe(int idProducto, final Callback<List<Categoria>> callback) {
        ApiClient.getInstancia().get("productos/" + idProducto + "/categorias", new Callback<JSONObject>() {
            @Override
            public void onExito(JSONObject respuesta) {
                List<Categoria> categorias = new ArrayList<>();
                if (respuesta.optBoolean("ok", false)) {
                    try {
                        JSONArray datos = respuesta.getJSONArray("data");
                        for (int i = 0; i < datos.length(); i++) {
                            categorias.add(Categoria.desdeJson(datos.getJSONObject(i)));
                        }
                    } catch (Exception ignored) {
                        // JSON mal formado -> se muestra el producto sin categorias.
                    }
                }
                callback.onExito(categorias);
            }

            @Override
            public void onError(String mensaje) {
                callback.onExito(new ArrayList<Categoria>());
            }
        });
    }
}
