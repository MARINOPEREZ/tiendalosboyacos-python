package co.edu.sena.tiendalosboyacos.mobile;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import org.json.JSONObject;
import org.junit.Test;

import co.edu.sena.tiendalosboyacos.mobile.modelo.Producto;

/**
 * Verifica que Producto.desdeJson respete los nombres de columna reales
 * de la tabla PRODUCTO (Nom_Producto, Vlr_Unitario, ...) tal como los
 * devuelve GET /api/productos — el mismo tipo de desajuste de nombres
 * que ya se documentó como riesgo del proyecto.
 */
public class ProductoMapperTest {

    @Test
    public void mapea_todos_los_campos_esperados() throws Exception {
        JSONObject json = new JSONObject();
        json.put("Id_Producto", 18);
        json.put("Nom_Producto", "Café Boyacense 500g");
        json.put("Descripcion", "Café de origen, tueste medio");
        json.put("Vlr_Unitario", 18500.0);
        json.put("Cant_Stock", 12);
        json.put("IVA", 19.0);
        json.put("Img_Producto", "prod_18_descarga_1.jpg");
        json.put("Activo", 1);

        Producto producto = Producto.desdeJson(json);

        assertEquals(18, producto.idProducto);
        assertEquals("Café Boyacense 500g", producto.nombre);
        assertEquals(18500.0, producto.valorUnitario, 0.001);
        assertEquals(12, producto.cantidadStock);
        assertTrue(producto.activo);
    }

    @Test
    public void usa_valores_por_defecto_si_faltan_campos_opcionales() throws Exception {
        JSONObject json = new JSONObject();
        json.put("Id_Producto", 5);
        json.put("Nom_Producto", "Miel de abejas");
        json.put("Vlr_Unitario", 12000.0);
        // Sin Descripcion ni Img_Producto: el backend los permite NULL.

        Producto producto = Producto.desdeJson(json);

        assertEquals("", producto.descripcion);
        assertNull(producto.imagen);
    }

    @Test
    public void producto_inactivo_se_mapea_como_no_activo() throws Exception {
        JSONObject json = new JSONObject();
        json.put("Id_Producto", 7);
        json.put("Nom_Producto", "Producto descontinuado");
        json.put("Vlr_Unitario", 5000.0);
        json.put("Activo", 0);

        Producto producto = Producto.desdeJson(json);

        assertEquals(false, producto.activo);
    }
}
