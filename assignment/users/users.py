from flask import Blueprint, render_template, request, url_for, session, redirect
from assignment.decorators import login_required
from assignment import db
from boto.s3.key import Key

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route("/")
def index():
	try:
		check_user = session["email"]
		return redirect(url_for("users.home"))
	except:
		return render_template("index.html")

@users_blueprint.route("/home")
@login_required
def home():
	return render_template("home.html", error=None)

@users_blueprint.route("/login_admin", methods=["GET","POST"])
def login_admin():
	admins = db.admins
	if request.method == "POST":
		email = request.form["email"]
		check_admin = admins.find_one({"email":email})
		if check_admin == None:
			return render_template("login_admin.html", error="Not an admin")
		else:
			session["email"] = email
			session["user"] = "admin"
			return redirect(url_for("users.home"))
		
	return render_template("login_admin.html")


@users_blueprint.route("/login_manager", methods=["GET","POST"])
def login_manager():
	managers = db.managers
	if request.method == "POST":
		email = request.form["email"]
		check_manager = managers.find_one({"email":email})
		if check_manager == None:
			return render_template("login_manager.html", error="Not a manager")
		else:
			session["email"] = email
			session["user"] = "manager"
			return redirect(url_for("users.home"))

	return render_template("login_manager.html")

@users_blueprint.route("/logout")
@login_required
def logout():
	session.pop("email",None)
	session.pop("user",None)
	return redirect(url_for("users.index"))