

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, make_response,redirect
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
import boto3
import random
import requests

app = Flask(__name__,)
api = Api(app)

global current_ip
current_ip = ""

tasks = [
    {
        'id': 1,
        'title': random.randint(1,101),
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': random.randint(1,101),
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

#instancias init
credentials = boto3.Session().get_credentials()
ec2 = boto3.resource('ec2', region_name = "us-east-1")

current_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

ec2info = []
avalible_inst=[]
for instance in current_instances:
    for tag in instance.tags:
        if ('Owner'in tag['Key']) and ('Paulo'in tag['Value']):
            name = tag['Value']
            # Add instance info to a dictionary
            avalible_inst.append(instance.public_ip_address)         
            ec2info.append({
                'Name': name,
                'ins_id': instance.id,
                'Type': instance.instance_type,
                'State': instance.state['Name'],
                'Private IP': instance.private_ip_address,
                'Public IP': instance.public_ip_address,
                'Launch Time': instance.launch_time
                })

class balancer_list(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(balancer_list, self).__init__()

    def get(self):
        ip = random.choice(avalible_inst)
        url = "http://" + ip + ":5000/tasks"
        return redirect(url,code=301)

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'id': tasks[-1]['id'] + 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        tasks.append(task)
        return {'task': marshal(task, task_fields)}, 201

class balancer(Resource):

    def __init__(self):
        super(balancer, self).__init__()

    def get(self):
        ip = random.choice(avalible_inst)
        url = "http://"+ip+":5000"

        return requests.get(url)




#api.add_resource(balancer_list, '/load', endpoint='load')
#api.add_resource(TaskAPI, '/tasks/<int:id>', endpoint='task')
#api.add_resource(Check, '/healthcheck', endpoint='healthcheck')
api.add_resource(balancer_list, '/load', endpoint='load')


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port = 5000)