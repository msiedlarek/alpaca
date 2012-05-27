import hashlib
import hmac
import iso8601
import flask
import mongoengine as db
from flask import request, url_for
from werkzeug.exceptions import BadRequest
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

@blueprint.route('/api/report', methods=('POST',))
def report():
    """
    The report API service allowing reporters to report error occurrences.
    Incoming report takes form of HTTP POST request with additional, custom
    headers:

        X-Alpaca-Reporter  -- reporter identifier, as in REPORTERS configuration
                              dict key;
        X-Alpaca-Signature -- HMAC-SHA256 signature of the request built from
                              reporter's API key (as in REPORTERS configuration
                              dict value) and request body.

    The body of the request should be a JSON-encoded object containing all of
    following fields:

        error_hash -- client-customized hash, by which error occurrences are
                      grouped in single error object, no more than 100
                      characters long;
        date       -- ISO8601-encoded date and time when given error occurred;
        uri        -- URI requested when error occurrend, can be left blank
                      if exception occurred outside of request logic (eg.
                      in a CRON job);
        get_data   -- JSON object of HTTP GET data, blank if error occurred
                      outside of request logic;
        post_data  -- JSON object of HTTP POST data, blank if error occurred
                      outside of request logic;
        cookies    -- JSON object of HTTP cookies, blank if error occurred
                      outside of request logic;
        cookies    -- JSON object of HTTP/FastCGI/WSGI meta headers, blank if
                      error occurred outside of request logic.

    This API method returns one of the following HTTP codes:

        200 OK                    -- incoming message was processed and saved
                                     successfully
        400 BAD REQUEST           -- missing headers or required data
        401 UNAUTHORIZED          -- nonexistent reporter declared or invalid
                                     signature
        500 INTERNAL SERVER ERROR -- unexpected condition occurred
    """
    try:
        # Get the identifier of the reporter the error is coming from.
        reporter = request.headers['X_ALPACA_REPORTER']
        # Get the message HMAC signature.
        signature = request.headers['X_ALPACA_SIGNATURE']
    except KeyError:
        # Required, Alpaca-specific HTTP headers were not found.
        return '', 400
    try:
        reporter_api_key = flask.current_app.config['REPORTERS'][reporter]
    except KeyError:
        # Reporter identifier was not found in configuration.
        return '', 401
    # Report signature is built using HMAC-SHA256 algorithm from reporter's
    # exclusive API key and the raw, incoming request data.
    correct_signature = hmac.new(
        reporter_api_key,
        request.data,
        hashlib.sha256
    ).hexdigest()
    if signature != correct_signature:
        # Signature declared in HTTP header is invalid.
        return '', 401
    try:
        # Extract unique for each error hash from incoming data.
        error_hash = request.json['error_hash']
        # Create occurrence embedded MongoDB document.
        occurrence = ErrorOccurrence(
            date=iso8601.parse_date(request.json['date']),
            reporter=reporter,
            uri=request.json['uri'],
            get_data=sorted(request.json['get_data'].items()),
            post_data=sorted(request.json['post_data'].items()),
            cookies=sorted(request.json['cookies'].items()),
            headers=sorted(request.json['headers'].items())
        )
    except (KeyError, BadRequest, iso8601.ParseError):
        # One of the following conditions occurred:
        #     KeyError   -- the message is missing required JSON key
        #     BadRequest -- the message is not a valid JSON
        #     ParseError -- the date is not in correct ISO 8601 format
        return '', 400
    try:
        # Check if error of given hash already exists.
        Error.objects.get(hash=error_hash)
    except Error.DoesNotExist:
        try:
            # So it doesn't. Try to create one.
            Error.objects.create(
                hash=error_hash,
                summary=request.json['traceback'].split('\n')[-1],
                traceback=request.json['traceback']
            )
        except db.OperationError:
            # This error *PROBABLY* means other concurrent request created the
            # error object in a tight spot beetween our checking and creating.
            # Let's assume that's what happened and go on - we wanted to
            # have our error and now we have it after all.
            pass
    # Atomic operation of inserting the new occurence to the error object,
    # trimming the occurences array to the limit specified in configuration
    # and setting several caching values, like `last_occurrence` or
    # `occurrence_counter` on error object.
    Error.objects(hash=error_hash).exec_js(
        '''
        function(){
            db[collection].find(query).forEach(function(error){
                while (error[~occurrences].length
                        > options.occurrence_history_limit - 1) {
                    error[~occurrences].shift();
                }
                error[~occurrences].push(options.occurrence);
                error[~occurrence_counter]++;
                error[~last_occurrence] = options.occurrence[~occurrences.date];
                if (error[~reporters].indexOf(
                        options.occurrence[~occurrences.reporter]) === -1) {
                    error[~reporters].push(
                        options.occurrence[~occurrences.reporter]
                    );
                }
                db[collection].save(error);
            });
        }
        ''',
        # Occurrence embedded document converted to MongoDB format.
        occurrence=occurrence.to_mongo(),
        # Limit of occurrence history stored for each error.
        occurrence_history_limit=flask.current_app \
                                      .config['ERROR_OCCURRENCE_HISTORY_LIMIT']
    )
    # Return empty HTTP 200 OK response.
    return ''
