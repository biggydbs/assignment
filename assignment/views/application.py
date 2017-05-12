import random, string
from assignment import db
from boto.s3.key import Key
from werkzeug import secure_filename
from assignment.utils import get_s3_bucket, validate
from assignment.decorators import login_required
from flask import Blueprint, render_template, request, url_for, session, redirect

main_blueprint = Blueprint('application', __name__)

@main_blueprint.route("/dashboard")
@login_required
def dashboard():
	admins = db.admins
	managers = db.managers
	check_admin = admins.find_one({"email":session["email"]})
	check_manager = managers.find_one({"email":session["email"]})
	contact_no = None
	profile_pic = None
	bucket_url = None
	if check_admin != None:
		name = check_admin["first_name"] + " " + check_admin["last_name"]
		gender = check_admin["gender"]
		address = check_admin["address"]
	if check_manager != None:
		name = check_manager["first_name"] + " " + check_manager["last_name"]
		gender = check_manager["gender"]
		address = check_manager["address"]
		contact_no = check_manager["contact_no"]
		profile_pic = check_manager.get("profile_pic", None)
		bucket = get_s3_bucket()
		bucket_key = bucket.get_key(profile_pic)
		bucket_url = bucket_key.generate_url(3600, query_auth=True, force_http=True)
	return render_template("dashboard.html", name=name, email=session["email"],
		gender=gender, address=address, contact_no=contact_no, profile_pic=bucket_url)