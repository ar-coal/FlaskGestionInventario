import sqlite3
from flask import current_app, g
import click


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

#Aqui mandamos a llamar a la base de datos
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

#Aqui cerramos la base de datos
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

#Aqui inicializamos la base de datos desde la carpeta modelos
def init_db():
    db = get_db()

    with current_app.open_resource('modelos/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#Este es un comando el cual es necesario para mandar a llamar el init_db() desde consola
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')