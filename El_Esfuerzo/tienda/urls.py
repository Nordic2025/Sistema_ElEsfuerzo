from django.urls import path # type: ignore
from . import views
from django.contrib.auth import views as auth_views # type: ignore


urlpatterns = [
    #Login, Logout y Principal
    path('', views.login_usuario, name='login'),
    path('principal/', views.principal, name= 'principal'),
    path('login/', auth_views.LoginView.as_view(template_name='tienda/login.html'), name='login'),
    path('logout', views.logout_usuario, name='logout'),

    #Usuarios
    path('cliente/', views.cliente, name='cliente'),
    path('editar_cliente/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),


    #Proveedores
    path('ver_proveedor/', views.ver_proveedor, name= 'ver_proveedor'),
    path('anadir_proveedor/', views.anadir_proveedor, name= 'anadir_proveedor'),
    path('editar_proveedor/<int:proveedor_id>/', views.editar_proveedor, name= 'editar_proveedor'),
    path('eliminar_proveedor/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

    #Compras
    path('ver_compras/', views.ver_compras, name= 'ver_compras'),
    path('detalle-compra/<int:compra_id>/', views.detalle_compra, name='detalle_compra'),
    path('anadir_compra/', views.anadir_compra, name= 'anadir_compra'),
    path('obtener_productos/', views.obtener_productos_por_tipo, name='obtener_productos_por_tipo'),
    path('editar_compra/<int:compra_id>/', views.editar_compra, name= 'editar_compra'),
    path('eliminar_compra/<int:compra_id>/', views.eliminar_compra, name='eliminar_compra'),
    

    #Productos
    path('producto/', views.producto, name= 'producto'),
    path('lista_producto/', views.lista_producto, name='lista_producto'),
    path('agregar_producto/', views.agregar_producto, name= 'agregar_producto'),
    path('editar_producto/<int:producto_id>/', views.editar_producto, name = 'editar_producto'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),


    #Ventas
    path('ver_ventas/', views.ver_ventas, name='ver_ventas'),
    path('anadir_ventas/', views.anadir_ventas, name='anadir_ventas'),
    path('editar_ventas/<int:venta_id>/', views.editar_ventas, name='editar_ventas'),
    path('eliminar_venta/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
    path('detalle_venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('obtener_precio_producto/', views.obtener_precio_producto, name='obtener_precio_producto'),


]