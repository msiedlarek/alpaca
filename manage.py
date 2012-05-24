#!/usr/bin/env python

import sys
from flaskext.script import Manager, prompt_pass
from alpaca import create_application

application = create_application()
manager = Manager(application)

@manager.command
@manager.option('username')
def createuser(username):
    import re
    if not re.match(r'^[\w\.\@]+$', username):
        print ("Username can only contain: letters (A-B, a-b), numbers (0-9),"
               " underscore (_), dot (.) and 'at' sign (@).")
        sys.exit(1)
    password = _get_new_password()
    from alpaca.tracker.models import User
    print "Creating new user..."
    user = User(username=username)
    user.set_password(password)
    user.save()
    print "done."

@manager.command
@manager.option('username')
def changepass(username):
    from alpaca.tracker.models import User
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print "No such user: %s" % username
        sys.exit(1)
    password = _get_new_password()
    print "Changing user's password..."
    user.set_password(password)
    user.save()
    print "done."

def _get_new_password():
    password = prompt_pass("New password")
    if password is None or len(password) < 5:
        print "Password must be at least 5 chars long."
        sys.exit(1)
    repeat_password = prompt_pass("Repeat password")
    if password != repeat_password:
        print "Passwords don't match."
        sys.exit(1)
    return password

if __name__ == '__main__':
    manager.run()
