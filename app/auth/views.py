import random
from datetime import datetime

import requests
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, login_required, logout_user, current_user

from app import db
from app.auth import auth_bp, keys
from app.auth.forms import RegisterForm, LoginForm, VerifyCodeForm
from app.auth.keys import client
from app.auth.models import User


@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            db.session.add(User(username=form.name.data,
                                phone_number=form.phone_number.data,
                                email=form.email.data,
                                password=form.password.data))
            db.session.commit()
            flash(f'Account created for {form.name.data}!', category='success')
        except:
            db.session.rollback()

        return redirect(url_for('auth.login', username=form.email.data))

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).filter_by(email=form.email.data).first()

            if user and user.email == form.email.data:
                from pytz import utc
                now = datetime.now(utc)

                failed_attempts = session.get('failed_attempts', 0)
                last_failed_attempt = session.get('last_failed_attempt', None)

                if (
                        last_failed_attempt
                        and (now - last_failed_attempt).total_seconds() < 60  # Блокування на 1 хвилину
                ):
                    session.pop('failed_attempts', 0)
                    flash('Account is locked. Please try again later.', category='warning')
                    return redirect(url_for('auth.login'))

                if user.verify_password(form.password.data):
                    session.pop('failed_attempts', 0)
                    session.pop('last_failed_attempt', None)
                    session["user_id"] = user.id
                    return redirect(url_for('auth.send_code'))
                else:
                    session['failed_attempts'] = failed_attempts + 1
                    flash('Login unsuccessful. Please check username and password', category='warning')

                    if failed_attempts >= 10:
                        session['last_failed_attempt'] = now
                        print(session['failed_attempts'])
                        flash('You have exceeded the maximum login attempts. Your account is locked for 1 minute.',
                              category='warning')
                        return redirect(url_for('auth.login'))

            else:
                flash('User does not exist, please register your account', category='warning')
                return redirect(url_for('auth.register'))

    return render_template('login.html', form=form)


@auth_bp.route('/send_code', methods=['GET'])
def send_code():
    user = db.session.query(User).filter_by(id=session["user_id"]).first()

    if user:
        code = ''.join(str(random.randint(0, 9)) for _ in range(6))

        message = client.messages.create(
            body=f'Your verification code is: {code}',
            from_=keys.twilio_number,
            to=user.phone_number
        )

        session['verification_code'] = code

        flash('Verification code sent to your phone number.', category='success')
        return redirect(url_for('auth.verify_code'))


@auth_bp.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    form = VerifyCodeForm()

    if form.validate_on_submit():
        user = db.session.query(User).filter_by(id=session["user_id"]).first()
        user_code = form.code.data

        if 'verification_code' in session and session['verification_code'] == user_code:
            # Code is correct, you can proceed with authentication
            login_user(user)
            session['user_id'] = None
            session['logged_in'] = True
            flash('Authentication successful', category='success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Incorrect verification code')

    return render_template('verify_code.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    flash('You have been logged out', category='success')
    return redirect(url_for('auth.login'))


@auth_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", username=current_user)
