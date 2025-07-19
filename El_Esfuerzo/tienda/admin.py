from django.contrib import admin
from .models import Productos, Compras, Proveedores, ProductoCompra, Ventas, Clientes

# Register your models here.
admin.site.register(Productos)
admin.site.register(Compras)
admin.site.register(Proveedores)
admin.site.register(ProductoCompra)
admin.site.register(Ventas)
admin.site.register(Clientes)