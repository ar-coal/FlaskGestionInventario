import functools
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.controladores.auth import login_required
from flaskr.modelos.db import get_db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

#Url que  nos redirecciona inmediatamente a las consultas
@bp.route('/main', methods=('GET', 'POST'))
def main():
    return redirect(url_for('productos.consulta'))

#ruta dinamica para llamar a las consultas de cada controlador
@bp.route('/consulta/<string:val>', methods=('GET', 'POST'))
def consulta(val):
    url = val+'.consulta'
    return redirect(url_for(url))
        
#ruta para los registros
@bp.route('/registro', methods=('GET', 'POST'))
@login_required
def registro():
    return render_template('dashboard/registro.html')




    