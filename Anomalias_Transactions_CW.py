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


# Análise inicial das operações com denied

df_denied = df[df.status == 'denied'].reset_index(drop=True)

max_denied = df_denied['count'].max()
df_denied[df_denied['count'] == max_denied]

''' maximo de operacoes negadas foi as 16h, o que bate com gráfico anterior'''

min_denied = df_denied['count'].min()

''' mínimo é 1, conferindo que valores estão ok'''



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


fig, ax1 = plt.subplots()

# Plot the first dataset
for dia in df_denied.dia.unique():
    df_plot = df_denied[df_denied.dia == dia]
    ax1.bar(x=df_plot.minutos,height=df_plot['%denied'], label=dia)

# Set x-axis label
ax1.set_xlabel('Minutos')

# Set y-axis label for the first dataset
ax1.set_ylabel('%denied')

# Create a second y-axis object
ax2 = ax1.twinx()

# Plot the second dataset
ax2.scatter(x=df_denied[df_denied.dia == '2023-01-01']['minutos'],
           y=df_denied[df_denied.dia == '2023-01-01']['count'],
           label='2023-01-01',
           s=0.3)
ax2.scatter(x=df_denied[df_denied.dia == '2023-01-02']['minutos'],
           y=df_denied[df_denied.dia == '2023-01-02']['count'],
           label='2023-01-02',
           s=0.3)

# Set y-axis label for the second dataset
ax2.set_ylabel('count')

# Set legend for both datasets
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Show the plot
plt.show()


''' regras: - absoluta: valores maiores que 75 (2,8%)
            - relativo: valores maiores que 20%, mas somente acima dos 
            350 minutos (05:50h) (1,4%)
        
            0,5% cumpre as duas restrições, indicando que elas não estão 
            necessariamente interligadas
            3,6% cumprem uma restrição ou outra -> 83 operações (~41 por dia)
            
            o grande percentual de denied de madrugada (0h - 6h) pode ser já 
            por conta de critérios pré estabelecidos para este horário, de 
            maior risco
'''




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
    

fig, ax1 = plt.subplots()

# Plot the first dataset
for dia in df_reversed.dia.unique():
    df_plot = df_reversed[df_reversed.dia == dia]
    ax1.bar(x=df_plot.minutos,height=df_plot['%reversed'], label=dia)

# Set x-axis label
ax1.set_xlabel('Minutos')

# Set y-axis label for the first dataset
ax1.set_ylabel('%reversed')

# Create a second y-axis object
ax2 = ax1.twinx()

# Plot the second dataset
ax2.scatter(x=df_reversed[df_reversed.dia == '2023-01-01']['minutos'],
           y=df_reversed[df_reversed.dia == '2023-01-01']['count'],
           label='2023-01-01',
           s=0.3)
ax2.scatter(x=df_reversed[df_reversed.dia == '2023-01-02']['minutos'],
           y=df_reversed[df_reversed.dia == '2023-01-02']['count'],
           label='2023-01-02',
           s=0.3)

# Set y-axis label for the second dataset
ax2.set_ylabel('count')

# Set legend for both datasets
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Show the plot
plt.show()


''' Regras: - absoluto: acima de 80 por minuto (5%)
            - relativo: acima de 30% (5,2%)
            
            1,8% cumpre as duas condições e 8,5% uma das duas, resultando
            em 125 operações (~62 por dia)
            
            possível que um dos dias tenha tido comportamento atípico

'''




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
    
fig, ax1 = plt.subplots()

# Plot the first dataset
for dia in df_failed.dia.unique():
    df_plot = df_failed[df_failed.dia == dia]
    ax1.bar(x=df_plot.minutos,height=df_plot['%failed'], label=dia)

# Set x-axis label
ax1.set_xlabel('Minutos')

# Set y-axis label for the first dataset
ax1.set_ylabel('%failed')

# Create a second y-axis object
ax2 = ax1.twinx()

# Plot the second dataset
ax2.scatter(x=df_failed[df_failed.dia == '2023-01-01']['minutos'],
           y=df_failed[df_failed.dia == '2023-01-01']['count'],
           label='2023-01-01',
           s=0.3)
ax2.scatter(x=df_failed[df_failed.dia == '2023-01-02']['minutos'],
           y=df_failed[df_failed.dia == '2023-01-02']['count'],
           label='2023-01-02',
           s=0.3)

# Set y-axis label for the second dataset
ax2.set_ylabel('count')

# Set legend for both datasets
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Show the plot
plt.show()


''' pico das failed operations ligado no segundo pico de operaçoes, no período
da tarde

    Regra: - absoluta: acima de 13 (5%)
           - relativa: acima de 2,3% (4,5%)
           
           3,6% cumprem as duas e 4,5% cumprem pelo menos uma:
               10 operações, 5 por dia'''
               
df['id_op'] = ''               
for index, row in df.iterrows():
               
    df['id_op'][index] = (str(df['dia'][index])
                          +str(df['time'][index]).strip()
                          +str(df['count'][index])
                          +str(df['status'][index]))

df.to_csv('Transactions_CW.csv',index=False)
