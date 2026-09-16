package co.edu.sena.tiendalosboyacos.mobile.ui;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import co.edu.sena.tiendalosboyacos.mobile.R;
import co.edu.sena.tiendalosboyacos.mobile.datos.AuthRepository;

/**
 * Pantalla inicial (LAUNCHER). Autentica contra el servicio REST que ya
 * usa el resto del proyecto (/api/auth/login, evidencia AA5-EV01) y
 * navega al catálogo si las credenciales son válidas.
 */
public class LoginActivity extends Activity {

    private EditText campoMail;
    private EditText campoPassword;
    private Button botonIngresar;
    private ProgressBar barraProgreso;
    private TextView textoAyuda;

    private final AuthRepository authRepository = new AuthRepository();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        campoMail = findViewById(R.id.campoMail);
        campoPassword = findViewById(R.id.campoPassword);
        botonIngresar = findViewById(R.id.botonIngresar);
        barraProgreso = findViewById(R.id.barraProgreso);
        textoAyuda = findViewById(R.id.textoAyuda);

        botonIngresar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                intentarLogin();
            }
        });
    }

    private void intentarLogin() {
        final String mail = campoMail.getText().toString().trim();
        final String password = campoPassword.getText().toString();

        if (mail.isEmpty() || password.isEmpty()) {
            textoAyuda.setText("Correo y contraseña son obligatorios");
            return;
        }

        mostrarCargando(true);

        authRepository.login(mail, password, new AuthRepository.LoginCallback() {
            @Override
            public void onExito(String nombreUsuario, String rol) {
                mostrarCargando(false);
                Intent intent = new Intent(LoginActivity.this, CatalogoActivity.class);
                intent.putExtra(CatalogoActivity.EXTRA_NOMBRE_USUARIO, nombreUsuario);
                intent.putExtra(CatalogoActivity.EXTRA_ROL, rol);
                startActivity(intent);
                finish();
            }

            @Override
            public void onError(String mensaje) {
                mostrarCargando(false);
                textoAyuda.setText(mensaje);
                Toast.makeText(LoginActivity.this, mensaje, Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void mostrarCargando(boolean cargando) {
        barraProgreso.setVisibility(cargando ? View.VISIBLE : View.GONE);
        botonIngresar.setEnabled(!cargando);
    }
}
