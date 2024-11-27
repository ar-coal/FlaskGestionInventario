from flaskr.modelos.db import get_db

import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('almacen', __name__, url_prefix='/dashboard/almacen')

#Ruta para realizar registros
@bp.route('/registro',methods=('GET','POST'))
def registrar ():
    db = get_db()
    if request.method == 'GET':
        ubicaciones = db.execute('SELECT * FROM Ubicacion').fetchall()
        return render_template('almacen/form.html',ubicaciones=ubicaciones,alm=None)
    if request.method == 'POST':
        ubicacion = request.form['ubicacion']
        capacidad = request.form['capacidad']
        try:
            db.execute(
                "INSERT INTO Almacen (Ubicacion, Capacidad) VALUES (?, ?)", (ubicacion, capacidad),
            )
            db.commit()
        except db.IntegrityError:
            error = f"error"
        else:
            return redirect(url_for("almacen.consulta"))
        flash(error)

    
    
#Ruta para hacer la tabla
@bp.route('/consulta',methods=('GET','POST'))
def consulta ():
    db = get_db()
    if request.method == 'GET':
        almacenes =  db.execute('SELECT a.Clave AS Clave ,u.Nombre AS Ubicacion, a.Capacidad AS Capacidad FROM Almacen AS a INNER JOIN Ubicacion AS u WHERE a.Ubicacion = u.Clave').fetchall()
        return render_template('almacen/consulta.html',almacenes = almacenes)
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
        #Buscamos que en lugar del ID se muestre el nombre de la ubicacion
        query = f'''
        SELECT a.Clave AS Clave ,u.Nombre AS Ubicacion, a.Capacidad AS Capacidad FROM Almacen AS a
        INNER JOIN Ubicacion AS u ON a.Ubicacion = u.Clave   
        {valor} ORDER BY {campo} {desc} {max}
        '''
        almacenes = db.execute(query).fetchall()
        return render_template('almacen/consulta.html',almacenes=almacenes)

#Aqui enviamos los objetos a actualizar
@bp.route('/editar/<int:clave>',methods=('GET','POST'))
def modificar (clave):
    db = get_db()
    if request.method == 'GET':
        alm = db.execute("SELECT * FROM Almacen WHERE Clave = ? ",(clave,)).fetchone()
        ubicaciones = db.execute('SELECT * FROM Ubicacion').fetchall()
        return render_template('almacen/form.html',ubicaciones=ubicaciones,alm=alm)
    if request.method == 'POST':
        ubicacion = request.form['ubicacion']
        capacidad = request.form['capacidad']
        try:
            db.execute(
                "UPDATE Almacen SET Ubicacion = ?, Capacidad = ? WHERE Clave = ?", (ubicacion, capacidad,clave),
            )
            db.commit()
        except db.IntegrityError:
            flash(f"Error")
            return redirect(url_for("almacen.consulta"))
        else:
            return redirect(url_for("almacen.consulta"))


#Ruta para borrar
@bp.route('/eliminar/<int:clave>',methods=('POST',))
def eliminar (clave):
    db = get_db()
    db.execute('DELETE FROM Almacen WHERE Clave = ?',(clave,))
    db.commit()
    return redirect(url_for('dashboard.consulta', val='almacen'))