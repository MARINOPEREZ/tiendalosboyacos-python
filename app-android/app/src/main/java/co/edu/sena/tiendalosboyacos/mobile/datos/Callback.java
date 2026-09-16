package co.edu.sena.tiendalosboyacos.mobile.datos;

/**
 * Callback generico para operaciones asincronas de red. ApiClient
 * garantiza que siempre se invoque en el hilo principal, de modo que
 * las pantallas puedan actualizar vistas directamente desde aqui.
 */
public interface Callback<T> {
    void onExito(T resultado);
    void onError(String mensaje);
}
