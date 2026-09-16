package co.edu.sena.tiendalosboyacos.mobile.ui;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.util.List;

import co.edu.sena.tiendalosboyacos.mobile.R;
import co.edu.sena.tiendalosboyacos.mobile.datos.Callback;
import co.edu.sena.tiendalosboyacos.mobile.datos.ProductoRepository;
import co.edu.sena.tiendalosboyacos.mobile.modelo.Categoria;
import co.edu.sena.tiendalosboyacos.mobile.modelo.Producto;
import co.edu.sena.tiendalosboyacos.mobile.util.FormateadorPrecio;

/** Detalle de un producto: datos, precio y categorías asociadas. */
public class DetalleActivity extends Activity {

    public static final String EXTRA_ID_PRODUCTO = "extra_id_producto";

    private final ProductoRepository productoRepository = new ProductoRepository();

    private TextView textoNombre;
    private TextView textoPrecio;
    private TextView textoDescripcion;
    private TextView textoStock;
    private TextView textoCategorias;
    private ProgressBar barraProgreso;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detalle);

        textoNombre = findViewById(R.id.textoNombreDetalle);
        textoPrecio = findViewById(R.id.textoPrecioDetalle);
        textoDescripcion = findViewById(R.id.textoDescripcionDetalle);
        textoStock = findViewById(R.id.textoStockDetalle);
        textoCategorias = findViewById(R.id.textoCategoriasDetalle);
        barraProgreso = findViewById(R.id.barraProgresoDetalle);

        int idProducto = getIntent().getIntExtra(EXTRA_ID_PRODUCTO, -1);
        if (idProducto == -1) {
            Toast.makeText(this, "Producto inválido", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        cargarProducto(idProducto);
    }

    private void cargarProducto(int idProducto) {
        barraProgreso.setVisibility(View.VISIBLE);

        productoRepository.buscarPorId(idProducto, new Callback<Producto>() {
            @Override
            public void onExito(Producto producto) {
                barraProgreso.setVisibility(View.GONE);
                mostrarProducto(producto);
                cargarCategorias(producto.idProducto);
            }

            @Override
            public void onError(String mensaje) {
                barraProgreso.setVisibility(View.GONE);
                Toast.makeText(DetalleActivity.this, mensaje, Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void mostrarProducto(Producto producto) {
        textoNombre.setText(producto.nombre);
        textoPrecio.setText(FormateadorPrecio.aCop(producto.valorUnitario));
        textoDescripcion.setText(
                producto.descripcion.isEmpty() ? "Sin descripción" : producto.descripcion);
        textoStock.setText(getString(R.string.stock_formato, producto.cantidadStock));
    }

    private void cargarCategorias(int idProducto) {
        productoRepository.categoriasDe(idProducto, new Callback<List<Categoria>>() {
            @Override
            public void onExito(List<Categoria> categorias) {
                if (categorias.isEmpty()) {
                    textoCategorias.setText("Sin categoría asignada");
                    return;
                }
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < categorias.size(); i++) {
                    if (i > 0) sb.append(", ");
                    sb.append(categorias.get(i).nombre);
                }
                textoCategorias.setText(sb.toString());
            }

            @Override
            public void onError(String mensaje) {
                textoCategorias.setText("Sin categoría asignada");
            }
        });
    }
}
