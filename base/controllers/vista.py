from flask import Blueprint, render_template, redirect, request, session, flash, url_for, g 
from datetime import datetime, date


from base.models.asesorias import Asesoria
from base.models.usuario import Usuario

bp = Blueprint('vista', __name__, url_prefix='/vista')

from base.controllers.usuarios import login_required

@bp.route('/view')
def view():
    return render_template('auth.html')

@bp.route('/new')
@login_required
def new():
    
    form = {"id": session['usuario_id']}
    usuario = Usuario.obtener_por_id(form)

    usuarios = Usuario.get_all_except_current(form)

    future_date = datetime.now().date() 

    return render_template('create.html', usuario=usuario, usuarios=usuarios, future_date=future_date)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    
    if not Asesoria.validar_asesoria(request.form):
        return redirect('/new')
    
    Asesoria.save(request.form)
    flash('Asesoría creada exitosamente', 'success')
    return redirect(url_for('usuarios.dashboard'))

@bp.route('/edit/<int:id>')
@login_required
def edit(id):

    
    form = {"id": session['usuario_id']}
    usuario = Usuario.obtener_por_id(form)

    data_asesoria = {"id": id}
    asesoria = Asesoria.get_by_id(data_asesoria)

    if asesoria.usuario_id != session['usuario_id']:
        return redirect(url_for('usuarios.dashboard'))    
        # Obtener tutores de la base de datos
    usuarios = Usuario.obtener_todos()  # Cambia esto según cómo obtengas los tutores
    tutor_actual = Usuario.obtener_por_id({"id": asesoria.tutor_id}) if asesoria.tutor_id else None

    puede_cambiar_tutor = True  # Cambia según tu lógica

    return render_template('editar.html', 
                            usuario=usuario, 
                            asesoria=asesoria, 
                            usuarios=usuarios, 
                            tutor_actual=tutor_actual, 
                            puede_cambiar_tutor=puede_cambiar_tutor,)




@bp.route('/ver/<int:id>', methods=['GET'])
@login_required
def ver(id):
    # Utilizamos g.user para acceder al usuario logueado
    usuario = g.user  # Aquí obtenemos el usuario logueado directamente

    # Consultamos la asesoría usando el ID proporcionado
    data_asesoria = {"id": id}
    asesoria = Asesoria.get_by_id_with_tutor(data_asesoria)

    # Verificamos si el usuario logueado es el solicitante
    puede_cambiar_tutor = asesoria.usuario_id == g.user.id
    
    # Obtenemos todos los usuarios excepto el solicitante
    usuarios = Usuario.get_all_except_current({"id": g.user.id})

    # Obtenemos el nombre del tutor actual
    tutor_actual = Usuario.obtener_por_id({"id": asesoria.tutor_id}) if asesoria.tutor_id else None

    # Pasamos la información a la plantilla
    return render_template('ver.html', usuario=usuario, asesoria=asesoria, puede_cambiar_tutor=puede_cambiar_tutor, usuarios=usuarios, tutor_actual=tutor_actual)

@bp.route('/update_tutor_ver/<int:id>', methods=['POST'])
def update_tutor_ver(id):
    return actualizar_tutor(id, 'ver')

@bp.route('/update_tutor_editar/<int:id>', methods=['POST'])
def update_tutor_editar(id):
    return actualizar_tutor(id, 'editar')
def actualizar_tutor(id, pagina):
    if not g.user:
        return redirect('/logout')

    nuevo_tutor_id = request.form['tutor_id']
    data = {
        "id": id,
        "tutor_id": nuevo_tutor_id
    }
    Asesoria.update_tutor(data)  # Verifica que este método realmente actualice el tutor

    # Redirección según la página solicitada
    if pagina == 'ver':
        return redirect(url_for('vista.ver', id=id))
    elif pagina == 'editar':
        return redirect(url_for('usuarios.dashboard', id=id))

@bp.route('/update', methods=['POST'])
@login_required
def update():

    nueva_asesoria_id = request.form['id']
    form = {
        "id": nueva_asesoria_id,
        "tema": request.form['tema'],
        "fecha": request.form['fecha'],
        "duracion": request.form['duracion'],
        "nota": request.form['nota'],
        "tutor_id": request.form['tutor_id']
    }
    
    # Validar los datos del formulario
    if not Asesoria.validar_asesoria(request.form):
        return redirect('/edit/asesoria/' + request.form['id'])
    
    # Llamar al método de actualización con los datos del formulario
    Asesoria.update_asesoria(request.form)
    
    # Redirigir al dashboard después de actualizar
    return redirect(url_for('usuarios.dashboard', id=session['usuario_id']))
    
@bp.route('/delete/<int:id>')
@login_required
def delete(id):

    # Eliminar la asesoría
    data_asesoria = {"id": id}
    Asesoria.delete(data_asesoria)

    # Redirigir al dashboard después de eliminar
    return redirect(url_for('usuarios.dashboard'))

