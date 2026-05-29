import sys
sys.path.append("../")
from src.models.producto import Producto
from src.models.usuario import Usuario

# ─── Probar Producto ────────────────────────────────────
print("\n--- PRUEBA PRODUCTOS ---")
Producto.agregar("Café Boyacense", "Café premium 500g",
                  15000, 50, "2025-12-31", 19)
productos = Producto.listar()
for p in productos:
    print(p)

# ─── Probar Usuario ─────────────────────────────────────
print("\n--- PRUEBA USUARIOS ---")
Usuario.registrar("123456", "CC", "Juan", "Carlos",
                   "Pérez", "García", "3001234567",
                   "juan@email.com")
usuarios = Usuario.listar()
for u in usuarios:
    print(u)