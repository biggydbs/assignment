import random, string
from assignment import db
from boto.s3.key import Key
from werkzeug import secure_filename
from assignment.utils import get_s3_bucket, validate
from assignment.decorators import login_required
from flask import Blueprint, render_template, request, url_for, session, redirect

main_blueprint = Blueprint('application', __name__)

@main_blueprint.route("/add_admin", methods=["GET","POST"])
@login_required
def add_admin():
	if session["user"] != "admin":
		return render_template("home.html", error="You are not admin")
	admins = db.admins
	managers = db.managers
	if request.method == "POST":
		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		gender = request.form["gender"]
		address = request.form["address"]
		check_admin = admins.find_one({"email":email})
		if check_admin == None:
			check_manager = managers.find_one({"email":email})
			if check_manager == None:
				code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
				if validate(email):
					admins.insert_one({
						"email":email,
						"first_name":first_name,
						"last_name":last_name,
						"gender":gender,
						"address":address,
						"code":code
						})
					return render_template("add_admin.html", error="Admin Added")
				else:
					return render_template("add_admin.html", error="Not a valid email id")
			else:
				return render_template("add_admin.html", error="Email already registered as manager")
		else:
			return render_template("add_admin.html", error="Email already registered as admin")
	return render_template("add_admin.html", error=None)

@main_blueprint.route("/add_manager", methods=["GET","POST"])
@login_required
def add_manager():
	if session["user"] != "admin":
		return render_template("home.html", error="You are not admin")
	admins = db.admins
	managers = db.managers
	if request.method == "POST":
		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		gender = request.form["gender"]
		address = request.form["address"]
		contact_no = request.form["contact_no"]
		profile_pic = request.files["profile_picture"]
		code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
		check_manager = managers.find_one({"email":email})
		if check_manager == None:
			check_admin = admins.find_one({"email":email})
			if check_admin == None:
				if validate(email):
					if profile_pic:
						file_contents = profile_pic.read()
						file_name = secure_filename(profile_pic.filename)
						filetype = file_name.split(".")[1]
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
						else:
							return render_template("add_manager.html", error="File type not accepted")
					else:
						return render_template("add_manager.html", error="Choose a profile Picture")
				else:
					return render_template("add_manager.html", error="Not a valid email id")
			else:
				return render_template("add_manager.html", error="Email already registered as admin")
		else:
			return render_template("add_manager.html", error="Email already registered as manager")
	return render_template("add_manager.html", error=None)

@main_blueprint.route("/dashboard")
@login_required
def dashboard():
	admins = db.admins
	managers = db.managers
	check_admin = admins.find_one({"email":session["email"]})
	check_manager = managers.find_one({"email":session["email"]})
	if check_admin != None:
		name = check_admin["first_name"] + " " + check_admin["last_name"]
		gender = check_admin["gender"]
		address = check_admin["address"]
		return render_template("dashboard.html", name=name, email=session["email"],
			gender=gender, address=address)
	if check_manager != None:
		name = check_manager["first_name"] + " " + check_manager["last_name"]
		gender = check_manager["gender"]
		address = check_manager["address"]
		contact_no = check_manager["contact_no"]
		profile_pic = check_manager.get("profile_pic", None)
		bucket = get_s3_bucket()
		plans_key = bucket.get_key(profile_pic)
		plans_url = plans_key.generate_url(3600, query_auth=True, force_http=True)
		return render_template("dashboard.html", name=name, email=session["email"],
			gender=gender, address=address, contact_no=contact_no, profile_pic=plans_url)