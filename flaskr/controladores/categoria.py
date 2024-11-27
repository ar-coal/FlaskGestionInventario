from flaskr.modelos.db import get_db

import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('categoria', __name__, url_prefix='/dashboard/categorias')

#Ruta para realizar registros
@bp.route('/registro',methods=('GET','POST'))
def registrar ():
    if request.method == 'POST':
        clave = request.form['clave']
        descripcion = request.form['descripcion']
        db = get_db()
        try:
            db.execute(
                "INSERT INTO categoria (Clave, Descripcion) VALUES (?, ?)", (clave, descripcion),
            )
            db.commit()
        except db.IntegrityError:
            error = f"La clave {clave} ya está registrado."
        else:
            return redirect(url_for("categoria.consulta"))

        flash(error)

    return render_template('categoria/form.html',cat=None)
    

#Ruta para hacer la tabla
@bp.route('/consulta',methods=('GET','POST'))
def consulta ():
    db = get_db()
    if request.method == 'GET':
        categorias =  db.execute('SELECT * FROM Categoria').fetchall()
        return render_template('categoria/consulta.html',categorias = categorias)
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
        SELECT * FROM Categoria 
        {valor} ORDER BY {campo} {desc} {max}
        '''
        categorias = db.execute(query).fetchall()
        return render_template('categoria/consulta.html',categorias=categorias)

#Aqui enviamos los objetos a actualizar
@bp.route('/editar/<string:clave>',methods=('GET','POST'))
def modificar (clave):
    db = get_db()
    if request.method == 'GET':
        cat = db.execute("SELECT * FROM categoria WHERE Clave = ? ",(clave,)).fetchone()
        return render_template('categoria/form.html',cat=cat)
    if request.method == 'POST':
        claven = request.form['clave']
        descripcion = request.form['descripcion']
        try:
            db.execute(
                "UPDATE Categoria SET Clave = ?, Descripcion = ? WHERE Clave = ?", (claven, descripcion,clave),
            )
            db.commit()
        except db.IntegrityError:
            flash(f"La clave {claven} ya está registrado.")
            return redirect(url_for("categoria.consulta"))
        else:
            return redirect(url_for("categoria.consulta"))


#Ruta para borrar
@bp.route('/eliminar/<string:clave>',methods=('POST',))
def eliminar (clave):
    db = get_db()
    db.execute('DELETE FROM Categoria WHERE Clave = ?',(clave,))
    db.commit()
    return redirect(url_for('dashboard.consulta', val='categoria'))