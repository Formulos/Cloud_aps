

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, make_response,request
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
import random

app = Flask(__name__,)
api = Api(app)

global current_ip
current_ip = ""



class line(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(line, self).__init__()

    def get(self):
        liner = open("1liners.txt","r")
        data=liner.readlines()
        liner.close()
        
        return random.choice(data)[0:-2]



class Check(Resource):

    def __init__(self):
        super(Check, self).__init__()

    def get(self):
        return 200


api.add_resource(line, '/liners', endpoint='liners')
api.add_resource(Check, '/healthcheck', endpoint='healthcheck')


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port = 5000)