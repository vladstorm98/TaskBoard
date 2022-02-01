from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_babel import _
from flask_login import login_required

from app.users import bp
from app.models.profile import Profile
from app.models.user import User
from app.models.task import Task
from app.users.forms import ClientForm


@bp.route('/', methods=['GET'])
@login_required
def clients():
    clients_list = Profile.query.all()
    return render_template('users/clients.html', clients=clients_list,
                           title=_('Clients'))


@bp.route('/', methods=['POST'])
@login_required
def get_profile():
    if 'more' in request.form:
        return redirect(url_for('users.profile', id=request.form['more']))


@bp.route('/<id>', methods=['GET'])
@login_required
def profile(id):
    client = Profile.query.get(id)
    name = client.first_name + ' ' + client.last_name
    last_visit = User.query.get(id).last_seen.strftime("%Y-%m-%d %H:%M") \
        if User.query.get(id) else '-'
    history = [task.date for task in client.tasks.order_by(Task.date.desc())]
    return render_template('users/profile.html', client=client, title=name,
                           last_visit=last_visit, history=history)

@bp.route('/<id>', methods=['POST'])
@login_required
def delete_profile(id):
    if 'delete_profile' in request.form:
        Profile.delete_profile(id)
        return redirect(url_for('users.clients'))

@bp.route('/new_client', methods=['POST', 'GET'])
@login_required
def new_client():
    form = ClientForm()
    if form.validate_on_submit():
        Profile.create_client(first_name=form.first_name.data,
                              last_name=form.last_name.data,
                              number=form.number.data,
                              price=form.price.data + ' грн',
                              address=form.address.data,
                              about_client=form.about_client.data)
        return redirect(url_for('users.clients'))
    return render_template('users/create_client.html', title=_('New Client'),
                           form=form)
