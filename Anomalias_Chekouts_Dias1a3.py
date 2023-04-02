# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:20:23 2023

@author: rafin
"""

import pandas as pd
import matplotlib.pyplot as plt

# importando as 2 bases 

check1 = pd.read_csv('https://raw.githubusercontent.com/thais-menezes/monitoring/main/checkout_1.csv')
check2 = pd.read_csv('https://raw.githubusercontent.com/thais-menezes/monitoring/main/checkout_2.csv')

''' verificando a estrutura dos dados importados'''

print(check1.dtypes)
check1.dtypes == check2.dtypes


''' como o yesterday do check2 é igual ao today do check1, juntar tudo em
1 df com 3 dias'''

dia1 = check1.drop(columns=['today']).rename(columns={'yesterday':'quant_ops'})
dia1['dia'] = 1
dia2 = check1.drop(columns=['yesterday']).rename(columns={'today':'quant_ops'})
dia2['dia'] = 2
dia3 = check2.drop(columns=['yesterday']).rename(columns={'today':'quant_ops'})
dia3['dia'] = 3

df = pd.concat([dia1,dia2,dia3]).reset_index(drop=True)


''' gráfico inicial para perceber outliers, comparando os pontos com a média
do último mês - o mês suaviza mais os padrões que a semana'''  

img, ax = plt.subplots(1,1,sharex=True)

ax.plot(pd.unique(df.time),df[df.dia==3].avg_last_month)

ax.scatter(df[df.dia==1].time,y=df[df.dia == 1].quant_ops, label = 'Dia1')
ax.scatter(df[df.dia==2].time,y=df[df.dia == 2].quant_ops, label = 'Dia2')
ax.scatter(df[df.dia==3].time,y=df[df.dia == 3].quant_ops, label = 'Dia3')
ax.set_xticklabels(df[df.dia==1].time, rotation=45)

ax.legend(loc='upper left')


''' - principal sinal de anomalia é no dia 3, das 15h as 17h, sem operações

- o fato de, fora as 3 operações descritas acima, 90% das operações das
9h as 23h estarem acima da média do último mês, pode ser explicado por um viés
do dia da semana e não necessariamente representam anomalia


- das 4 operações (de 39) abaixo da média, 2 são representativo de "queda" e
"retomada" das operações, as 14h e 18h

- possível anomalia das 8h as 10h dos dias 1 e 2, pois ficou estável quando
deveria subir e depois explodiu para valores bem acima da média histórica,
indicando possível compensação

- ideal seria ter os dados corrigidos por um fator de sazonalidade de dia da
semana/mês, mas estes são os primeiros padrões que chamam atenção ao olho'''




''' para os dias 2 e 3, é possível comparar com a semana anterior'''

# dia 2

img, ax = plt.subplots(1,1,sharex=True)

ax.scatter(df[df.dia == 2].time,y=df[df.dia==2].quant_ops, label = 'Dia2')
ax.scatter(df[df.dia == 2].time,y=df[df.dia==2].same_day_last_week,
           label = 'SemanaPassada')
ax.set_xticklabels(df[df.dia==2].time, rotation=45)

ax.legend(loc='upper left')

''' esta viz sugere que o comportamento 8h-10h(dia2) realmente é anomalia'''


# dia 3

img, ax = plt.subplots(1,1,sharex=True)

ax.scatter(df[df.dia == 3].time,y=df[df.dia==3].quant_ops, label = 'Dia3')
ax.scatter(df[df.dia == 3].time,y=df[df.dia==3].same_day_last_week,
           label = 'SemanaPassada')
ax.set_xticklabels(df[df.dia==3].time, rotation=45)

ax.legend(loc='upper left')

''' a viz confirma que ocorre anomalia 15-17h(dia3)'''



''' geração da estatística de erro para confirmar movimentos de anomalia
erro = distancia da média mensal ao quadrado
'''

df['desvio'] = round((df.quant_ops - df.avg_last_month)**2,1)



def create_ranges(df,n):
    if len(df)%n == 0:
        lista = []
        t = 0
        while t <= len(df) - int(len(df)/n):
            lista.append((range(t,t+int(len(df)/n))[0],
                          range(t,t+int(len(df)/n))[-1]+1))
            t += int(len(df)/n)
        return lista
    else:
        print('Não é possível dividir em intervalos iguais')

ranges = create_ranges(df,3)

''' gerando lista com desvio médio acumulado a cada hora do dia, para cada dia'''

lista_desvio_c = []
for range_ in ranges:
    new_df = df[range_[0]:range_[-1]]
    cum_mean = list(new_df['desvio'].cumsum() / (pd.RangeIndex(len(new_df)) + 1))
    
    for item in cum_mean:
        lista_desvio_c.append(round(item,1))
    
df['desvio_c'] = lista_desvio_c 


'''plot do desvio acumulado durante o dia'''
img, ax = plt.subplots(1,1)
for range_ in ranges:
    new_df = df[range_[0]:range_[1]]
    ax.plot(new_df.time,new_df.desvio_c,label='Dia'+str(new_df.dia.tolist()[0]))
    ax.set_xticklabels(df[df.dia==1].time, rotation=45)
    
ax.legend(loc='upper left')

''' dias 2 e 3 com desvio bem superiores ao dia 1, sugerindo maior possibilidade 
de anomalia

como visto anteriormente, no dia 2 o desvio se afasta dos outros dias perto
das 8h
no dia 3, perto das 15h
'''

''' exportando para csv, para poder inserir em database e fazer query SQL'''

df.to_csv('Checkouts_dias1a3.csv',index=False)
