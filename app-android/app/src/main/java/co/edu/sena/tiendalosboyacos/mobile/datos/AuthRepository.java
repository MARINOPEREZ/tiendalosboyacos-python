package co.edu.sena.tiendalosboyacos.mobile.datos;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Encapsula el consumo de /api/auth/login (servicio ya entregado en la
 * evidencia AA5-EV01). LoginActivity no conoce HttpURLConnection ni el
 * formato JSON exacto de la respuesta: solo recibe éxito/error ya
 * interpretados — esta es la capa de acceso a datos, separada de la
 * capa de presentación (Activities).
 *
 * Patron de diseño: Repository.
 */
public class AuthRepository {

    public interface LoginCallback {
        void onExito(String nombreUsuario, String rol);
        void onError(String mensaje);
    }

    public void login(String mail, String password, final LoginCallback callback) {
        JSONObject cuerpo = new JSONObject();
        try {
            cuerpo.put("mail", mail);
            cuerpo.put("password", password);
        } catch (JSONException e) {
            callback.onError("No se pudo preparar la solicitud");
            return;
        }

        ApiClient.getInstancia().post("auth/login", cuerpo, new Callback<JSONObject>() {
            @Override
            public void onExito(JSONObject respuesta) {
                boolean ok = respuesta.optBoolean("ok", false);
                if (ok) {
                    String usuario = respuesta.optString("usuario", "");
                    String rol = respuesta.optString("rol", "Cliente");
                    callback.onExito(usuario, rol);
                } else {
                    // Mensaje exacto que ya define AA5-EV01 ("Error en la autenticación")
                    callback.onError(respuesta.optString("mensaje", "Error en la autenticación"));
                }
            }

            @Override
            public void onError(String mensaje) {
                callback.onError(mensaje);
            }
        });
    }
}
