import re
import boto
from flask import session
from flask_mail import Message
from assignment import app, db, mail
from boto.s3.connection import OrdinaryCallingFormat

def send_email(to, subject, template):
	msg = Message(
		subject,
		recipients = to,
		html = template,
		sender = app.config["MAIL_DEFAULT_SENDER"]
		)
	mail.send(msg)

def get_s3_bucket():
	s3 = boto.s3.connect_to_region(region_name=app.config["REGION_HOST"], 
		aws_access_key_id=app.config["aws_access_key_id"], aws_secret_access_key=app.config["aws_secret_access_key"], 
		calling_format = boto.s3.connection.OrdinaryCallingFormat())
	bucket_name = app.config["bucket_name"]
	bucket = s3.get_bucket(bucket_name)	
	return bucket

def validate(email): 
	match = re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]*\.*[com|org|edu]{3}$)", email)
	return match