from flaskr.modelos.db import get_db

import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('productos', __name__, url_prefix='/dashboard/productos')

#Esta funcion recibe una cantidad, un destino y en casi de que haya un producto el cual revisar
#Si enviamos la clave del producto le decimos que no lo cuente como tal sino que contemple la cantidad anterior que habia
def suficiente_inventario(cantidad, almacen,id):
    db = get_db()
    max = db.execute('SELECT Capacidad FROM Almacen WHERE Clave = ?',(almacen,)).fetchone()
    conteo = db.execute('SELECT SUM(CantidadDisponible) FROM Producto WHERE Almacen = ?',(almacen,)).fetchone()
    cuenta = 0
    #Si ya hay cosas en el almacen las contemplamos en la cuenta
    if conteo[0] != None:
        cuenta = cuenta + int(conteo[0])
    #Si tenemos un producto revisamos cuanto habia antes y lo descartamos de la cuenta es decir:
    #Si añadimos 10 a un producto con 70 la cuenta anterior ya estaba contando esa cantidad, lo que queremos en realidad
    #es saber si la cantidad que recibimos aqui cabe dentro de ese almacen, recordando que si por ejemplo ya teniamos 70 de algo
    #los descartamos y comparamos con la nueva cantidad es decir los 80
    if id != None:
        anterior = db.execute('SELECT CantidadDisponible FROM Producto WHERE Clave = ?',(id,)).fetchone()
        cuenta = cuenta-anterior[0]
        
    if cuenta+int(cantidad) <= int(max[0]):
        return True
    else:
        return False

#Ruta para registrar
@bp.route('/registro',methods=('GET','POST'))
def registrar ():
    db = get_db()
    if request.method == 'GET':
        almacenes = db.execute(
            'SELECT a.Clave,u.Nombre,a.Capacidad FROM Almacen AS a INNER JOIN Ubicacion AS u ON a.Ubicacion = u.Clave;').fetchall()
        categorias = db.execute('SELECT * FROM Categoria').fetchall()
        proveedores = db.execute('SELECT * FROM Proveedor').fetchall()
        return render_template('producto/form.html',almacenes=almacenes,categorias=categorias,proveedores=proveedores,prod=None)
    else:
        almacen = request.form['almacen']
        categoria = request.form['categoria']
        proveedor = request.form['proveedor']
        nombre = request.form['nombre'].lower()
        fecha_cad = request.form['fecha_cad']
        cantidad = request.form['cantidad']
        alerta = request.form['alerta']
        creadoen = datetime.today().strftime('%Y-%m-%d')
        try:
            db.execute(
                "INSERT INTO Producto (Almacen,Categoria,Proveedor,Nombre,FechaOrden,FechaCaducidad,CantidadDisponible,CantidadMinima) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (almacen,categoria,proveedor,nombre,creadoen,fecha_cad,0,alerta)
            )
            db.commit()
            return redirect(url_for('dashboard.registro'))
   
        except db.IntegrityError:
            error = f"Ocurrio un error"

#Ruta que rederiza la tabla
@bp.route('/consulta',methods=('GET','POST'))
def consulta ():  
    db = get_db()
    if request.method == 'GET':
        productos =  db.execute('SELECT * FROM Producto').fetchall()
        return render_template('producto/consulta.html',productos = productos)
    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor']
        desc = request.form['desc']
        max = request.form['max']

        if valor != "":
            valor = f"WHERE {campo} LIKE '{"%"+valor+"%"}'"

        if max=="" or max=="0":
            max=""
        else:
            max = f" LIMIT {max}"

        query = f'''
        SELECT * FROM Producto
        {valor} ORDER BY {campo} {desc} {max}
        '''
        productos = db.execute(query).fetchall()
        return render_template('producto/consulta.html',productos=productos)

#Ruta para editarlo
@bp.route('/editar/<int:clave>',methods=('GET','POST'))
def modificar (clave):
    db = get_db()
    if request.method == 'GET':
        almacenes = db.execute(
            'SELECT a.Clave,u.Nombre,a.Capacidad FROM Almacen AS a INNER JOIN Ubicacion AS u ON a.Ubicacion = u.Clave;').fetchall()
        categorias = db.execute('SELECT * FROM Categoria').fetchall()
        proveedores = db.execute('SELECT * FROM Proveedor').fetchall()
        producto = db.execute('SELECT * FROM Producto WHERE Clave = ?',(clave,)).fetchone()
        return render_template('producto/form.html',almacenes=almacenes,categorias=categorias,proveedores=proveedores,prod=producto)
    else:
        almacen = request.form['almacen']
        categoria = request.form['categoria']
        proveedor = request.form['proveedor']
        nombre = request.form['nombre'].lower()
        fecha_cad = request.form['fecha_cad']
        cantidad = request.form['cantidad']
        alerta = request.form['alerta']
        try:
            if(suficiente_inventario(cantidad,almacen,clave)):
                db.execute(
                    "UPDATE Producto SET Almacen = ?,Categoria = ?,Proveedor = ?,Nombre = ?,FechaCaducidad = ?,CantidadDisponible = ?,CantidadMinima = ? WHERE Clave = ?",
                    (almacen,categoria,proveedor,nombre,fecha_cad,cantidad,alerta,clave)
                )
                db.commit()
                return redirect(url_for('dashboard.consulta', val='productos'))
            else:
                flash('Capacidad del almacen '+almacen+' es insuficiente')
                return redirect(url_for('dashboard.consulta', val='productos'))
        except db.IntegrityError:
            print(db.DataError)
#Ruta para eliminar
@bp.route('/eliminar/<int:clave>',methods=('POST',))
def eliminar (clave):
    db = get_db()
    db.execute('DELETE FROM Producto WHERE Clave = ?',(clave,))
    db.commit()
    return redirect(url_for('dashboard.consulta', val='productos'))