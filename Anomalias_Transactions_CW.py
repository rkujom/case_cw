# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 14:26:27 2023

@author: rafin
"""

import pandas as pd
import matplotlib.pyplot as plt


## importando csv como df e depois unindo em um só

df1 = pd.read_csv('https://raw.githubusercontent.com/thais-menezes/'+
                  'monitoring/main/transactions_1.csv')
df1['dia'] = '2023-01-01'
df2 = pd.read_csv('https://raw.githubusercontent.com/thais-menezes/'+
                  'monitoring/main/transactions_2.csv')
df2['dia'] = '2023-01-02'

df1 = df1.rename(columns={'f0_':'count'})

df = pd.concat([df1,df2]).reset_index(drop=True)

last_col = df.iloc[:, -1]
df = df.iloc[:, :-1]
df.insert(0, 'dia', last_col)


## analisando os possiveis status e verificando se há algum erro

status = list(pd.unique(df.status))

## Verificando que não existem mais tempos que possíveis
if len(pd.unique(df.time)) > 24*60:
    print('Necessário verificar os horários')




'''gráfico para ter uma noção básica da distribuição no tempo,
antes convertendo a coluna de horário para variavel continua'''

df['minutos'] = ''
for index, row in df.iterrows():
    df.minutos[index] = (int(df.time[index].split('h ')[0])*60 + 
                      int(df.time[index].split('h ')[1]))
    
                    


''' fazer o grafico para cada status'''

axes = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]

img, ax = plt.subplots(2,3)

t = 0
for item in status[:6]:
    df_status = df[df.status == item]
    for dia in df_status.dia.unique():
        ax[axes[t][0],axes[t][1]].scatter(df_status[df_status.dia==dia].minutos,df_status[df_status.dia==dia]['count'],
                                          s = 0.5)
    ax[axes[t][0],axes[t][1]].set_xticks(ticks=[],labels=[])
    ax[axes[t][0],axes[t][1]].set_title(item+' ('+str(round(df_status[df_status.status==item]['count'].sum()/df['count'].sum(),1)*100)+'%)',
                                        fontsize=10)
    t += 1


''' Approved: dois picos no dia, com várias opearções aprovadas no último 
momento do dia;

Denied: Pico na metade do dia, com vários períodos de 0 operações e também
grande mov no último momento;

Refunded: Movimento constante, com alguns picos;

Reversed: Meio do dia, no resto muito pouco;

Backend_reversed: Poucas operações, no máx cerca de 20 e acompanha mov de
approved;

Failed: Segue quase distribuiçao normal, mas não são muitas operaçoes diárias.

'''


# Análise inicial das operações, com denied

df_denied = df[df.status == 'denied'].reset_index(drop=True)


''' calculando quanto as denieds representam no total de operações a cada min
'''

lista_denied = []

for index, row in df_denied.iterrows():
    lista_denied.append(df[(df.dia==df_denied.dia[index])&
                               (df.minutos==df_denied.minutos[index])&
                               (df.status=='denied')]['count'].tolist()[0]/
                        df[(df.dia==df_denied.dia[index])&
                           (df.minutos==df_denied.minutos[index])]['count'].sum())
df_denied['%denied'] = lista_denied

# visualizando valores relativos e absolutos 
fig, ax1 = plt.subplots()

for dia in df_denied.dia.unique():
    df_plot = df_denied[df_denied.dia == dia]
    ax1.bar(x=df_plot.minutos,height=df_plot['%denied'], label=dia)

ax1.set_xlabel('Minutos')

ax1.set_ylabel('%denied')

ax2 = ax1.twinx()

ax2.scatter(x=df_denied[df_denied.dia == '2023-01-01']['minutos'],
           y=df_denied[df_denied.dia == '2023-01-01']['count'],
           label='2023-01-01',
           s=0.3)
ax2.scatter(x=df_denied[df_denied.dia == '2023-01-02']['minutos'],
           y=df_denied[df_denied.dia == '2023-01-02']['count'],
           label='2023-01-02',
           s=0.3)

ax2.set_ylabel('count')

ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.show()


'''mesmo processo para reversed'''


df_reversed = df[df.status == 'reversed'].reset_index(drop=True)


lista_reversed = []

for index, row in df_reversed.iterrows():
    lista_reversed.append(df[(df.dia==df_reversed.dia[index])&
                               (df.minutos==df_reversed.minutos[index])&
                               (df.status=='reversed')]['count'].tolist()[0]/
                        df[(df.dia==df_reversed.dia[index])&
                           (df.minutos==df_reversed.minutos[index])]['count'].sum())
df_reversed['%reversed'] = lista_reversed
    
# visualizando valores relativos e absolutos 
fig, ax1 = plt.subplots()

for dia in df_reversed.dia.unique():
    df_plot = df_reversed[df_reversed.dia == dia]
    ax1.bar(x=df_plot.minutos,height=df_plot['%reversed'], label=dia)

ax1.set_xlabel('Minutos')

ax1.set_ylabel('%reversed')

ax2 = ax1.twinx()

ax2.scatter(x=df_reversed[df_reversed.dia == '2023-01-01']['minutos'],
           y=df_reversed[df_reversed.dia == '2023-01-01']['count'],
           label='2023-01-01',
           s=0.3)
ax2.scatter(x=df_reversed[df_reversed.dia == '2023-01-02']['minutos'],
           y=df_reversed[df_reversed.dia == '2023-01-02']['count'],
           label='2023-01-02',
           s=0.3)

ax2.set_ylabel('count')

ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.show()





''' failed operations'''


df_failed = df[df.status == 'failed'].reset_index(drop=True)


lista_failed = []

for index, row in df_failed.iterrows():
    lista_failed.append(df[(df.dia==df_failed.dia[index])&
                               (df.minutos==df_failed.minutos[index])&
                               (df.status=='failed')]['count'].tolist()[0]/
                        df[(df.dia==df_failed.dia[index])&
                           (df.minutos==df_failed.minutos[index])]['count'].sum())
df_failed['%failed'] = lista_failed
 


# visualizando valores relativos e absolutos   
fig, ax1 = plt.subplots()


for dia in df_failed.dia.unique():
    df_plot = df_failed[df_failed.dia == dia]
    ax1.bar(x=df_plot.minutos,height=df_plot['%failed'], label=dia)


ax1.set_xlabel('Minutos')


ax1.set_ylabel('%failed')

ax2 = ax1.twinx()

ax2.scatter(x=df_failed[df_failed.dia == '2023-01-01']['minutos'],
           y=df_failed[df_failed.dia == '2023-01-01']['count'],
           label='2023-01-01',
           s=0.3)
ax2.scatter(x=df_failed[df_failed.dia == '2023-01-02']['minutos'],
           y=df_failed[df_failed.dia == '2023-01-02']['count'],
           label='2023-01-02',
           s=0.3)

ax2.set_ylabel('count')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.show()




# gerando coluna com id única para cada operação
               
df['id_op'] = ''               
for index, row in df.iterrows():
               
    df['id_op'][index] = (str(df['dia'][index])
                          +str(df['time'][index]).strip()
                          +str(df['count'][index])
                          +str(df['status'][index]))


# exportando para csv
df.to_csv('Transactions_CW.csv',index=False)
