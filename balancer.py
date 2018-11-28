

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
avalible_inst=[] #intancias disponiveis que não sejam o loadbalancer
all_inst=[]#todas as intancias
for instance in current_instances:
    for tag in instance.tags:
        if ('Paulo' in tag['Value']): 
            all_inst.append(instance.public_ip_address)
            if('Paulo_b' not in tag['Value']):
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

print(avalible_inst)
print(all_inst)

@app.route('/', defaults={'path': ''},methods=['GET', 'POST'])
@app.route('/<path:path>',methods=['GET', 'POST'])
def catch_all(path):
    ip = random.choice(avalible_inst)
    url = "http://" + ip + ":5000/tasks"
    return redirect(url,code=307)

def check_status():
    pass


#timer
#timer = threading.Timer(2.0, gfg)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port = 5000)