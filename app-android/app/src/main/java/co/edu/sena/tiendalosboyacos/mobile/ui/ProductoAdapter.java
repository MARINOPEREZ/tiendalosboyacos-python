package co.edu.sena.tiendalosboyacos.mobile.ui;

import android.app.Activity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.List;

import co.edu.sena.tiendalosboyacos.mobile.R;
import co.edu.sena.tiendalosboyacos.mobile.modelo.Producto;
import co.edu.sena.tiendalosboyacos.mobile.util.FormateadorPrecio;

/**
 * Patrón de diseño: Adapter — traduce la lista de objetos Producto
 * (modelo) a las vistas de cada fila de la lista (item_producto.xml).
 */
public class ProductoAdapter extends ArrayAdapter<Producto> {

    public ProductoAdapter(Activity contexto, List<Producto> productos) {
        super(contexto, 0, productos);
    }

    @Override
    public View getView(int position, View vistaReciclada, ViewGroup padre) {
        View fila = vistaReciclada;
        if (fila == null) {
            fila = LayoutInflater.from(getContext()).inflate(R.layout.item_producto, padre, false);
        }

        Producto producto = getItem(position);

        TextView textoNombre = fila.findViewById(R.id.textoNombreProducto);
        TextView textoPrecio = fila.findViewById(R.id.textoPrecioProducto);
        TextView textoStock = fila.findViewById(R.id.textoStockProducto);

        textoNombre.setText(producto.nombre);
        textoPrecio.setText(FormateadorPrecio.aCop(producto.valorUnitario));
        textoStock.setText(fila.getContext().getString(R.string.stock_formato, producto.cantidadStock));

        return fila;
    }
}
