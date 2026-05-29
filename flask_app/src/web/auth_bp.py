import logging

from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask import current_app as app

from src.web.forms import LoginForm, RegisterForm

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _auth_service():  # type: ignore[no-untyped-def]
    return app.extensions["auth_service"]


@auth_bp.route("/register", methods=["GET", "POST"])
def register():  # type: ignore[return]
    form = RegisterForm()
    if form.validate_on_submit():
        user = _auth_service().register(form.username.data, form.password.data)
        if user is None:
            flash("Такой логин уже занят.", "danger")
        else:
            flash("Регистрация успешна! Войдите.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():  # type: ignore[return]
    form = LoginForm()
    if form.validate_on_submit():
        user = _auth_service().authenticate(form.username.data, form.password.data)
        if user is None:
            flash("Неверный логин или пароль.", "danger")
        else:
            session["user_id"]   = user.id
            session["username"]  = user.username
            return redirect(url_for("game.index"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из игры.", "info")
    return redirect(url_for("auth.login"))