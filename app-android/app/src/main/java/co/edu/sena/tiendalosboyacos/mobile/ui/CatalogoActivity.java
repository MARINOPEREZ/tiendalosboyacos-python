package co.edu.sena.tiendalosboyacos.mobile.ui;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

import co.edu.sena.tiendalosboyacos.mobile.R;
import co.edu.sena.tiendalosboyacos.mobile.datos.Callback;
import co.edu.sena.tiendalosboyacos.mobile.datos.ProductoRepository;
import co.edu.sena.tiendalosboyacos.mobile.modelo.Producto;

/**
 * Catálogo de productos activos (GET /api/productos). Al tocar un
 * producto se abre DetalleActivity con su Id_Producto.
 */
public class CatalogoActivity extends Activity {

    public static final String EXTRA_NOMBRE_USUARIO = "extra_nombre_usuario";
    public static final String EXTRA_ROL = "extra_rol";

    private final ProductoRepository productoRepository = new ProductoRepository();
    private final List<Producto> productos = new ArrayList<>();

    private ListView listaProductos;
    private ProgressBar barraProgreso;
    private TextView textoEstado;
    private ProductoAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_catalogo);

        String nombreUsuario = getIntent().getStringExtra(EXTRA_NOMBRE_USUARIO);
        String rol = getIntent().getStringExtra(EXTRA_ROL);

        TextView textoBienvenida = findViewById(R.id.textoBienvenida);
        textoBienvenida.setText(getString(R.string.bienvenida_formato, nombreUsuario, rol));

        listaProductos = findViewById(R.id.listaProductos);
        barraProgreso = findViewById(R.id.barraProgresoCatalogo);
        textoEstado = findViewById(R.id.textoEstadoCatalogo);

        adapter = new ProductoAdapter(this, productos);
        listaProductos.setAdapter(adapter);
        listaProductos.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Producto seleccionado = productos.get(position);
                Intent intent = new Intent(CatalogoActivity.this, DetalleActivity.class);
                intent.putExtra(DetalleActivity.EXTRA_ID_PRODUCTO, seleccionado.idProducto);
                startActivity(intent);
            }
        });

        cargarProductos();
    }

    private void cargarProductos() {
        barraProgreso.setVisibility(View.VISIBLE);
        textoEstado.setText("");

        productoRepository.listar(new Callback<List<Producto>>() {
            @Override
            public void onExito(List<Producto> resultado) {
                barraProgreso.setVisibility(View.GONE);
                productos.clear();
                productos.addAll(resultado);
                adapter.notifyDataSetChanged();
                if (productos.isEmpty()) {
                    textoEstado.setText("No hay productos registrados todavía");
                }
            }

            @Override
            public void onError(String mensaje) {
                barraProgreso.setVisibility(View.GONE);
                textoEstado.setText(mensaje);
                Toast.makeText(CatalogoActivity.this, mensaje, Toast.LENGTH_SHORT).show();
            }
        });
    }
}
