package co.edu.sena.tiendalosboyacos.mobile.datos;

import android.os.Handler;
import android.os.Looper;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/**
 * Cliente HTTP minimalista para consumir la API REST de Tienda Los
 * Boyacos (Flask). Implementado con HttpURLConnection + org.json
 * (ambos incluidos en el SDK de Android) a proposito: evita agregar
 * dependencias de red externas (Retrofit/OkHttp) y con ello el riesgo
 * de repetir el problema de resolucion de Gradle que se presento en
 * AA2-EV01.
 *
 * Patron de diseño: Singleton — una sola instancia gestiona la URL
 * base y el despacho al hilo principal para toda la app.
 */
public class ApiClient {

    /**
     * 10.0.2.2 es el alias especial que el EMULADOR de Android usa para
     * llegar al localhost del computador anfitrion (donde corre XAMPP +
     * Flask). Para probar en un celular fisico, cambiar por la IP LAN
     * del PC (ej: 192.168.1.50:5000) con el celular en la misma red.
     */
    public static final String BASE_URL = "http://10.0.2.2:5000/api/";

    private static final int TIMEOUT_MS = 8000;

    private static ApiClient instancia;

    private final Handler hiloPrincipal = new Handler(Looper.getMainLooper());

    private ApiClient() {
    }

    public static synchronized ApiClient getInstancia() {
        if (instancia == null) {
            instancia = new ApiClient();
        }
        return instancia;
    }

    public void get(String endpoint, Callback<JSONObject> callback) {
        ejecutar("GET", endpoint, null, callback);
    }

    public void post(String endpoint, JSONObject cuerpo, Callback<JSONObject> callback) {
        ejecutar("POST", endpoint, cuerpo, callback);
    }

    private void ejecutar(final String metodo, final String endpoint,
                           final JSONObject cuerpo, final Callback<JSONObject> callback) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                HttpURLConnection conexion = null;
                try {
                    URL url = new URL(BASE_URL + endpoint);
                    conexion = (HttpURLConnection) url.openConnection();
                    conexion.setRequestMethod(metodo);
                    conexion.setConnectTimeout(TIMEOUT_MS);
                    conexion.setReadTimeout(TIMEOUT_MS);
                    conexion.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                    conexion.setRequestProperty("Accept", "application/json");

                    if (cuerpo != null) {
                        conexion.setDoOutput(true);
                        byte[] datos = cuerpo.toString().getBytes(StandardCharsets.UTF_8);
                        OutputStream salida = conexion.getOutputStream();
                        try {
                            salida.write(datos);
                        } finally {
                            salida.close();
                        }
                    }

                    int codigo = conexion.getResponseCode();
                    InputStream flujo = (codigo >= 200 && codigo < 300)
                            ? conexion.getInputStream()
                            : conexion.getErrorStream();

                    String respuesta = leer(flujo);
                    final JSONObject json = new JSONObject(respuesta);
                    notificarExito(callback, json);

                } catch (Exception e) {
                    notificarError(callback, "Error de conexión: " + e.getMessage());
                } finally {
                    if (conexion != null) {
                        conexion.disconnect();
                    }
                }
            }
        }).start();
    }

    private String leer(InputStream flujo) throws IOException {
        StringBuilder sb = new StringBuilder();
        BufferedReader lector = new BufferedReader(new InputStreamReader(flujo, StandardCharsets.UTF_8));
        try {
            String linea;
            while ((linea = lector.readLine()) != null) {
                sb.append(linea);
            }
        } finally {
            lector.close();
        }
        return sb.toString();
    }

    private void notificarExito(final Callback<JSONObject> callback, final JSONObject json) {
        hiloPrincipal.post(new Runnable() {
            @Override
            public void run() {
                callback.onExito(json);
            }
        });
    }

    private void notificarError(final Callback<JSONObject> callback, final String mensaje) {
        hiloPrincipal.post(new Runnable() {
            @Override
            public void run() {
                callback.onError(mensaje);
            }
        });
    }
}
