# project/server/user/views.py

from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from project.server import bcrypt, db
from project.server.main.views import get_child_weekly_total, get_start_of_week
from project.server.models import Child, Chore, CompletedChore, User, WeeklyTotals
from project.server.user.forms import (
    AddAdminForm,
    AddChildForm,
    AddChoreForm,
    ApprovePaymentForm,
    DeleteChoreForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
)

user_blueprint = Blueprint("user", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            flash("You must be an admin to view this page.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function


@user_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(user_name=form.user_name.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash("Thank you for registering.", "success")
        return redirect(url_for("main.home"))

    return render_template("user/register.html", form=form)


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first()
        if user and bcrypt.check_password_hash(
            user.password, request.form["password"]
        ):
            login_user(user)
            flash("You are logged in. Welcome!", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("user/login.html", form=form)
    return render_template("user/login.html", title="Please Login", form=form)


@user_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out. Bye!", "success")
    return redirect(url_for("user.login"))


@user_blueprint.route("/setup", methods=["GET", "POST"])
@login_required
@admin_required
def setup():
    form_child = AddChildForm(request.form)
    if request.method == 'POST' and form_child.validate_on_submit():
        child = Child(name=form_child.name.data)
        db.session.add(child)
        db.session.commit()
        flash(f"Child {child.name} added.")
        return redirect(url_for("user.setup"))

    children = Child.query.all()
    chores = Chore.query.all()

    form_chore = AddChoreForm(request.form)
    if request.method == 'POST' and form_chore.validate_on_submit():
        chores = Chore(chore=form_chore.chore.data, value=form_chore.value.data)
        db.session.add(chores)
        db.session.commit()
        flash(f"Chore {chores.chore} added.")
        return redirect(url_for("user.setup"))

    form_delete = DeleteChoreForm(request.form)
    last_10_chores = Chore.query.order_by(Chore.id.desc()).limit(10)
    if request.method == 'POST' and form_delete.validate_on_submit():
        chore_id = form_delete.chore_id.data
        chore_to_delete = CompletedChore.query.get(chore_id)
        if chore_to_delete:
            chore_value = db.session.query(Chore.value).filter(Chore.id == chore_to_delete.chore_id).scalar()

            weekly_total = db.session.query(WeeklyTotals).filter(
                WeeklyTotals.child_id == chore_to_delete.child_id,
                WeeklyTotals.week_start == chore_to_delete.completed_on - timedelta(
                    days=chore_to_delete.completed_on.weekday()
                    )
            ).first()

            if weekly_total and chore_value:
                # Subtract the chore value from the weekly total
                weekly_total.total -= chore_value
                db.session.commit()

        db.session.delete(chore_to_delete)
        db.session.commit()
        flash("Chore deleted.")
        return redirect(url_for("user.setup"))

    form_admin = AddAdminForm(request.form)
    if request.method == 'POST' and form_admin.validate_on_submit():
        user = User.query.filter_by(user_name=form_admin.user_name.data).first()
        if user:
            user.admin = True
            db.session.commit()
            flash(f"{user.user_name} is now an admin.")
        else:
            flash(f"User {form_admin.user_name.data} not found.", "danger")
        return redirect(url_for("user.setup"))

    return render_template("user/setup.html",
                           form_child=form_child,
                           children=children,
                           chores=chores,
                           form_chore=form_chore,
                           form_delete=form_delete,
                           last_10_chores=last_10_chores,
                           form_admin=form_admin,
                           )


@user_blueprint.route("/approval/", methods=["GET", "POST"])
@login_required
@admin_required
def approval():
    this_week = get_start_of_week()
    # Get the selected start_of_week from the frontend
    start_of_week_str = request.args.get('start_of_week', None)

    if start_of_week_str:
        start_of_week = datetime.strptime(start_of_week_str, "%Y-%m-%d")
    else:
        # Default to the current week's Monday if no input
        start_of_week = get_start_of_week()

    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    weekly_totals = db.session.query(WeeklyTotals).all()

    running_total = {}
    for child in weekly_totals:
        if child.child_id not in running_total:
            kid = Child.query.get(child.child_id)
            running_total[child.child_id] = (kid.name, get_child_weekly_total(
                child.child_id,
                start_of_week,
                end_of_week,
                ))

    approved = db.session.query(WeeklyTotals).filter_by(week_start=start_of_week.date()).all()
    approved_this_week = {}
    for child in approved:
        if child.child_id not in approved:
            kid = Child.query.get(child.child_id)
            approved_by_user = User.query.get(child.approved_by)
            child = WeeklyTotals.query.get(child.id)
            approved_this_week[child.child_id] = (kid.name,
                                                  approved_by_user.user_name if approved_by_user else "Not Approved",
                                                  f"on {child.approved_on}" if child.approved_on else "",)

    form = ApprovePaymentForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        child_name = form.child.data
        child = Child.query.filter_by(id=child_name).first()
        if child:
            weekly_total = WeeklyTotals.query.filter_by(child_id=child.id, week_start=start_of_week.date()).first()
            if weekly_total:
                weekly_total.approved_by = current_user.id
                weekly_total.approved_on = datetime.now()
                db.session.commit()
                flash(f"{child.name}'s allowance has been approved by {current_user.user_name}.")
            else:
                flash(f"No weekly total found for {child.name}.", "danger")
        else:
            flash(f"User {child_name} not found.", "danger")
        return redirect(url_for("user.approval"))

    return render_template("main/approval.html",
                           running_total=running_total,
                           start_of_week=start_of_week,
                           this_week=this_week,
                           form=form,
                           approved_this_week=approved_this_week,
                           )


@user_blueprint.route("/change_password/", methods=["GET", "POST"])
@login_required
def change_password():
    if current_user.is_authenticated:
        id = current_user.id
        user = User.query.filter_by(id=id).first()
        form = ResetPasswordForm()
        if request.method == 'POST' and form.validate_on_submit():
            user.set_password(form.password.data)
            db.session.commit()
            logout_user()
            flash('Your password has been changed.', 'success')
            return redirect(url_for('user.login'))
    return render_template('user/change_password.html', form=form)
