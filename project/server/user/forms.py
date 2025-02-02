# project/server/user/forms.py


from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, EqualTo, Length

from project.server.models import Child, Chore, CompletedChore, User, WeeklyTotals


class LoginForm(FlaskForm):
    user_name = StringField("User Name", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])


class RegisterForm(FlaskForm):
    user_name = StringField(
        "User Name",
        validators=[
            DataRequired(),
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )


class AddChoreForm(FlaskForm):
    chore = StringField("Chore", validators=[DataRequired()])
    value = StringField("Value", validators=[DataRequired()])


class AddChildForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])


class CompleteChoreForm(FlaskForm):
    child = SelectField("Child")
    chore = SelectField("Chore")

    def __init__(self, *args, **kwargs):
        super(CompleteChoreForm, self).__init__(*args, **kwargs)
        self.child.choices = [(c.id, c.name) for c in Child.query.all()]
        self.chore.choices = [(c.id, c.chore) for c in Chore.query.all()]


class DeleteChoreForm(FlaskForm):
    chore_id = SelectField('Chore')

    def __init__(self, *args, **kwargs):
        super(DeleteChoreForm, self).__init__(*args, **kwargs)
        self.chore_id.choices = [(c.id, f"{c.child.name} - {c.chore.chore} - {c.completed_on}")
                                 for c in CompletedChore.query.order_by(CompletedChore.id.desc()).limit(10)]


class AddAdminForm(FlaskForm):
    user_name = SelectField("User Name")

    def __init__(self, *args, **kwargs):
        super(AddAdminForm, self).__init__(*args, **kwargs)
        self.user_name.choices = [(u.user_name) for u in User.query.all()]


class ApprovePaymentForm(FlaskForm):
    child = SelectField("Child")

    def __init__(self, *args, **kwargs):
        super(ApprovePaymentForm, self).__init__(*args, **kwargs)
        self.child.choices = [(c.id, f"{c.child.name}") for c in WeeklyTotals.query.all()]


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', [DataRequired()])
    password2 = PasswordField('Repeat New Password', [DataRequired(), EqualTo('password')])
