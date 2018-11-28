import boto3
import re
import requests
from requests_aws4auth import AWS4Auth
import sys


#region = 'us-east-1' # e.g. us-west-1\n
#service = 'ec2',

#credentials = boto3.Session().get_credentials()
#awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

client = boto3.client('ec2')
ec2 = boto3.resource('ec2')
waiter = client.get_waiter('instance_terminated')

content = open("public.pem")
pubkey = content.read()
content.close()

#response = client.create_key_pair(KeyName='test')
#print(response)
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


current_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

ec2info = []
for instance in current_instances:
    for tag in instance.tags:
        if ('Owner'in tag['Key']) and ('Paulo'in tag['Value']):
            name = tag['Value']
            # Add instance info to a dictionary         
            ec2info.append({
                'Name': name,
                'ins_id': instance.id,
                'Type': instance.instance_type,
                'State': instance.state['Name'],
                'Private IP': instance.private_ip_address,
                'Public IP': instance.public_ip_address,
                'Launch Time': instance.launch_time
                })


if len(ec2info) != 0:#checa se estava vazio
    instance_ids = []
    for runing in ec2info:
        instance_ids.append(runing["ins_id"])
        client.terminate_instances(InstanceIds=instance_ids)
        print("matei uma instancia, espera um minuto até ela morrer de vez")

    waiter.wait(InstanceIds=instance_ids)
    print("a instancia esta morta, vida longa a nova instancia!")


try:
    client.describe_key_pairs(KeyNames=['paulo_final',],)
    print("key ja existe deletando e criando uma nova")
    client.delete_key_pair(KeyName="paulo_final")
    key = client.import_key_pair(KeyName='paulo_final',PublicKeyMaterial=pubkey,DryRun=False)
except :
    key = client.import_key_pair(KeyName='paulo_final',PublicKeyMaterial=pubkey,DryRun=False)
    print("key criada")

try:
    client.describe_security_groups(GroupNames=['Paulo_Aps'])
    print("grupo reiniciado")
    client.delete_security_group(GroupName='Paulo_Aps')
    group = client.create_security_group(Description='Paulo_Aps',GroupName='Paulo_Aps')
    client.authorize_security_group_ingress(GroupName ="Paulo_Aps" ,IpPermissions = IpPermissions )
except :
    group = client.create_security_group(Description='Paulo_Aps',GroupName='Paulo_Aps')
    client.authorize_security_group_ingress(GroupName ="Paulo_Aps" ,IpPermissions = IpPermissions)
    print("grupo iniciado")


initi_comand='''#!/bin/bash
cd home/ubuntu
git clone https://github.com/Formulos/Cloud_aps
cd Cloud_aps
./dependencias.sh
python aps1.py

'''

ec2.create_instances(UserData = initi_comand,ImageId="ami-06cd4dcc1f9e068d9",TagSpecifications=ec2_tag,InstanceType = 't2.micro',MaxCount = 3,MinCount = 3,SecurityGroups=['Paulo_Aps'],KeyName = "paulo_final" )
