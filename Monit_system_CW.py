# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 22:31:14 2023

@author: rafin
"""

import json
import requests
import datetime
import smtplib
import pandas as pd
import pyodbc
import time as tm
import numpy as np


''' gerando dados fictícios para teste '''

data = {
    "operations": [
        {
            "dia":{"2023-01-01"},
            "time": {"00h 01"},
            "status": {"denied"},
            "count": {"110"}
        },
        {
            "dia":{"2023-01-01"},
            "time": {"00h 01"},
            "status": {"approved"},
            "count": {"100"}
        }
    ]
}
    
for operation in data['operations']:
    operation['time'] = list(operation['time'])
    operation['status'] = list(operation['status'])
    operation['count'] = list(operation['count'])
    operation['dia'] = list(operation['dia'])

data_api = json.dumps(data)




''' definindo a configuração da parte do envio do email'''

EMAIL_FROM = "email@email.com"
EMAIL_TO = "email@email.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "email@email.com"
SMTP_PASSWORD = "senha"

# função para coleta da base de dados em SQL
def get_database(cnxn_str):
    try:
        cnxn = pyodbc.connect(cnxn_str)

        query = "SELECT * FROM dbo.Transactions_CW"
        
        df = pd.read_sql(query,cnxn)
            
        cnxn.commit()
        
        
        ''' verificação dos percentis para denied, reversed
        e failed, gerando um dicionario '''
        
        dic_perc = {'denied':[],'reversed':[],'failed':[]}
        dic_abs = {'denied':[],'reversed':[],'failed':[]}
        
        for time in df.time.unique():
            df_time = df[df.time==time]
            
            for status in ['denied','reversed','failed']:
                
                if status in (df_time.status.tolist()):
                    
                    perc = (df_time[df_time.status == status]['count'].sum()
                            / df_time['count'].sum())
                                       
                    dic_perc[status].append(perc)
                    
                    
        for item in dic_perc:
            if item == 'denied':
                lista = []
                lista.append(np.percentile(dic_perc[item][:int(0.25*len(item))],95))
                lista.append(np.percentile(dic_perc[item][int(0.25*len(item)):],95))
                dic_perc[item] = lista
            else:
                dic_perc[item] = np.percentile(dic_perc[item],95)
            
            
        for status in ['denied','reversed','failed']:
            if status == 'denied':
                val1 = np.percentile(df[(df.status==status)&(df.minutos < 360)]['count'],95)
                val2 = np.percentile(df[(df.status==status)&(df.minutos >= 360)]['count'],95)
                dic_abs[status].append(val1)
                dic_abs[status].append(val2)
            else:
                val = np.percentile(df[df.status==status]['count'],95)
                dic_abs[status].append(val)
                    
        print('Base de dados coletada com sucesso.')
        
        return df, dic_perc, dic_abs
    except Exception as e:
        print('Erro ao coletar base de dados:',e)


# criando função para envio do email
def send_alert(time_str, status_str):
    message = "Alerta: Comportamento suspeito no seguinte horário: "+time_str+", quando operações "+status_str+" estavam acima do esperado. Favor investigar."
    try:
        # Create SMTP connection
        smtp_conn = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_conn.ehlo()
        smtp_conn.starttls()
        smtp_conn.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Send email
        smtp_conn.sendmail(EMAIL_FROM, EMAIL_TO, message)

        # Close SMTP connection
        smtp_conn.quit()

        print("Alert sent:", message)
    except Exception as e:
        print("Error sending alert:", e)




# criando função que analisa os dados e faz envio de email, se precisar
def analyze_data(base, dic_perc, dic_abs, data):

    # Parse the JSON data
    try:
        json_data = json.loads(data)
    except json.JSONDecodeError as e:
        print("Erro na análise dos dados JSON:", e)
        return
    
    lista_time = []
    lista_status = []
    lista_count = []
    lista_dia = []
    lista_minutos = []
    lista_id = []
    
    count_total = 0
    for operation in json_data['operations']:
        count_total += int(operation['count'][0])
    
    # Loop para pegar os dados de cada operação
    for operation in json_data['operations']:
        time_str = operation['time'][0]
        status_str = operation['status'][0]
        count = int(operation['count'][0])
        dia = datetime.datetime.strptime(operation['dia'][0],"%Y-%m-%d").date()
        
        
        id_op = str(dia)+str(time_str)+str(count)+str(status_str)
        # Verificando se é operação nova
        if id_op not in (base['id_op'].tolist()):

            lista_time.append(time_str)
            lista_status.append(status_str)
            lista_count.append(count)
            lista_dia.append(dia)
            
            
            lista_id.append(id_op)
    
            # Transformação do horário para minutos
            minutos = (int(time_str.split('h ')[0])*60+
                       int(time_str.split('h ')[1]))
            lista_minutos.append(minutos)
    
            
                
            # Verificando anomalias baseadas em regras
            if status_str == 'denied':
                if minutos < 360:
                    if abs(count) > dic_abs['denied'][0]:
                        send_alert(time_str, status_str)
                    elif count / count_total > dic_perc['denied'][1]:
                        send_alert(time_str, status_str)
                else:
                    if abs(count) > dic_abs['denied'][1]:
                        send_alert(time_str, status_str)
                    elif count / count_total > dic_perc['denied'][0]:
                        send_alert(time_str, status_str)
            elif status_str == 'reversed':
                if abs(count) > dic_abs['reversed'][0]:
                    send_alert(time_str, status_str)
                elif count / count_total > dic_perc['reversed']:
                    send_alert(time_str, status_str)
            elif status_str == 'failed':
                if abs(count) > dic_abs['failed'][0]:
                    send_alert(time_str, status_str)
                elif count / count_total > dic_perc['failed']:
                    send_alert(time_str, status_str)
    
    df = pd.DataFrame({'dia':lista_dia,
                       'time':lista_time,
                       'status':lista_status,
                       'count':lista_count,
                       'minutos':lista_minutos,
                       'id_op':lista_id})
    
    return df


#criando função final para chamar API, analisar e update via query SQL
def query_data(api,cnxn_str):

    response = requests.get(api)
    if response.status_code == 200:
        
        base, dic_perc, dic_abs = get_database(cnxn_str)
        
        df_hora = analyze_data(base, dic_perc, dic_abs, response.text)
        
        try:
            cnxn = pyodbc.connect(cnxn_str)
            
            cursor = cnxn.cursor()
            
            for index, row in df_hora.iterrows():
                cursor.execute("INSERT INTO dbo.Transactions_CW (dia,time,status,count,minutos,id_op) values("
                           +"'"+str(df_hora.dia[index])
                           +"',"
                           +"'"+str(df_hora.time[index])
                           +"',"
                           +"'"+str(df_hora.status[index])
                           +"',"
                           +str(df_hora['count'][index])
                           +","
                           +str(df_hora['minutos'][index])
                           +","
                           +"'"+str(df_hora['id_op'][index])+
                           "')"
                          )
            
            cnxn.commit()
            cursor.close()
            
            print('Dados enviados à base de dados')
        
        except Exception as e:
            
            print('Erro: ',e)
    
    else:
        print("Erro ao obter data da API")


## definindo as variáveis que serão utilizadas na parte final do código    

# API endpoint URL
API_ENDPOINT = "https://example.com/api"
# Dados do servidor SQL Server
cnxn_str = ("Driver={SQL Server Native Client 11.0};"
            "Server=LAPTOP-RE2P03AH;"
            "Database=Teste;"
            "Trusted_Connection=yes;")    
 

''' rodando o código que recebe o valor da API, faz a análise, envia email se
for necessário, e envia os dados para a base no servidor (SQL)'''

while True:
    query_data(API_ENDPOINT,cnxn_str)
    
    tm.sleep(10)


