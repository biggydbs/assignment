from flask import Flask, Blueprint, render_template, request, json, Markup, url_for, session, redirect, flash
from werkzeug import generate_password_hash, check_password_hash
from functools import wraps
from assignment.decorators import login_required
from assignment import app, db, ROOT_DIR
from assignment.utils import send_email
import random, string
from werkzeug import secure_filename
import os
from random import randint
from shutil import rmtree
import boto
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.key import Key

main_blueprint = Blueprint('application', __name__)

def get_s3_bucket():
	REGION_HOST = app.config["REGION_HOST"]
	s3_upload_directory = app.config["s3_upload_directory"]
	aws_access_key_id = app.config["aws_access_key_id"]
	aws_secret_access_key = app.config["aws_secret_access_key"]
	s3 = boto.s3.connect_to_region(region_name=REGION_HOST, aws_access_key_id=aws_access_key_id, 
		aws_secret_access_key=aws_secret_access_key, calling_format = boto.s3.connection.OrdinaryCallingFormat())
	bucket_name = app.config["bucket_name"]
	bucket = s3.get_bucket(bucket_name)
	return bucket

@main_blueprint.route("/login_admin", methods=["GET","POST"])
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
			return redirect(url_for("application.home"))
		
	return render_template("login_admin.html")


@main_blueprint.route("/login_manager", methods=["GET","POST"])
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
			return redirect(url_for("application.home"))

	return render_template("login_manager.html")

@main_blueprint.route("/")
def index():
	try:
		x = session["email"]
		return redirect(url_for("application.home"))
	except:
		return render_template("index.html")

@main_blueprint.route("/home")
def home():

	return render_template("home.html", error=None)

@main_blueprint.route("/logout")
def logout():
	session.pop("email",None)
	session.pop("user",None)
	return redirect(url_for("application.index"))

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
				if "@" in email:
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
				if "@" in email:
					if profile_pic:
						file_contents = profile_pic.read()
						file_name = secure_filename(profile_pic.filename)
						filetype = file_name.split(".")[1]
						if filetype == "jpg" or filetype == "png" or filetype == "jpeg":
							actual_filename = code + "." + filetype
							#profile_pic.save(os.path.join(app.config["PROFILE_IMAGE"],file_name))
							#os.rename(os.path.join(app.config["PROFILE_IMAGE"],file_name),os.path.join(app.config["PROFILE_IMAGE"],actual_filename))
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
	return render_template("home.html")

@main_blueprint.route("/edit_products")
@login_required
def edit_products():
	if session["user"] != "manager":
		return render_template("home.html", error="You are not manager")
	products = db.products
	all_products = products.find({})
	products_list = []
	for each in all_products:
		products_list.append(each)
	return render_template("edit_products.html", products_list=products_list, error=None)

@main_blueprint.route("/add_product", methods=["GET","POST"])
@login_required
def add_product():
	if session["user"] != "manager":
		return render_template("home.html", error="You are not manager")
	if request.method == "POST":
		products = db.products
		managers = db.managers
		get_all_managers = managers.find({},{"_id":0,"email":1})
		to = []
		for i in get_all_managers:
			if i["email"] != session["email"]:
				to.append(str(i["email"]))
		code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
		title = request.form["title"]
		description = request.form["description"]
		price = request.form["price"]
		quantity = request.form["quantity"]
		product_image = request.files.getlist("product_image[]")
		product_images = []
		ct = 1
		#directory = app.config["PRODUCT_IMAGES"] + code + "/"
		#if not os.path.exists(directory):
			#os.makedirs(directory)
		bucket = get_s3_bucket()
		
		for i in product_image:
			file_contents = i.read()
			file_name = secure_filename(i.filename)
			filetype = file_name.split(".")[1]
			if filetype == "jpg" or filetype == "png" or filetype == "jpeg":
				actual_filename = code + "_" + str(ct) + "." + filetype
				#i.save(os.path.join(directory,file_name))
				#os.rename(os.path.join(directory,file_name),os.path.join(directory,actual_filename))
				k = Key(bucket)
				k.key = actual_filename
				k.set_contents_from_string(file_contents)
				ct += 1	
				product_images.append(actual_filename)	
		products.insert_one({
			"code" : code,
			"title":title,
			"description":description,
			"price":price,
			"quantity":quantity,
			"product_images":product_images,
			})
		html = render_template("notification.html", email=session["email"])
		subject = "New Product Added"
		#send_email(to, subject, html)

		return render_template("add_product.html", error="Product Added")

	return render_template("add_product.html", error=None)

@main_blueprint.route("/update_product/<product_id>/", methods=["GET","POST"])
@login_required
def update_product(product_id):
	products = db.products
	if session["user"] != "manager":
		return render_template("home.html", error="You are not manager")
	if request.method == "POST":
		product_info = products.find_one({"code":product_id})
		cur_images_count = len(product_info["product_images"]) + 1
		title = request.form["title"]
		description = request.form["description"]
		price = request.form["price"]
		quantity = request.form["quantity"]
		product_image = request.files.getlist("product_image[]")
		product_images = []
		bucket = get_s3_bucket()
		#directory = app.config["PRODUCT_IMAGES"] + product_id + "/"
		#if not os.path.exists(directory):
			#os.makedirs(directory)
		for i in product_image:
			if i.filename == "":
				break
			file_contents = i.read()
			file_name = secure_filename(i.filename)
			filetype = file_name.split(".")[1]
			if filetype == "jpg" or filetype == "png" or filetype == "jpeg":
				actual_filename = product_id + "_" + str(cur_images_count) + "." + filetype
				#i.save(os.path.join(directory,file_name))
				#os.rename(os.path.join(directory,file_name),os.path.join(directory,actual_filename))
				k = Key(bucket)
				k.key = actual_filename
				k.set_contents_from_string(file_contents)
				cur_images_count += 1	
				product_images.append(actual_filename)
		if product_info["product_images"] != []:
			all_images = product_info["product_images"] + product_images
		else:
			all_images = product_info["product_images"]
		products.update_one({"code":product_id},{"$set":{
			"code" : product_id,
			"title":title,
			"description":description,
			"price":price,
			"quantity":quantity,
			"product_images":all_images,
			}})
		return redirect(url_for("application.update_product", product_id=product_id))
		
	else:
		product_info = products.find_one({"code":product_id})
		if product_info == None:
			return render_template("update_product.html", error="Product Not Found")
		product_images = []
		count_images = 0
		bucket = get_s3_bucket()
		for each in product_info["product_images"]:
			count_images += 1
			plans_key = bucket.get_key(each)
			plans_url = plans_key.generate_url(3600, query_auth=True, force_http=True)
			product_images.append(plans_url)
		title=product_info["title"]
		description=product_info["description"]
		price=product_info["price"]
		quantity=product_info["quantity"]
		return render_template("update_product.html", product_images=product_images, count_images=count_images, 
			price=price, description=description, title=title, quantity=quantity ,product_id=product_id)

	return render_template("update_product.html")

@main_blueprint.route("/delete_product/<product_id>/", methods=["GET","POST"])
@login_required
def delete_product(product_id):
	if session["user"] != "manager":
		return render_template("home.html", error="You are not manager")
	products = db.products
	products.remove({"code":product_id})
	return redirect(url_for("application.edit_products"))

@main_blueprint.route("/show_products")
@login_required
def show_products():
	products = db.products
	all_products = products.find({})
	products_list = []
	for each in all_products:
		products_list.append(each)
	return render_template("show_products.html", error=None, products_list=products_list)