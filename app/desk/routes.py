from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import render_template
from flask import flash
from flask import g
from flask import current_app
from flask_login import login_required
from flask_login import current_user
from flask_babel import _
from calendar import Calendar
from datetime import datetime

from app import db
from app import get_locale
from app.models.task import Task
from app.models.profile import Profile
from app.desk import bp
from app.desk.forms import *
from app.search import add_to_index

c = Calendar()


@bp.before_app_request
def before_request():
    # Task.reindex()
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.get_tasks()
    total = len(tasks)
    page = request.args.get('page', 1, type=int)
    next_url = url_for('desk.get_tasks', q=page, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('desk.get_tasks', q=page, page=page - 1) \
        if page > 1 else None
    return render_template('desk/task_board.html', title=_('Records board'),
                           tasks=tasks, next_url=next_url, prev_url=prev_url)


@bp.route('/', methods=['POST'])
@login_required
def update_task_board():
    if 'delete_id' in request.form:
        id = request.form['delete_id']
        Task.delete_task(id)
    elif 'archive' in request.form:
        id = request.form['archive']
        Task.transfer_task(id)
    return redirect(url_for('desk.get_tasks'))


@bp.route('/select_client', methods=['GET', 'POST'])
@login_required
def get_client_type():
    if 'existing_client' in request.form:
        return redirect(url_for('desk.new_client_task'))
    elif 'new_client' in request.form:
        return redirect(url_for('desk.new_common_task'))
    return render_template('desk/select_client.html', title=_('Select client'))


@bp.route('/new_client_task', methods=['POST', 'GET'])
@login_required
def new_client_task():
    form = ClientTaskForm()
    form.set_choices()
    if form.validate_on_submit():
        if form.day.data > 31 or form.day.data < 1:
            flash(_('Invalid input'), 'error')
            return redirect(url_for('desk.new_client_task'))
        if form.day.data < 10:
            form.day.data = '0' + str(form.day.data)
        if int(form.month.data) < 10:
            form.month.data = '0' + str(form.month.data)
        date = datetime(int(form.year.data), int(form.month.data),
                        int(form.day.data), int(form.time.data[:2]),
                        int(form.time.data[-2:])).strftime("%Y-%m-%d %H:%M")
        client = Profile.query.get(form.client.data)
        name = client.first_name + ' ' + client.last_name
        Task.create_task(title=form.title.data, address=client.address,
                         note=form.note.data, price=client.price, date=date,
                         client_id=form.client.data, name=name)
        Profile.update_last_order(form.client.data, date)
        return redirect(url_for('desk.get_tasks'))
    return render_template('desk/add_client_task.html', title=_('New Record'),
                           form=form)


@bp.route('/new_common_task', methods=['POST', 'GET'])
@login_required
def new_common_task():
    form = TaskForm()
    if form.validate_on_submit():
        if form.day.data > 31 or form.day.data < 1:
            flash(_('Invalid input'), 'error')
            return redirect(url_for('desk.new_common_task'))
        if form.day.data < 10:
            form.day.data = '0' + str(form.day.data)
        if int(form.month.data) < 10:
            form.month.data = '0' + str(form.month.data)
        date = datetime(int(form.year.data), int(form.month.data),
                        int(form.day.data), int(form.time.data[:2]),
                        int(form.time.data[-2:])).strftime("%Y-%m-%d %H:%M")
        Task.create_task(title=form.title.data, address=form.address.data,
                         note=form.note.data, price=form.price.data + ' грн',
                         date=date)
        return redirect(url_for('desk.get_tasks'))
    return render_template('desk/add_common_task.html', title=_('New Record'),
                           form=form)


@bp.route('/archive', methods=['GET'])
@login_required
def get_archive():
    tasks = Task.get_tasks(in_progress=False)
    return render_template('desk/archive.html', title=_('Records archive'),
                           tasks=tasks)


@bp.route('/archive', methods=['POST'])
@login_required
def archive():
    if 'desk' in request.form:
        id = request.form['desk']
        Task.transfer_task(id)
    return redirect(url_for('desk.get_archive'))


@bp.route('/calendar', methods=['GET'])
@login_required
def calendar_settings():
    if 'year' not in session or 'month' not in session:
        form = CalendarForm()
        return render_template('desk/set_calendar.html', form=form,
                               title=_('Calendar settings'))
    return redirect(url_for('desk.get_calendar', year=session['year'],
                            month=session['month']))


@bp.route('/calendar', methods=['POST'])
@login_required
def set_calendar():
    form = CalendarForm()
    if form.validate_on_submit():
        session['year'] = form.year.data
        session['month'] = form.month.data
    return redirect(url_for('desk.get_calendar', year=session['year'],
                            month=session['month']))


@bp.route('/calendar/<year>/<month>', methods=['GET'])
@login_required
def get_calendar(year, month):
    if 'year' not in session or 'month' not in session:
        return redirect(url_for('desk.get_calendar_settings'))
    year_days = c.itermonthdates(year=int(year), month=int(month))
    month_days = [[day.day, day.weekday()] for day in year_days
                  if day.month == int(month)]
    for day in month_days:
        if day[0] < 10:
            day[0] = '0' + str(day[0])
    tasks = Task.get_tasks()
    archives = Task.get_tasks(in_progress=False)
    if int(month) < 10 and len(str(month)) == 1:
        month = '0' + str(month)
    return render_template('desk/calendar.html', title=_('Calendar'),
                           days=month_days, year=year, month=month,
                           tasks=tasks, archives=archives)


@bp.route('/calendar/<year>/<month>', methods=['POST'])
@login_required
def calendar(year, month):
    if 'last' in request.form:
        month = int(month) - 1
        if month <= 0:
            month = 12
            year = int(year) - 1
    elif 'next' in request.form:
        month = int(month) + 1
        if month >= 13:
            month = 1
            year = int(year) + 1
    session['year'] = year
    session['month'] = month
    return redirect(url_for('desk.get_calendar', year=session['year'],
                            month=session['month']))


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('desk.get_tasks'))
    page = request.args.get('page', 1, type=int)
    tasks, total = Task.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('desk.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('desk.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), tasks=tasks,
                           next_url=next_url, prev_url=prev_url)
