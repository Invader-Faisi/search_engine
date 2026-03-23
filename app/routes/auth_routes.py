from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.user_model import User
from app import db
from app.utils.security import hash_password, verify_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and verify_password(password, user.password_hash):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('search.home'))
        flash("Invalid Credentials", "error")
        return redirect(url_for('search.home'))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = hash_password(password)

        user = User(username=username, email=email, password_hash=hashed_password)

        db.session.add(user)
        db.session.commit()

        flash("Registered successful. Please login", "success")
        return redirect(url_for('search.home'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Good bye. See you again", "success")
    return redirect(url_for('search.home'))
