import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_service import access
from storage import util

server = Flask(__name__)
server.config['MONGO_URI'] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)
fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(
	pika.ConnectionParameters("rabbitmq")
)
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
	token, error = access.login(request)

	if not error:
		return token
	else:
		return error

@server.route("/upload", methods=["POST"])
def upload():
	access, err = validate.token(request)
	access = json.loads(access)

	if access["admin"]:
		if len(request.files) > 1 or len(request.files) < 1:
			return "Exactly one file must be uploaded", 400
		
		for _, file in request.files.items():
			err = util.upload(file, fs, channel, access)

			if err:
				return err
		
		return "File uploaded", 200
	else:
		return "Not authorized", 403

@server.route("/download", methods=["GET"])
def download():
	pass

if __name__ == "__main__":
	server.run(host="0.0.0.0", port=8080)