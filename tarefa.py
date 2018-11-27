#!/usr/bin/env python3.
import sys
import requests
import json


endpoint = "http://127.0.0.1:5000/tasks"
def main():

    if sys.argv[1] == 'adicionar':
        titulo = input("titulo:")
        description = input("descrição:")
        payload = {'title': titulo , 'description':description}
        r = requests.post(endpoint, json=payload)
        print(r.text)
        print('adicionar concluido')
        

    if sys.argv[1] == 'listar':
        print('pro')
        r = requests.get(endpoint)
        print(r.text)
        #get all tarefa

    if sys.argv[1] == 'buscar':
        r = requests.get(endpoint + "/" + sys.argv[2])
        print('pro')
        #get one id

    if sys.argv[1] == 'apagar':
        print('pro')
        r = requests.delete(endpoint + "/" + sys.argv[2])
        #put delete

    if sys.argv[1] == 'atualizar':
        titulo = input("titulo:")
        description = input("descrição:")
        payload = {'title': titulo , 'description':description}
        r = requests.put(endpoint + "/" + sys.argv[2], json=payload)
        print(r.text)
        #post tarefe


if __name__ == "__main__":
    main()

