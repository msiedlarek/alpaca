import hashlib
import iso8601
import flask
import mongoengine as db
from flask import request, url_for
import flaskext.login
from flaskext.login import login_required
from alpaca.tracker import blueprint, forms
from alpaca.tracker.models import User, Error, ErrorOccurrence

@blueprint.route('/')
@login_required
def dashboard():
    errors = Error.objects.order_by('-last_occurrence')[:100]
    return flask.render_template('dashboard.html',
        errors=errors,
    )

@blueprint.route('/reporter/<reporter>')
@login_required
def reporter(reporter):
    errors = Error.objects(reporters=reporter) \
                  .order_by('-last_occurrence')[:100]
    return flask.render_template('reporter.html',
        reporter=reporter,
        errors=errors,
    )

@blueprint.route('/login', methods=('GET', 'POST',))
def login():
    form = forms.LoginForm(request.form)
    if form.validate_on_submit():
        try:
            user = User.objects.get(username=form.username.data)
        except User.DoesNotExist:
            pass
        else:
            if user.password_matches(form.password.data):
                flaskext.login.login_user(user)
                return flask.redirect(request.args.get('next') or
                                      url_for('tracker.dashboard'))
        flask.flash("Sorry, invalid credentials.", 'error')
    return flask.render_template('login.html',
        login_form=form,
    )

@blueprint.route('/logout', methods=('POST',))
@login_required
def logout():
    form = forms.LogoutForm(request.form)
    if form.validate_on_submit():
        flaskext.login.logout_user()
    return flask.redirect(url_for('tracker.login'))

@blueprint.route('/change-password', methods=('GET', 'POST',))
@login_required
def change_password():
    form = forms.ChangePasswordForm(request.form)
    if form.validate_on_submit():
        if form.password.data == form.repeat_password.data:
            user = flaskext.login.current_user
            user.set_password(form.password.data)
            user.save()
            flask.flash("Your password has been successfuly changed.",
                        'success')
            flask.redirect(url_for('tracker.change_password'))
        else:
            form.repeat_password.errors.append(
                "Password repeated incorrectly."
            )
    return flask.render_template('change_password.html',
        change_password_form=form,
    )

@blueprint.route('/report/<api_key>', methods=('POST',))
def report(api_key):
    try:
        reporter = flask.current_app.config['CLIENTS'][api_key]
    except KeyError:
        flask.abort(401)
    if not request.json:
        flask.abort(400)
    try:
        checksum = hashlib.md5(request.json['traceback']).hexdigest()
        occurrence = ErrorOccurrence(
            date=iso8601.parse_date(request.json['date']),
            reporter=reporter,
            uri=request.json['uri'],
            get_data=request.json['get_data'],
            post_data=request.json['post_data'],
            cookies=request.json['cookies'],
            headers=request.json['headers']
        )
    except (KeyError, iso8601.ParseError):
        flask.abort(400)
    try:
        Error.objects.get(checksum=checksum)
    except Error.DoesNotExist:
        try:
            Error.objects.create(
                checksum=checksum,
                summary=request.json['traceback'].split('\n')[-1],
                traceback=request.json['traceback']
            )
        except db.OperationError:
            pass
    Error.objects(checksum=checksum).exec_js(
        """
            function()
            {
                db[collection].find(query).forEach(function(error){
                    while (error[~occurrences].length > 29) {
                        error[~occurrences].shift();
                    }
                    error[~occurrences].push(options.occurrence);
                    error[~occurrence_counter]++;
                    error[~last_occurrence] = options.occurrence.date;
                    if
                    (error[~reporters].indexOf(options.occurrence[~occurrences.reporter]) === -1) {
                        error[~reporters].push(options.occurrence[~occurrences.reporter]);
                    }
                    db[collection].save(error);
                });
            }
        """,
        occurrence=occurrence.to_mongo(),
        occurrence_history_limit=flask.current_app.config['ERROR_OCCURRENCE_HISTORY_LIMIT']
    )
    return ''

@blueprint.route('/error/<error_id>')
@login_required
def investigate(error_id):
    try:
        error = Error.objects.get(id=error_id)
    except Error.DoesNotExist:
        flask.abort(404)
    return flask.render_template('investigate.html',
        error=error,
    )
