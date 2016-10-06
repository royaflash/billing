from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_required, LoginManager, login_user, logout_user, current_user
from dateutil.parser import parse
from collaboratory import Collaboratory
from user_management import UserDatabase
from auth import sessions
from config import default

app = Flask(__name__)
app.config.from_object(default)

app.secret_key = app.config['SECRET_KEY']

# TODO: Remove, this was for proof of concept
token = sessions.get_new_token(auth_url=app.config['AUTH_URI'], username='admin', password='admin')
database = Collaboratory(app.config['MYSQL_URI'])

users = UserDatabase()
users.init_db()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(user_id):
    if user_id == 7:
        return users.get_test_user(7)
    else:
        return users.get_user_by_id(user_id)


def get_relevant_projects():
    if current_user.username == 'admin':
        return database.get_projects()
    else:
        return current_user.projects


@app.route('/')
@login_required
def root():
    return render_template('template.html',
                           projects=get_relevant_projects())


@app.route('/login', methods=['GET', 'POST'])
def login():
    print 'attempting login'
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':

        if request.form.get('username') == 'admin':
            user = users.get_test_user(7)
        else:
            user = users.get_user_by_username(request.form.get('username'))

        if user is not None and user.authenticate(request.form.get('username'),
                                                  request.form.get('password')):
            login_user(user)
            flash('LOGIN SUCCESSFUL')
            print current_user.username
            print current_user.projects
            return redirect(url_for('root'))
        else:
            flash('LOGIN FAILED', 'error')
            return render_template('login.html',
                                   username=request.form.get('username'))


@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    flash('LOGGED OUT')
    return redirect('login')


@app.route('/by_user', methods=['GET'])
@login_required
def calculate_cost_by_user():
    start_date = parse(request.args.get('start_date'), ignoretz=True)
    end_date = parse(request.args.get('end_date'), ignoretz=True)
    project_id = request.args.get('project_id')
    user_id = request.args.get('user_id')

    instance_core_hours = database.get_instance_core_hours_by_user(start_date, end_date, project_id, user_id)

    volume_gigabyte_hours = database.get_volume_gigabyte_hours_by_user(start_date, end_date, project_id, user_id)

    project_users = database.get_users_by_project(project_id)

    return render_template('search_by_user.html',
                           start_date=start_date,
                           end_date=end_date,
                           instance_core_hours=instance_core_hours,
                           volume_gb_hours=volume_gigabyte_hours,
                           project_id=project_id,
                           users=project_users,
                           current_user_id=user_id,
                           projects=get_relevant_projects())


# Might wanna do javascript in order to allow for a dynamic path variable
# Need to add auth so that a user can't manually enter project details and access projects they shouldn't
@app.route('/by_project', methods=['GET'])
@login_required
def calculate_cost_by_project():
    start_date = parse(request.args.get('start_date'), ignoretz=True)
    end_date = parse(request.args.get('end_date'), ignoretz=True)
    project_id = request.args.get('project_id')

    instance_core_hours = database.get_instance_core_hours_by_project(start_date, end_date, project_id)

    volume_gigabyte_hours = database.get_volume_gigabyte_hours_by_project(start_date, end_date, project_id)

    image_gigabyte_hours = database.get_image_storage_gigabyte_hours_by_project(start_date, end_date, project_id)

    project_users = database.get_users_by_project(project_id)

    return render_template('search_by_project.html',
                           start_date=start_date,
                           end_date=end_date,
                           instance_core_hours=instance_core_hours,
                           volume_gb_hours=volume_gigabyte_hours,
                           image_gb_hours=image_gigabyte_hours,
                           project_id=project_id,
                           users=project_users,
                           projects=get_relevant_projects())
