import datetime
from ipaddress import ip_address
# from urllib import response
import csv
import requests
import json

# from rm import data


def get_carel_one_value(ip_addr, reg_name):
    resp=requests.get(f'http://{ip_addr}/xxxx/getvar.csv?name={reg_name}')
    print (ip_addr, reg_name, resp)

    csv_data = csv.DictReader(resp.text.splitlines(), delimiter=',')
    data = [row for row in csv_data]
    print (data[0].get('name') == reg_name)
    for row in data:
            if row.get('name') == reg_name:
                print(row.get('val'))  # Возвращаем значение val для найденного name
                return row.get('val')
    return None  # Если name не найден, возвращаем None

def get_carel_all_values(ip_addr):
    resp=requests.get(f'http://{ip_addr}/xxxx/getvar.csv?')
    print (ip_addr, resp)

    csv_data = csv.DictReader(resp.text.splitlines(), delimiter=',')
    data = [row for row in csv_data]
    print (data[0].get('name') == reg_name)
    for row in data:
            print(row.get('name'), row.get('val'))  # Возвращаем значение val для найденного name
    return None  # Если name не найден, возвращаем None

def get_carel_all_values_json(ip_addr):
    resp=requests.get(f'http://{ip_addr}/xxxx/getvarjson.cgi?full=1')
    print (ip_addr, resp)
    data_json = resp.text
    data=json.loads(data_json)
    return data  # Возвращаем словарь с именами и значениями


def get_carel_selected_values(ip_addr, reg_names):
    try:
        ip_address(ip_addr)  # Validate IP address
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip_addr}")
    try:
        if not isinstance(reg_names, list):
            raise ValueError("Register names must be provided as a list.")

        if not reg_names:
            raise ValueError("Register names list cannot be empty.")
    except TypeError:
        raise ValueError("Register names must be provided as a list.")
    reg_str = ''
    i=0
    for reg_name in reg_names:
        if not isinstance(reg_name, str):
            raise ValueError(f"Invalid register name: {reg_name}. Must be a string.")
        if not reg_name:
            raise ValueError("Register name cannot be empty.")
        if i==0:
            reg_str+=str(reg_name)
        else:
            reg_str+='&name='+str(reg_name)
        i+=1
    # print (reg_str)
    resp=requests.get(f'http://{ip_addr}/xxxx/getvar.csv?name={reg_str}')
    # print (ip_addr, reg_names, resp.text)

    csv_data = csv.DictReader(resp.text.splitlines(), delimiter=',')
    data = [row for row in csv_data]
    val_dict = {}
    for row in data:
        val_dict[row.get('name')] = float(row.get('val'))
    return val_dict  # Возвращаем значение val для найденного name
    


def set_carel_value(ip_addr, reg_name, value):
    payload={'name':reg_name, 'value':value}
    print (payload)
    resp=requests.get(url=f'http://{ip_addr}/xxxx/setvar.csv?{reg_name}={value}')
    if resp.status_code == 200:
        if reg_name in resp.text:
            print(f'Successfully set {reg_name} to {value} on {ip_addr}')
            return True
    else:
        return False