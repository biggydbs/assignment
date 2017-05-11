from functools import wraps
from flask import g , render_template , flash , redirect , request , url_for , session

#login-required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
        	check = session["email"]
        	return f(*args, **kwargs)
        except:
            flash("You need to Login first!")
            return redirect(url_for("application.index"))
    return wrap