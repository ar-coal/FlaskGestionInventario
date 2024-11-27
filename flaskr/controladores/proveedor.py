from flaskr.modelos.db import get_db

import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('proveedor', __name__, url_prefix='/dashboard/proveedores')
#Ruta de registr
@bp.route('/registro',methods=('GET','POST'))
def registrar ():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        db = get_db()
        try:
            db.execute(
                "INSERT INTO Proveedor (Nombre, Telefono) VALUES (?, ?)", (nombre, telefono),
            )
            db.commit()
        except db.IntegrityError:
            error = f"El nombre {nombre} ya está registrado."
        else:
            return redirect(url_for("proveedor.consulta"))

        flash(error)

    return render_template('proveedor/form.html',prov=None)
    
#Ruta que renderiza la tabla
@bp.route('/consulta',methods=('GET','POST'))
def consulta ():
    db = get_db()
    if request.method == 'GET':
        proveedores =  db.execute('SELECT * FROM Proveedor').fetchall()
        return render_template('proveedor/consulta.html',proveedores = proveedores)
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
        SELECT * FROM Proveedor 
        {valor} ORDER BY {campo} {desc} {max}
        '''
        proveedores = db.execute(query).fetchall()
        return render_template('proveedor/consulta.html',proveedores=proveedores)

#Ruta para modificar
@bp.route('/editar/<int:clave>',methods=('GET','POST'))
def modificar (clave):
    db = get_db()
    if request.method == 'GET':
        prov = db.execute("SELECT * FROM proveedor WHERE Clave = ? ",(clave,)).fetchone()
        return render_template('proveedor/form.html',prov=prov)
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        try:
            db.execute(
                "UPDATE proveedor SET Nombre = ?, Telefono = ? WHERE Clave = ?", (nombre, telefono,clave),
            )
            db.commit()
        except db.IntegrityError:
            flash(f"El nombre {nombre} ya está registrado.")
            return redirect(url_for("proveedor.consulta"))
        else:
            return redirect(url_for("proveedor.consulta"))


#Ruta para borrar
@bp.route('/eliminar/<int:clave>',methods=('POST',))
def eliminar (clave):
    db = get_db()
    db.execute('DELETE FROM Proveedor WHERE Clave = ?',(clave,))
    db.commit()
    return redirect(url_for('dashboard.consulta', val='proveedor'))