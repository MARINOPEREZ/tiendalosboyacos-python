package co.edu.sena.tiendalosboyacos.mobile;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import co.edu.sena.tiendalosboyacos.mobile.util.FormateadorPrecio;

/**
 * Prueba unitaria local (no necesita emulador ni dispositivo): valida
 * el formato de precios en pesos colombianos usado en el catálogo y el
 * detalle de producto.
 */
public class FormateadorPrecioTest {

    @Test
    public void formatea_valores_con_separador_de_miles() {
        assertEquals("$ 15.000", FormateadorPrecio.aCop(15000));
        assertEquals("$ 1.234.567", FormateadorPrecio.aCop(1234567));
    }

    @Test
    public void formatea_cero() {
        assertEquals("$ 0", FormateadorPrecio.aCop(0));
    }

    @Test
    public void redondea_valores_decimales() {
        // Vlr_Unitario es DECIMAL en la base de datos; puede llegar con
        // centavos aunque la tienda solo maneje pesos enteros.
        assertEquals("$ 2.500", FormateadorPrecio.aCop(2499.6));
    }
}
