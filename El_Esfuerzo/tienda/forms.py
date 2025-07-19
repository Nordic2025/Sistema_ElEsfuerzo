from django import forms # type: ignore
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Productos, Compras, Proveedores, Ventas, Clientes


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['nombre', 'tipo', 'precio', 'tipo_cantidad', 'cantidad']

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo')
        return precio

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad < 0:
            raise forms.ValidationError('La cantidad no puede ser negativa')
        return cantidad

class ProveedoresForm(forms.ModelForm):
    class Meta:
        model = Proveedores
        fields = ['nombre_proveedor', 'Telefono_gmail', 'ubicacion']

class ClientesForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['rut', 'cantidad_compras']

class CompraForm(forms.ModelForm):
    nombre_proveedor = forms.ModelChoiceField(
        queryset=Proveedores.objects.all(),
        label="Proveedor",
        empty_label="Selecciona un proveedor",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    nombreProducto = forms.ModelChoiceField(
        queryset=Productos.objects.all(),
        label="Producto",
        empty_label="Seleccione un producto",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_Total(self):
        total = self.cleaned_data.get('Total')
        if total < 0:
            raise forms.ValidationError('El total no puede ser negativo')
        return total

    class Meta:
        model = Compras
        fields = ['nombre_proveedor', 'fecha', 'nombreProducto', 'Total']



class VentaForm(forms.ModelForm):
    nombreProducto = forms.ModelChoiceField(
        queryset=Productos.objects.all(),
        label="Producto",
        empty_label="Seleccione un producto",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_total(self):
        total = self.cleaned_data.get('total')
        if total < 0:
            raise forms.ValidationError('El total no puede ser negativo')
        return total

    class Meta:
        model = Ventas
        fields = ['rut_cliente', 'nombreProducto']