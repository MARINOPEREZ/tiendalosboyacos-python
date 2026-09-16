package co.edu.sena.tiendalosboyacos.mobile.modelo;

import org.json.JSONException;
import org.json.JSONObject;

/** Representa un registro de la tabla CATEGORIA. */
public class Categoria {

    public final int idCategoria;
    public final String nombre;

    public Categoria(int idCategoria, String nombre) {
        this.idCategoria = idCategoria;
        this.nombre = nombre;
    }

    public static Categoria desdeJson(JSONObject json) throws JSONException {
        return new Categoria(
                json.getInt("Id_Categoria"),
                json.optString("Nom_Categoria", "")
        );
    }

    @Override
    public String toString() {
        return nombre;
    }
}
