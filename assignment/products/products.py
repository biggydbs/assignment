import random, string
from assignment import db
from boto.s3.key import Key
from werkzeug import secure_filename
from assignment.decorators import login_required
from assignment.utils import send_email, get_s3_bucket
from flask import Blueprint, render_template, request, url_for, session, redirect

product_blueprint = Blueprint('product', __name__)

@product_blueprint.route("/edit_products")
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

@product_blueprint.route("/add_product", methods=["GET","POST"])
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
		bucket = get_s3_bucket()
		
		for i in product_image:
			file_contents = i.read()
			file_name = secure_filename(i.filename)
			filetype = file_name.split(".")[1]
			if filetype == "jpg" or filetype == "png" or filetype == "jpeg":
				actual_filename = code + "_" + str(ct) + "." + filetype
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
		send_email(to, subject, html)

		return render_template("add_product.html", error="Product Added")

	return render_template("add_product.html", error=None)

@product_blueprint.route("/update_product/<product_id>/", methods=["GET","POST"])
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
		for i in product_image:
			if i.filename == "":
				break
			file_contents = i.read()
			file_name = secure_filename(i.filename)
			filetype = file_name.split(".")[1]
			if filetype == "jpg" or filetype == "png" or filetype == "jpeg":
				actual_filename = product_id + "_" + str(cur_images_count) + "." + filetype
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
		return redirect(url_for("product.update_product", product_id=product_id))
		
	else:
		product_info = products.find_one({"code":product_id})
		if product_info == None:
			return render_template("update_product.html", error="Product Not Found")
		product_images = []
		count_images = 0
		bucket = get_s3_bucket()
		for each in product_info["product_images"]:
			count_images += 1
			bucket_key = bucket.get_key(each)
			bucket_url = bucket_key.generate_url(3600, query_auth=True, force_http=True)
			product_images.append(bucket_url)
		title=product_info["title"]
		description=product_info["description"]
		price=product_info["price"]
		quantity=product_info["quantity"]
		return render_template("update_product.html", product_images=product_images, count_images=count_images, 
			price=price, description=description, title=title, quantity=quantity ,product_id=product_id)

@product_blueprint.route("/delete_product/<product_id>/", methods=["GET","POST"])
@login_required
def delete_product(product_id):
	if session["user"] != "manager":
		return render_template("home.html", error="You are not manager")
	products = db.products
	products.remove({"code":product_id})
	return redirect(url_for("product.edit_products"))

@product_blueprint.route("/show_products")
@login_required
def show_products():
	products = db.products
	all_products = products.find({})
	products_list = []
	for each in all_products:
		products_list.append(each)
	return render_template("show_products.html", error=None, products_list=products_list)