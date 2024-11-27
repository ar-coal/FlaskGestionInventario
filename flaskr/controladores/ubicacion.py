from flaskr.modelos.db import get_db

import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('ubicacion', __name__, url_prefix='/dashboard/ubicaciones')

#Ruta de registro de datos
@bp.route('/registro',methods=('GET','POST'))
def registrar ():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        db = get_db()
        try:
            db.execute(
                "INSERT INTO Ubicacion (Nombre, Descripcion) VALUES (?, ?)", (nombre, descripcion),
            )
            db.commit()
        except db.IntegrityError:
            error = f"El nombre {nombre} ya está registrado."
        else:
            return redirect(url_for("ubicacion.consulta"))

        flash(error)

    return render_template('ubicacion/form.html',ubi=None)
    
#Ruta que renderiza la tabla
@bp.route('/consulta',methods=('GET', 'POST'))
def consulta ():
    db = get_db()
    if request.method == 'GET':
        ubicaciones =  db.execute('SELECT * FROM Ubicacion').fetchall()
        return render_template('ubicacion/consulta.html',ubicaciones = ubicaciones)
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
        SELECT * FROM Ubicacion    
        {valor} ORDER BY {campo} {desc} {max}
        '''
        ubicaciones = db.execute(query).fetchall()
        return render_template('ubicacion/consulta.html',ubicaciones=ubicaciones)

#Ruta para editar
@bp.route('/editar/<int:clave>',methods=('GET','POST'))
def modificar (clave):
    db = get_db()
    if request.method == 'GET':
        ubi = db.execute("SELECT * FROM Ubicacion WHERE Clave = ? ",(clave,)).fetchone()
        return render_template('ubicacion/form.html',ubi=ubi)
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        try:
            db.execute(
                "UPDATE Ubicacion SET Nombre = ?, Descripcion = ? WHERE Clave = ?", (nombre, descripcion,clave),
            )
            db.commit()
        except db.IntegrityError:
            flash(f"El nombre {nombre} ya está registrado.")
            return redirect(url_for("ubicacion.consulta"))
        else:
            return redirect(url_for("ubicacion.consulta"))

#Ruta q elimina
@bp.route('/eliminar/<int:clave>',methods=('POST',))
def eliminar (clave):
    db = get_db()
    db.execute('DELETE FROM Ubicacion WHERE Clave = ?',(clave,))
    db.commit()
    return redirect(url_for('dashboard.consulta', val='ubicacion'))