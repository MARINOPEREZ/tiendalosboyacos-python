package co.edu.sena.tiendalosboyacos.mobile.util;

import java.util.Locale;

/**
 * Da formato a valores en pesos colombianos (COP) para mostrarlos en la
 * UI (ej: 15000 -> "$ 15.000"). Es una clase pura, sin dependencias de
 * Android, a propósito: se puede probar con JUnit local, sin emulador
 * ni instrumentación.
 */
public final class FormateadorPrecio {

    private FormateadorPrecio() {
    }

    public static String aCop(double valor) {
        long redondeado = Math.round(valor);
        String texto = String.format(Locale.US, "%,d", redondeado).replace(',', '.');
        return "$ " + texto;
    }
}
