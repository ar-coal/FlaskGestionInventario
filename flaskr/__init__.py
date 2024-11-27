import os
from flask import Flask
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .controladores import movimientos
from flaskr.modelos.db import get_db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # a simple page that says hello
    @app.before_request
    def load_logged_in_user():
        clave_usuario = session.get('clave_usuario')

        if clave_usuario is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM Usuario WHERE Clave = ?', (clave_usuario,)
            ).fetchone()
            

    @app.route('/')
    def index():
        if g.user is None:
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('dashboard.main'))
    
    from .modelos import db
    db.init_app(app)
    
    from .controladores import auth,dashboard,producto,acciones,ubicacion,almacen,categoria,proveedor
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(producto.bp)
    app.register_blueprint(movimientos.bp)
    app.register_blueprint(acciones.bp)
    app.register_blueprint(ubicacion.bp)
    app.register_blueprint(almacen.bp)
    app.register_blueprint(categoria.bp)
    app.register_blueprint(proveedor.bp)

    return app