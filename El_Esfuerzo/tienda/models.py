from django.db import models # type: ignore
from django.core.validators import RegexValidator # type: ignore


# Modelo Productos
class Productos(models.Model):
    OPCIONES_TIPO = [
        ('verdura', 'Verdura'),
        ('fruta', 'Fruta'),
    ]

    OPCIONES_CANTIDAD = [
        ('unt.', 'Unidades'),
        ('kilo','Kilos'),
        ('saco', 'Sacos'),
        ('cajon', 'Cajones'),
        ('malla', 'Mallas'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15, choices=OPCIONES_TIPO)
    precio = models.PositiveBigIntegerField()
    tipo_cantidad = models.CharField(max_length=15, choices=OPCIONES_CANTIDAD)
    cantidad = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre



    

# Modelo Proveedores
class Proveedores(models.Model):
    nombre_proveedor = models.CharField(max_length=100)
    Telefono_gmail = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_proveedor

    
#Modelo compras
class Compras(models.Model):
    OPCIONES_TIPO = [
        ('verdura', 'Verdura'),
        ('fruta', 'Fruta'),
    ]

    OPCIONES_CANTIDAD = [
        ('unt.', 'Unidades'),
        ('kilo','Kilos'),
        ('saco', 'Sacos'),
        ('cajon', 'Cajones'),
        ('malla', 'Mallas'),
    ]

    nombreProducto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='compras')
    nombre_proveedor = models.CharField(max_length=100)
    fecha = models.DateField()
    Total = models.PositiveBigIntegerField()

    def __str__(self):
        return f'Compra de {self.nombre_proveedor} el {self.fecha}'
    


# Modelo de Producto relacionado a la compra
class ProductoCompra(models.Model):
    compra = models.ForeignKey(Compras, related_name="productos", on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    tipo_cantidad = models.CharField(max_length=15, choices=Compras.OPCIONES_CANTIDAD)

    def __str__(self):
        return f'Compra de {self.producto if self.producto else "Producto eliminado"}'

    def get_tipo(self):
        return self.producto.tipo if self.producto else None
    
    @property
    def tipo(self):
        return self.producto.tipo



# Modelo Ventas
class Ventas(models.Model):
    fecha = models.DateField(auto_now_add=True)
    rut_cliente = models.CharField(max_length=12,
        validators=[
            RegexValidator(
                regex = r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$',
                message= 'El RUT debe tener el formato 12.345.678-9'
            )
        ])
    total = models.PositiveIntegerField()

    def __str__(self):
        return f"Venta {self.id} - {self.fecha}"


class ProductoVenta(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name='productos')
    producto = models.ForeignKey('Productos', on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    tipo_cantidad = models.CharField(max_length=15)
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} {self.tipo_cantidad}"
    


# Modelo Ventas
class Clientes(models.Model):
    rut = models.CharField(max_length=12, unique=True,
        validators=[
            RegexValidator(
                regex = r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$',
                message= 'El RUT debe tener el formato 12.345.678-9'
            )
        ])
    cantidad_compras = models.PositiveIntegerField(default=0)
    
    def __str__(self):
         return self.rut
    

    
    

