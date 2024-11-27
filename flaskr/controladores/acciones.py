from flaskr.modelos.db import get_db

import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('acciones', __name__, url_prefix='/dashboard/acciones')
#Comando para insertar acciones desde cualquier parte del codigo
def insertarAccion (Almacen,Usario,Producto,Accion):
    db = get_db()
    Fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute("INSERT INTO Acciones (Almacen,Usuario,Producto,Accion,Fecha) VALUES (?, ?, ?, ?, ?)",
               (Almacen,Usario,Producto,Accion,Fecha))
    db.commit()  
#Ruta que renderiza la tabla
@bp.route('/consulta',methods=('GET','POST'))
def consulta ():
    db = get_db()
    if request.method == 'GET':
        acciones = db.execute('SELECT a.Almacen,u.Nombre as Usuario,p.Nombre as Producto,a.Accion,a.Fecha FROM Acciones AS a INNER JOIN Usuario AS u ON a.Usuario = u.Clave INNER JOIN Producto AS p ON a.Producto = p.Clave ORDER BY FECHA;').fetchall()
        return render_template('acciones/consulta.html',acciones=acciones)
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
        SELECT a.Almacen AS Almacen, u.Nombre AS Usuario, p.Nombre AS Producto, a.Accion AS Accion, a.Fecha AS Fecha FROM Acciones AS a
        INNER JOIN Usuario AS u ON a.Usuario = u.Clave
        INNER JOIN Producto AS p ON a.Producto = p.Clave 
        {valor} ORDER BY {campo} {desc} {max}
        '''
        acciones = db.execute(query).fetchall()
        return render_template('acciones/consulta.html',acciones=acciones)

        
      
  