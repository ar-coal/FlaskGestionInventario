from flaskr.modelos.db import get_db
from flaskr.controladores.producto import suficiente_inventario
from flaskr.controladores.acciones import insertarAccion

import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('movimientos', __name__, url_prefix='/dashboard/registro')

#ruta para registrar retorna la tabla tambien
@bp.route('/movimientos/<string:val>',methods=('GET',))
def registrar (val):
    db = get_db()
    if val == 'clave':
        value = request.args['clave']
        resultados = db.execute('SELECT Clave, Almacen, Nombre, CantidadDisponible FROM Producto WHERE Clave = ?', (value,)).fetchall()
    elif val == 'nombre':
        value = request.args['nombre']
        resultados = db.execute("SELECT Clave, Almacen, Nombre, CantidadDisponible FROM Producto WHERE Nombre LIKE :valor", {"valor": '%' + value + '%'}).fetchall()
    else:
        resultados = db.execute('SELECT Clave, Almacen, Nombre, CantidadDisponible FROM Producto').fetchall()
    return render_template('movimientos/consulta.html',resultados=resultados)
   

#Ruta para procesar las entradas
@bp.route('/movimientos/entradas/<int:clave>',methods=('GET','POST'))
def entradas (clave):
    tipo="E"
    db = get_db()
    resultado = db.execute('SELECT * FROM Producto WHERE Clave = ?', (clave,)).fetchone()
    if request.method == 'GET':
        return render_template('movimientos/form.html',tipo=tipo, prod=resultado)
    else:
        cantidadOriginal = int(resultado['CantidadDisponible'])
        cantidad = cantidadOriginal + int(request.form['cantidad'])
        try:
            if(suficiente_inventario(cantidad,resultado['Almacen'],clave)):
                db.execute(
                    "UPDATE Producto SET CantidadDisponible = ? WHERE Clave = ?",
                    (cantidad,clave)
                )
                
                db.commit()
                insertarAccion(Almacen=resultado['Almacen'],Producto=clave,Usario=g.user['Clave'],Accion=("Entrada Cantidad:"+str(request.form['cantidad'])))
                
                return redirect(url_for('movimientos.registrar',val='x'))
            else:
                flash('Capacidad del almacen '+ str(resultado['Almacen'])+' es insuficiente')
                return redirect(url_for('movimientos.registrar',val='x'))
        except db.IntegrityError:
            error = f"Ocurrio un error"
                
#Ruta para procesar las salidas
@bp.route('/movimientos/salidas/<int:clave>',methods=('GET','POST'))
def salidas (clave):
    tipo="S"
    db = get_db()
    resultado = db.execute('SELECT * FROM Producto WHERE Clave = ?', (clave,)).fetchone()
    if request.method == 'GET':
        return render_template('movimientos/form.html',tipo=tipo, prod=resultado)
    else:
        cantidadOriginal = int(resultado['CantidadDisponible'])
        cantidad = cantidadOriginal - int(request.form['cantidad'])
        try:
            if(suficiente_inventario(cantidad,resultado['Almacen'],clave)):
                db.execute(
                    "UPDATE Producto SET CantidadDisponible = ? WHERE Clave = ?",
                    (cantidad,clave)
                )
                db.commit()
                insertarAccion(Almacen=resultado['Almacen'],Producto=clave,Usario=g.user['Clave'],Accion=("Salida Cantidad:"+str(request.form['cantidad'])))

                return redirect(url_for('movimientos.registrar',val='x'))
            else:
                flash('Capacidad del almacen '+ str(resultado['Almacen']) +' es insuficiente')
                return redirect(url_for('movimientos.registrar',val='x'))
        except db.IntegrityError:
            error = f"Ocurrio un error"


#Ruta para procesar los cambios
@bp.route('/movimientos/cambio/<int:clave>',methods=('GET','POST'))
def cambio (clave):
    tipo="C"
    db = get_db()
    producto = db.execute('SELECT * FROM Producto WHERE Clave = ?', (clave,)).fetchone()
    
    if request.method == 'GET':
        almacenes = db.execute(
        'SELECT a.Clave,u.Nombre,a.Capacidad FROM Almacen AS a INNER JOIN Ubicacion AS u ON a.Ubicacion = u.Clave;').fetchall()
        return render_template('movimientos/form.html',tipo=tipo, prod=producto, almacenes=almacenes)
    else:
        #Funcion revisa si hay suficiente espacio antes de mandar el cambio,
        #En caso de que si haya, revisa si hay uno de nombre igual y le añade la cantidad que se le está enviando en el cambio
        #Sinó crea un nuevo registro en ese almacen
        cantidadOrigen = int(producto['CantidadDisponible']) -  int(request.form['cantidad'])
        cantidadDestino = int(request.form['cantidad'])
        almacenOrigen = request.form['almacenOrg']
        almacenDestino = request.form['almacenDes']
        productoDestino = db.execute('SELECT * FROM Producto WHERE Nombre = ? AND Almacen = ?', (producto['Nombre'],almacenDestino,)).fetchone()
        try:
            if(suficiente_inventario(cantidadDestino,almacenDestino,None)):
                db.execute(
                    "UPDATE Producto SET CantidadDisponible = ? WHERE Clave = ? AND Almacen = ?",
                    (cantidadOrigen,clave,almacenOrigen)
                )
                db.commit()
                insertarAccion(Almacen=almacenOrigen,Producto=clave,Usario=g.user['Clave'],Accion=("Cambio "+str(almacenOrigen)+"-"+str(almacenDestino))+" Cantidad:"+str(cantidadDestino))
                if productoDestino == None:
                    db.execute(
                    "INSERT INTO Producto (Almacen,Categoria,Proveedor,Nombre,FechaOrden,FechaCaducidad,CantidadDisponible,CantidadMinima) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (almacenDestino,producto["Categoria"],producto["Proveedor"],producto["Nombre"],producto["FechaOrden"],producto["FechaCaducidad"],cantidadDestino,producto["CantidadMinima"])
                    )
                else:
                    cantidadDestino = cantidadDestino + int(productoDestino['CantidadDisponible'])
                    db.execute(
                    "UPDATE Producto SET CantidadDisponible = ? WHERE Clave = ? AND Almacen = ?",
                    (cantidadDestino,productoDestino['Clave'],almacenDestino)
                )
                db.commit()
                
                insertarAccion(Almacen=almacenDestino,Producto=clave,Usario=g.user['Clave'],Accion=("Cambio "+str(almacenOrigen)+"->"+str(almacenDestino))+" Cantidad:"+str(cantidadDestino))
                return redirect(url_for('movimientos.registrar',val='x'))
            else:
                flash('Capacidad del almacen '+ str(almacenDestino) +' es insuficiente')
                return redirect(url_for('movimientos.registrar',val='x'))
        except db.IntegrityError:
            error = f"Ocurrio un error"