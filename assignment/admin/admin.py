import random, string
from assignment import db
from boto.s3.key import Key
from werkzeug import secure_filename
from assignment.decorators import login_required
from assignment.utils import get_s3_bucket, validate
from flask import Blueprint, render_template, request, url_for, session, redirect

admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route("/add_admin", methods=["GET","POST"])
@login_required
def add_admin():
	if session["user"] != "admin":
		return render_template("home.html", error="You are not admin")
	admins = db.admins
	managers = db.managers
	error = None
	if request.method == "POST":
		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		gender = request.form["gender"]
		address = request.form["address"]
		error = "Not a valid email id"
		if validate(email):
			check_admin = admins.find_one({"email":email})
			error = "Email already registered as admin"
			if check_admin == None:
				error = "Email already registered as manager"
				check_manager = managers.find_one({"email":email})
				if check_manager == None:
					code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
					admins.insert_one({
						"email":email,
						"first_name":first_name,
						"last_name":last_name,
						"gender":gender,
						"address":address,
						"code":code
						})
					return render_template("add_admin.html", error="Admin Added")
	return render_template("add_admin.html", error=error)

@admin_blueprint.route("/add_manager", methods=["GET","POST"])
@login_required
def add_manager():
	if session["user"] != "admin":
		return render_template("home.html", error="You are not admin")
	admins = db.admins
	managers = db.managers
	error = None
	if request.method == "POST":
		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		gender = request.form["gender"]
		address = request.form["address"]
		contact_no = request.form["contact_no"]
		profile_pic = request.files["profile_picture"]
		error = "Not a valid email id"
		if validate(email):
			code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
			check_manager = managers.find_one({"email":email})
			error = "Email already registered as manager"
			if check_manager == None:
				check_admin = admins.find_one({"email":email})
				error = "Email already registered as admin"
				if check_admin == None:	
					error = "Choose a profile Picture"
					if profile_pic:
						file_contents = profile_pic.read()
						file_name = secure_filename(profile_pic.filename)
						filetype = file_name.split(".")[1]
						error = "File type not accepted"
						if filetype == "jpg" or filetype == "png" or filetype == "jpeg":
							actual_filename = code + "." + filetype
							bucket = get_s3_bucket()
							k = Key(bucket)
							k.key = actual_filename
							k.set_contents_from_string(file_contents)
							managers.insert_one({
								"email":email,
								"first_name":first_name,
								"last_name":last_name,
								"gender":gender,
								"address":address,
								"contact_no":contact_no, 
								"code":code,
								"profile_pic" : actual_filename
								})
							return render_template("add_manager.html", error="Manager Added")
	return render_template("add_manager.html", error=error)