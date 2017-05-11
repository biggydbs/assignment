from flask import Flask, render_template, url_for, session, request, flash, g, redirect
from pymongo import MongoClient
import os
from flask_mail import Mail

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
	error = "Template Not Found"
	return render_template('404.html',error=error), 404

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

app.config.from_object('config')

app.config.update(
	aws_access_key_id = "AKIAJ3OOAK6VSJ4QN6IA",
	aws_secret_access_key = "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",
	bucket_name = "hitesh-jain",
	REGION_HOST = "ap-south-1",
	s3_upload_directory = "/hitesh/"
)

mail = Mail(app)

client = MongoClient(app.config["MONGODB_SERVER"], app.config["MONGODB_PORT"])
db = client["assignment"]

from assignment.views.application import main_blueprint
app.register_blueprint(main_blueprint)