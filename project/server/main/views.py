# project/server/main/views.py


from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from project.server import db
from project.server.models import Child, Chore, CompletedChore, WeeklyTotals
from project.server.user.forms import CompleteChoreForm

main_blueprint = Blueprint("main", __name__)


def get_start_of_week():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    return start_of_week


def get_child_weekly_total(child_id, start_of_week, end_of_week):
    weekly_total = db.session.query(WeeklyTotals.total).filter(
        WeeklyTotals.child_id == child_id,
        WeeklyTotals.week_start >= start_of_week.date(),
        WeeklyTotals.week_start <= end_of_week.date()
    ).scalar()
    return weekly_total if weekly_total else 0


@main_blueprint.route("/", methods=["GET", "POST"])
@login_required
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('user.login'))

    form = CompleteChoreForm(request.form)
    start_of_week = get_start_of_week()

    if request.method == 'POST' and form.validate():
        child_id = form.child.data
        chore_id = form.chore.data
        user_id = current_user.id  # Get the current user ID
        new_chore = CompletedChore(chore_id=chore_id, child_id=child_id, user_id=user_id)

        chore_value = db.session.query(Chore.value).filter(Chore.id == chore_id).scalar()

        if chore_value is None:
            flash('Chore value not found.', 'danger')
            return redirect(url_for('main.home'))

        weekly_total = db.session.query(WeeklyTotals).filter(
            WeeklyTotals.child_id == child_id,
            WeeklyTotals.week_start == start_of_week.date()
            ).first()

        if weekly_total is None:
            # Create a new WeeklyTotals instance if it doesn't exist
            weekly_total = WeeklyTotals(child_id=child_id, week_start=start_of_week.date(), total=chore_value)
        else:
            # Update the total value
            weekly_total.total += chore_value

        db.session.add(new_chore)
        db.session.add(weekly_total)
        db.session.commit()

        flash('Chore assigned.')

        return redirect(url_for('main.home'))

    latest_chore = CompletedChore.query.order_by(CompletedChore.id.desc()).first()

    return render_template("main/home.html", form=form, latest_chore=latest_chore)


@main_blueprint.route("/summary/")
@login_required
def summary():
    this_week = get_start_of_week()
    start_of_week_str = request.args.get('start_of_week', None)

    if start_of_week_str:
        start_of_week = datetime.strptime(start_of_week_str, "%Y-%m-%d")
    else:
        # Default to the current week's Monday if no input
        start_of_week = get_start_of_week()

    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    weekly_chores = CompletedChore.query.filter(
        CompletedChore.completed_on >= start_of_week,
        CompletedChore.completed_on <= end_of_week,
        ).order_by(CompletedChore.completed_on.desc()).all()

    running_total = {}
    for chore in weekly_chores:
        if chore.child_id not in running_total:
            child = Child.query.get(chore.child_id)
            running_total[chore.child_id] = child.name, get_child_weekly_total(chore.child_id,
                                                                               start_of_week,
                                                                               end_of_week)

    return render_template("main/summary.html", weekly_chores=weekly_chores,
                           start_of_week=start_of_week,
                           running_total=running_total,
                           this_week=this_week,)
