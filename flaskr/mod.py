from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
    def _str_(self):
        return f"Perfil de {self.user.username}"

# Modelo para categorias de productos 
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
    # Modelo para Productos en el Inventario
class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=0)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_entrada = models.DateField(auto_now_add=True)

    def _str_(self):
        return self.nombre
    
    def actualizar_stock(self, cantidad):
        """ Actualiza la cantidad de productos en el inventario. """
        self.cantidad += cantidad
        self.save()

    def reducir_stock(self, cantidad):
        """ Reduce la cantidad de productos en el inventario. """
        if self.cantidad >= cantidad:
            self.cantidad -= cantidad
            self.save()
        else:
            raise ValueError("No hay suficiente stock para reducir.")

# Modelo para Entradas y Salidas de Inventario (Movimientos)
class Movimiento(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)

    def _str_(self):
        return f"{self.tipo.capitalize()} de {self.cantidad} unidades de {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        if self.tipo == 'entrada':
            self.producto.actualizar_stock(self.cantidad)
        elif self.tipo == 'salida':
            self.producto.reducir_stock(self.cantidad)
        super().save(*args, **kwargs)