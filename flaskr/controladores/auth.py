import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.modelos.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

#Ruta del tutorial para acceder al form
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        nombre = request.form['nombre']
        puesto = request.form['puesto']
        
        db = get_db()
        error = None

        if not usuario:
            error = 'Usuario es obligatorio.'
        elif not contrasena:
            error = 'Contraseña es obligatorio.'
        elif not nombre:
            error = 'Nombre es obligatorio.'
        elif not puesto:
            error = 'Puesto es obligatorio.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO Usuario (Usuario, Contrasena, Nombre, Puesto) VALUES (?, ?, ?, ?)",
                    (usuario, generate_password_hash(contrasena), nombre, puesto),
                )
                db.commit()
            except db.IntegrityError:
                error = f"El usuario {usuario} ya está registrado."
            else:
                if g.user == None:
                    return redirect(url_for("auth.login"))
                else:
                    return redirect(url_for("auth.consulta"))

        flash(error)

    return render_template('auth/register.html',usr = None)

#Aqui hacemos login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Usuario WHERE Usuario = ?', (usuario,)
        ).fetchone()
        

        if user is None:
            error = 'Usuario incorrecto.'
        elif not check_password_hash(user['Contrasena'], contrasena):
            error = 'Contraseña incorrecta.'

        if error is None:
            session.clear()
            session['clave_usuario'] = user['Clave']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

#Renderizar la tabla de usuarios
@bp.route('/consulta',methods = ('GET','POST'))
def consulta():
    db = get_db()
    if request.method == 'GET':
        usuarios = db.execute("SELECT * from Usuario")
        return render_template("auth/consulta.html", usuarios=usuarios) 
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
        SELECT * from Usuario 
        {valor} ORDER BY {campo} {desc} {max}
        '''
        almacenes = db.execute(query).fetchall()
        return render_template('almacen/consulta.html',almacenes=almacenes)

#Renderizar el form con datos para editar
@bp.route('/editar/<int:clave>',methods=('GET', 'POST'))
def modificar(clave):
    db = get_db()
    if request.method == 'GET':
        usr = db.execute("SELECT * FROM Usuario WHERE Clave = ?",(clave,)).fetchone()
        return render_template('auth/register.html',usr=usr)
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        nombre = request.form['nombre']
        puesto = request.form['puesto']
        try:
            db.execute(
                "UPDATE Usuario SET Usuario = ?, Contrasena = ?, Nombre = ?, Puesto = ? WHERE Clave = ?",
                (usuario, contrasena, nombre, puesto,clave),
            )
            db.commit()
        except db.IntegrityError:
            flash(f"El usuario: {usuario} ya está registrado.")
            return redirect(url_for("auth.consulta"))
        else:
            return redirect(url_for("auth.consulta"))

    
#Renderizar la tabla de usuarios
@bp.route('/eliminar/<int:clave>', methods=('GET', 'POST'))
def eliminar(clave):
    db = get_db()
    db.execute("DELETE FROM Usuario WHERE Clave = ? ",(clave,))
    db.commit()
    return redirect(url_for("auth.consulta"))

#Revisa antes de iniciar si ya estamos logueados y asigna el usuario a global
@bp.before_app_request
def load_logged_in_user():
    clave_usuario = session.get('clave_usuario')

    if clave_usuario is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Usuario WHERE Clave = ?', (clave_usuario,)
        ).fetchone()
  
#Ruta de logout       
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#Comando para revisar si ya estamos loguqeados
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view