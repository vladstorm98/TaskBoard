from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash
from flask import request
from flask_babel import _
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.forms import LoginForm
from app.auth.forms import RegistrationForm
from app.auth.forms import ResetPasswordRequestForm
from app.auth.forms import ResetPasswordForm
from app.models.user import User
from app.models.profile import Profile
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('desk.get_tasks'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('desk.get_tasks')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('desk.get_tasks'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        user_id = User.query.filter_by(email=form.email.data).first().id
        profile = Profile(first_name=form.first_name.data.title(),
                          last_name=form.last_name.data.title(),
                          user_id=user_id)
        db.session.add(profile)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'), 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'),
                           form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('desk.get_tasks'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash(_('Check your email for the instructions to reset your '
                    'password'), 'success')
        else:
            flash(_("User with this email doesn't exist"), 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('desk.get_tasks'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('desk.get_tasks'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'), 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
