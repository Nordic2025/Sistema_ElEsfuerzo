from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib import messages # type: ignore
from .models import Clientes, ProductoVenta, Productos, Compras, Proveedores, ProductoCompra, Ventas
from .forms import ProductoForm, CompraForm, ProveedoresForm,  VentaForm, ClientesForm
from django.contrib.auth.models import User # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.http import JsonResponse # type: ignore
import json
from django.core.exceptions import ValidationError # type: ignore
from django.core.validators import RegexValidator # type: ignore


#Login, Logout y Principal
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username= username, password = password)

        if user is not None:
            login(request, user)
            messages.success(request, f'{user} inició sesión correctamente')
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect ('principal')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'tienda/login.html')


def logout_usuario(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Cierre de sesion exitoso')
        return redirect('/')


@login_required(login_url='login')
def principal(request):
    return render(request, 'tienda/principal.html')



#Clientes
@login_required(login_url='login')
def cliente(request):
    clientes = Clientes.objects.all()
    return render(request, 'tienda/clientes/cliente.html', {'clientes': clientes})


@login_required(login_url='login')
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Clientes, id=cliente_id)
    
    if request.method == 'POST':
        rut_nuevo = request.POST.get('rut')
        rut_anterior = cliente.rut
        
        # Validar el nuevo RUT
        validator = RegexValidator(
            regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$',
        )
        
        try:
            validator(rut_nuevo) 
        except ValidationError as e:
            messages.error(request, 'El RUT debe tener el formato 12.345.678-9')
            return render(request, 'tienda/clientes/editar_cliente.html', {'cliente': cliente})
        
        # Actualizar el RUT en la tabla Clientes
        cliente.rut = rut_nuevo
        cliente.save()
        
        Ventas.objects.filter(rut_cliente=rut_anterior).update(rut_cliente=rut_nuevo)
        
        messages.success(request, 'Cliente editado correctamente')
        return redirect('cliente')
    
    return render(request, 'tienda/clientes/editar_cliente.html', {'cliente': cliente})




#Proveedores
@login_required(login_url='login')
def ver_proveedor(request):
    proveedores = Proveedores.objects.all()
    return render(request, 'tienda/proveedores/ver_proveedores.html', {'proveedores': proveedores})

@login_required(login_url='login')
def anadir_proveedor(request):
    if request.method == 'POST':
        form = ProveedoresForm (request.POST)
        if form.is_valid():
            form.save() #Guardar el Proveedor en la bd
            messages.success(request, 'Proveedor creado correctamente')
            return redirect('ver_proveedor')
    else: 
        form = ProveedoresForm ()
    return render(request, 'tienda/proveedores/anadir_proveedores.html', {'form': form})


@login_required(login_url='login')
def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedores, id=proveedor_id)
    if request.method == 'POST':
        form = ProveedoresForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor editado correctamente')
            return redirect('ver_proveedor') 
    else:
        form = ProveedoresForm(instance=proveedor)
    
    return render(request, 'tienda/proveedores/editar_proveedor.html', {'form': form})


@login_required(login_url='login')
def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedores, id=proveedor_id)
    proveedor.delete()
    messages.success(request, 'Proveedor eliminado correctamente.') 
    return redirect('ver_proveedor')



#Compras
@login_required(login_url='login')
def ver_compras(request):
    compras = Compras.objects.all()
    return render(request, 'tienda/proveedores/ver_compras.html', {'compras': compras})


@login_required(login_url='login')
def detalle_compra(request, compra_id):
    compra = get_object_or_404(Compras, id=compra_id)
    productos = ProductoCompra.objects.filter(compra=compra).select_related('producto')
    
    productos_procesados = []
    for producto_compra in productos:
        productos_procesados.append({
            'nombre': producto_compra.producto.nombre if producto_compra.producto else "Producto eliminado",
            'tipo': producto_compra.producto.tipo if producto_compra.producto else "No disponible",
            'cantidad': producto_compra.cantidad,
            'tipo_cantidad': producto_compra.tipo_cantidad
        })

    return render(request, 'tienda/proveedores/detalle_compra.html', {
        'compra': compra,
        'productos': productos_procesados,
    })

@login_required(login_url='login')
def anadir_compra(request):
    if request.method == 'POST':
        form = CompraForm (request.POST)

        form_data = request.POST.copy()
        form_data.pop('productos', None)  # Eliminar 'productos' para que no pase por la validación del formulario
        form = CompraForm(form_data)
        
        print("Errores de validación del formulario:", form.errors) 
        if form.is_valid():
            compra = form.save() #Guardar la compra en la bd

            print(form.errors)
            print(request.POST.get('productos'))

            # Procesar los productos enviados desde la grilla
            productos_seleccionados = json.loads(request.POST.get('productos', '[]'))

            for producto_data in productos_seleccionados:
                cantidad = int(producto_data['cantidad'])
                if cantidad < 0:
                    messages.error(request, 'La cantidad de productos no puede ser negativa')
                    if compra:
                        compra.delete()
                    return redirect('anadir_compra')
    
            # Guardar cada producto de la grilla como ProductoCompra
            for producto_data in productos_seleccionados:
                producto = Productos.objects.get(id=producto_data['productoId'])
                cantidad_comprada = int(producto_data['cantidad'])
                
                # Actualizar stock del producto
                producto.cantidad += cantidad_comprada
                producto.save()

                ProductoCompra.objects.create(
                    compra=compra,
                    producto_id=producto_data['productoId'],
                    cantidad=cantidad_comprada,
                    tipo_cantidad=producto_data['tipoCantidad'],
                )
            messages.success(request, 'Compra creada correctamente')
            return redirect('ver_compras')
    else: 
        form = CompraForm ()
    return render(request, 'tienda/proveedores/anadir_compra.html', {'form': form})

@login_required(login_url='login')
def obtener_productos_por_tipo(request):
    tipo = request.GET.get('tipo')
    productos = Productos.objects.filter(tipo=tipo).values('id', 'nombre')
    return JsonResponse({'productos': list(productos)})

@login_required(login_url='login')
def editar_compra(request, compra_id):
    compra = get_object_or_404(Compras, id=compra_id)
    productos_compra = ProductoCompra.objects.filter(compra=compra)

    if request.method == 'POST':
        form_data = request.POST.copy()
        productos_nuevos = json.loads(request.POST.get('productos', '[]'))
        if productos_nuevos:
            form_data['nombreProducto'] = productos_nuevos[0]['productoId']
        
        form = CompraForm(form_data, instance=compra)

        if form.is_valid():
            compra = form.save()
            productos_compra.delete()

            for producto_data in productos_nuevos:
                cantidad = int(producto_data['cantidad'])
                if cantidad < 0:
                    messages.error(request, 'La cantidad de productos no puede ser negativa')
                    return redirect('editar_compra', compra_id=compra_id)
    
            # Revertir cantidades anteriores
            for producto_anterior in productos_compra:
                producto = producto_anterior.producto
                producto.cantidad -= producto_anterior.cantidad
                producto.save()

            compra = form.save()
            productos_compra.delete()

            # Aplicar nuevas cantidades
            for producto_data in productos_nuevos:
                producto = Productos.objects.get(id=producto_data['productoId'])
                cantidad = int(producto_data['cantidad'])
                
                # Actualizar stock
                producto.cantidad += cantidad
                producto.save()

                ProductoCompra.objects.create(
                    compra=compra,
                    producto_id=producto_data['productoId'],
                    cantidad=cantidad,
                    tipo_cantidad=producto_data['tipoCantidad']
                )


            messages.success(request, 'Compra actualizada correctamente')
            return redirect('ver_compras')
    else:
        form = CompraForm(instance=compra)

    productos_json = json.dumps([
        {
            'productoId': producto.producto.id,
            'productoNombre': producto.producto.nombre,
            'tipo': producto.producto.tipo,
            'cantidad': producto.cantidad,
            'tipoCantidad': producto.tipo_cantidad,
        }
        for producto in productos_compra
    ])

    return render(request, 'tienda/proveedores/editar_compra.html', {
        'form': form,
        'productos': productos_json,
        'compra': compra,
    })



@login_required(login_url='login')
def eliminar_compra(request, compra_id):
    compra = get_object_or_404(Compras, id=compra_id)
    compra.delete()
    messages.success(request, 'Compra eliminada correctamente.') 
    return redirect('ver_compras')




#Productos
@login_required(login_url='login')
def producto(request):
    productos = Productos.objects.all()    
    if 'success_message' in request.session:
        messages.success(request, request.session['success_message'])
        del request.session['success_message']
    return render(request, 'tienda/productos/productos.html', {'productos': productos})


@login_required(login_url='login')
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)  
        if form.is_valid():
            nombre_producto = form.cleaned_data['nombre']
            # Verificar si ya existe un producto con el mismo nombre
            if Productos.objects.filter(nombre__iexact=nombre_producto).exists():
                messages.error(request, 'Ya existe un producto con este nombre')
                return render(request, 'tienda/productos/agregar_producto.html', {'form': form})
            
            form.save()
            messages.success(request, 'Producto creado correctamente')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('producto')
    else:
        form = ProductoForm()
    
    return render(request, 'tienda/productos/agregar_producto.html', {'form': form})


    
@login_required(login_url='login')
def editar_producto(request, producto_id):
    producto = get_object_or_404(Productos, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto editado correctamente')
        return redirect('producto')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'tienda/productos/editar_producto.html', {'form': form})


@login_required(login_url='login')
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Productos, id=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente.') 
    return redirect('producto')


@login_required(login_url='login')
def lista_producto(request):
    productos= Productos.objects.all()
    print(f"Productos encontrados: {productos.count()}") 
    return render(request, 'tienda/productos/lista_producto.html', {'productos': productos})


#Ventas
@login_required(login_url='login')
def ver_ventas(request):
    ventas = Ventas.objects.all().order_by('-fecha')
    for venta in ventas:
        productos_venta = ProductoVenta.objects.filter(venta=venta).select_related('producto')
        venta.has_deleted_products = any(not pv.producto for pv in productos_venta)
    return render(request, 'tienda/ventas/ver_ventas.html', {'ventas': ventas})



@login_required(login_url='login')
def anadir_ventas(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        form_data = request.POST.copy()
        form_data.pop('productos', None)
        form = VentaForm(form_data)

        print("Form errors:", form.errors) 
        
        if form.is_valid():
            rut_cliente = form.cleaned_data['rut_cliente']
            cliente_obj, created = Clientes.objects.get_or_create(
                rut=rut_cliente,
                defaults={'cantidad_compras': 1}
            )
            
            if not created:
                cliente_obj.cantidad_compras += 1
                cliente_obj.save()

            venta = form.save(commit=False)
            venta.total = 0
            venta.save()

            productos_seleccionados = json.loads(request.POST.get('productos', '[]'))
            total_venta = 0

            for producto_data in productos_seleccionados:
                cantidad = int(producto_data['cantidad'])
                if cantidad < 0:
                    messages.error(request, 'La cantidad de productos no puede ser negativa')
                    if venta:
                        venta.delete()
                    return redirect('anadir_ventas')

            # Verificar stock disponible
            for producto_data in productos_seleccionados:
                producto = Productos.objects.get(id=producto_data['productoId'])
                cantidad_solicitada = int(producto_data['cantidad'])
                
                if producto.cantidad < cantidad_solicitada:
                    messages.error(request, f'Stock insuficiente para {producto.nombre}. Stock actual: {producto.cantidad}')
                    venta.delete()  # Eliminar la venta si no hay stock suficiente
                    return redirect('anadir_ventas')

            # Procesar la venta
            for producto_data in productos_seleccionados:
                producto = Productos.objects.get(id=producto_data['productoId'])
                cantidad = int(producto_data['cantidad'])
                subtotal = producto.precio * cantidad

                # Actualizar stock
                producto.cantidad -= cantidad
                producto.save()

                ProductoVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    tipo_cantidad=producto_data['tipoCantidad'],
                    subtotal=subtotal
                )
                total_venta += subtotal

            venta.total = total_venta
            venta.save()


            messages.success(request, 'Venta creada correctamente')
            return redirect('ver_ventas')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')

    else:
        form = VentaForm()
    
    context = {
        'form': form,
        'tipos_producto': Productos.OPCIONES_TIPO,
        'tipos_cantidad': Productos.OPCIONES_CANTIDAD
    }
    return render(request, 'tienda/ventas/anadir_ventas.html', context)

@login_required(login_url='login')
def obtener_precio_producto(request):
    producto_id = request.GET.get('producto_id')
    producto = get_object_or_404(Productos, id=producto_id)
    return JsonResponse({'precio': producto.precio})


@login_required(login_url='login')
def editar_ventas(request, venta_id):
    venta = get_object_or_404(Ventas, id=venta_id)
    productos_venta = ProductoVenta.objects.filter(venta=venta)

    if request.method == 'POST':
        try:
            productos_nuevos = json.loads(request.POST.get('productos', '[]'))
            
            if not productos_nuevos:
                messages.error(request, 'Debe incluir al menos un producto')
                return redirect('editar_ventas', venta_id=venta_id)

            # Diccionario de productos actuales
            productos_actuales = {str(pv.producto.id): pv.cantidad for pv in productos_venta}

            # Actualizamos datos básicos de la venta
            venta.rut_cliente = request.POST.get('rut_cliente')
            venta.total = request.POST.get('total')

            for producto_data in productos_nuevos:
                cantidad = int(producto_data['cantidad'])
                if cantidad < 0:
                    messages.error(request, 'La cantidad de productos no puede ser negativa')
                    return redirect('editar_ventas', venta_id=venta_id)

            for producto_data in productos_nuevos:
                producto = Productos.objects.get(id=producto_data['productoId'])
                cantidad_nueva = int(producto_data['cantidad'])
                cantidad_actual = productos_actuales.get(str(producto.id), 0)
                
                diferencia = cantidad_nueva - cantidad_actual
                
                if diferencia > 0 and diferencia > producto.cantidad:
                    messages.error(request, f'Stock insuficiente para {producto.nombre}')
                    return redirect('editar_ventas', venta_id=venta_id)
                
                producto.cantidad -= diferencia
                producto.save()

            # Eliminamos los productos anteriores después de procesar las diferencias
            productos_venta.delete()
            total_venta = 0

            for producto_data in productos_nuevos:
                producto = Productos.objects.get(id=producto_data['productoId'])
                cantidad = int(producto_data['cantidad'])
                subtotal = producto.precio * cantidad

                ProductoVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    tipo_cantidad=producto_data['tipoCantidad'],
                    subtotal=subtotal
                )
                total_venta += subtotal

            venta.rut_cliente = request.POST.get('rut_cliente')
            venta.total = total_venta
            venta.save()
            messages.success(request, 'Venta actualizada correctamente')
            return redirect('ver_ventas')

        except Exception as e:
            messages.error(request, f'Error al actualizar la venta: {str(e)}')
            return redirect('editar_ventas', venta_id=venta_id)

    productos_json = json.dumps([{
        'productoId': producto.producto.id,
        'productoNombre': producto.producto.nombre,
        'tipo': producto.producto.tipo,
        'cantidad': producto.cantidad,
        'tipoCantidad': producto.tipo_cantidad,
        'precio': producto.producto.precio,
        'subtotal': producto.subtotal
    } for producto in productos_venta])

    return render(request, 'tienda/ventas/editar_ventas.html', {
        'venta': venta,
        'productos': productos_json
    })


@login_required(login_url='login')
def detalle_venta(request, venta_id):
    venta = get_object_or_404(Ventas, id=venta_id)
    productos = ProductoVenta.objects.filter(venta=venta).select_related('producto')
    
    productos_procesados = []
    for producto_venta in productos:
        productos_procesados.append({
            'nombre': producto_venta.producto.nombre if producto_venta.producto else "Producto eliminado",
            'tipo': producto_venta.producto.tipo if producto_venta.producto else "No disponible",
            'cantidad': producto_venta.cantidad,
            'tipo_cantidad': producto_venta.tipo_cantidad,
            'subtotal': producto_venta.subtotal
        })

    return render(request, 'tienda/ventas/detalle_venta.html', {
        'venta': venta,
        'productos': productos_procesados,
    })


@login_required(login_url='login')
def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Ventas, id=venta_id)
    venta.delete()
    messages.success(request, 'Venta eliminada correctamente.') 
    return redirect('ver_ventas')







