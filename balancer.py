# -*- coding: utf-8 -*-

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, make_response,redirect
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
import boto3
import random
import requests
import threading
import base64

import sys

#---coisas para começar uma instancia nova caso uma morra---
initi_comand='''#!/bin/bash
cd home/ubuntu
git clone https://github.com/Formulos/Cloud_aps
cd Cloud_aps
./dependencias.sh
python3 aps1.py

'''
ec2_tag = [{'ResourceType':'instance','Tags':[{'Key':'Owner','Value':"Paulo"}]}]

IpPermissions=[
            {'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
            'FromPort': 5000,
            'ToPort': 5000,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}]
#----
app = Flask(__name__,)
api = Api(app)

global current_ip
current_ip = ""

#instancias init
credentials = boto3.Session().get_credentials()
ec2 = boto3.resource('ec2', region_name = "us-east-1")
client = boto3.client('ec2')
waiter_running = client.get_waiter('instance_running')
waiter_ok = client.get_waiter('instance_status_ok')

current_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

ec2info = []
avalible_inst=[] #ip da intancias disponiveis que não sejam o loadbalancer
#all_inst=[]#ip de todas as intancias

def update_inst_data():

    ec2info.clear()
    avalible_inst.clear()
    for instance in current_instances:
        x = instance.describe_attribute(Attribute='userData')
        print(base64.b64decode(x['UserData']['Value']))
        for tag in instance.tags:
            if ('Paulo' in tag['Value']): 
                #all_inst.append(instance.public_ip_address)
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

    
update_inst_data()
print(avalible_inst)
#print(all_inst)

@app.route('/', defaults={'path': ''},methods=['GET', 'POST','DELETE','UPDATE'])
@app.route('/<path:path>',methods=['GET', 'POST','DELETE','UPDATE'])
def catch_all(path):

    ip =  ip = random.choice(avalible_inst)
    url = "http://" + ip + ":5000/tasks"
    return redirect(url,code=307)

def check_status():
    #print("check_status")
    for site in avalible_inst:
        try:
            r = requests.get("http://" + site + ":5000" +"/healthcheck",timeout=5)
            if (r.status_code != 200):
                print("não voltou 200!")
                terminate_broken(site)  
        except :
            print("tempo expirado")
            terminate_broken(site)
    print("tudo bem por aqui(check status)")
    
    if len(avalible_inst) < max_ins_number: # para debug
        print("poucas instancias")
        replenish_inst()
    
    t = threading.Timer(10.0, check_status)
    print(avalible_inst)
    t.start()
            
            
def terminate_broken(broken_inst): # broken_inst deve ser o ip publico dela
    print(broken_inst)
    inst_data = next(item for item in ec2info if item["Public IP"] == broken_inst) # pega informação da instancia quebrada
    id_broken = [inst_data["ins_id"]]

    print("update list")
    #deleta list and dict
    #ec2info[:] = [d for d in ec2info if d.get("Public IP") != broken_inst]
    #avalible_inst.remove(broken_inst)

    
    
    #faz um update da lista e dic
    client.terminate_instances(InstanceIds=id_broken)
    update_inst_data()

    
    replenish_inst() 



def replenish_inst(grupo=['Paulo_Aps'],chave = "paulo_final"):
    print("criando instancias novas")
    data = ec2.create_instances(UserData = initi_comand,ImageId="ami-06cd4dcc1f9e068d9",TagSpecifications=ec2_tag,InstanceType = 't2.micro',MaxCount = 1,MinCount = 1,SecurityGroups=grupo,KeyName = chave )
    data = data[0]
    print("esperando")
    waiter_running.wait(InstanceIds=[data.id])
    waiter_ok.wait(InstanceIds=[data.id])
    update_inst_data()
    print("lista depois do replenish_inst ",avalible_inst)


if __name__ == '__main__':
    #voce pode passar uma quantidade de instancias como primeiro argumento de sys.argvs
    max_ins_number = 3
    if int(len(sys.argv)) > 1 :
        max_ins_number = sys.argv[1]
        max_ins_number = int(max_ins_number)
    threading.Timer(10.0, check_status).start()
    app.run(debug=False,host="0.0.0.0",port = 5000)