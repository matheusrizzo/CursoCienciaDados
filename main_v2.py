import os;
import pandas as pd;
import re;
import matplotlib.pyplot as plt;
import seaborn as sns;
import numpy as np;

def ReadFile(path):
    colspecs = [(0, 2), (2, 10), (12, 24), (24, 27), (27, 39), (39, 49), (56, 69), (188, 201),(202, 210)]
    colnames = ['TipoRegistro', 'DataPregao', 'Papel', 'TipoMercado', 'Emissora', 'Especificacao', 'PrecoAbertura','Strike','Vencimento']
    df = pd.read_fwf(path, colspecs=colspecs, names=colnames, skiprows=1, headers=None)
    return df

def FiltrarAcao(acao,df):
    df_acoes = df[df['Papel'] == acao]
    df_acoes['PrecoAbertura'] = df_acoes['PrecoAbertura'].apply(lambda x: x/100);
    return df_acoes

def FiltrarOpcao(emissora, especificacao, df):
    df_opcoes = df[df['TipoMercado'] == 70]
    df_opcoes = df_opcoes[df_opcoes['Emissora'].str.contains(emissora)]
    df_opcoes = df_opcoes[df_opcoes['Especificacao'].str.contains(especificacao)]
    df_opcoes['PrecoAbertura'] = df_opcoes['PrecoAbertura'].apply(lambda x: x / 100);
    df_opcoes['Strike'] = df_opcoes['Strike'].apply(lambda x: x / 100);
    df_opcoes = df_opcoes[["DataPregao", "Papel", "PrecoAbertura","Strike","Vencimento"]];
    return df_opcoes

def ObterDataVencimento(df, sigla, ano):
    print(df.head(10));
    df_vencimento = df[["Papel","Vencimento"]];
    print(df_vencimento['Vencimento'].year)
    df_vencimento = df_vencimento[df_vencimento['Vencimento'].dt.year == ano]
    print(df_vencimento.head(10))

    df_vencimento['Mes'] = df_vencimento['Papel'].apply(lambda x: ObterMesOpcao(x, sigla));
    df_vencimento = df_vencimento[["Mes", "Vencimento"]];
    df_vencimento = df_vencimento.drop_duplicates();
    df_vencimento = df_vencimento.sort_values(by=['Mes'],ascending=True)
    return df_vencimento;

def ObterMesOpcao(papel, sigla):
    if sigla+'A' in papel:
        return 1
    if sigla+'B' in papel:
        return 2
    if sigla+'C' in papel:
        return 3
    if sigla+'D' in papel:
        return 4
    if sigla+'E' in papel:
        return 5
    if sigla+'F' in papel:
        return 6
    if sigla+'G' in papel:
        return 7
    if sigla+'H' in papel:
        return 8
    if sigla+'I' in papel:
        return 9
    if sigla+'J' in papel:
        return 10
    if sigla+'K' in papel:
        return 11
    if sigla+'L' in papel:
        return 12

def ObterPrecoAcaoVencimento(df_acoes, df_vencimento):
    merged = pd.merge(df_vencimento, df_acoes, how='inner', left_on='Vencimento', right_on='DataPregao')
    merged = merged.drop_duplicates();
    merged = merged.drop(columns=['Vencimento_y'])
    merged = merged.rename(columns={"Vencimento_x": "Vencimento"})
    return merged;

def ObterPrecoOpcaoVencimentoAnterior(df_opcoes, df_vencimento, sigla):
    df_opcoes["MesOp"] = df_opcoes['Papel'].apply(lambda x: ObterMesOpcao(x, sigla)-1);
    merged = pd.merge(df_vencimento, df_opcoes, how='inner', left_on=['Vencimento','Mes'], right_on=['DataPregao','MesOp'])
    merged = merged.drop_duplicates();
    merged = merged.drop(columns=['Vencimento_y'])
    merged = merged.rename(columns={"Vencimento_x": "Vencimento"})
    return merged;

def ObterPrecoAcaoMesAnterior(df_tratado, dataPregao):
    print('asdfasdf');
    print(dataPregao);
    anoAtual = int(str(dataPregao)[0:4]);
    mesAtual = int(str(dataPregao)[4:6]);
    if mesAtual == 1:
        anoAtual = anoAtual-1;
        mesAtual = 12;
    else:
        mesAtual = mesAtual-1;
    #return df_tratado.loc[df_tratado['Mes'] == mesAtual, 'PrecoAbertura']
    return df_tratado.loc[df_tratado['DataPregao'] == mesAtual, 'PrecoAbertura']

def RemoverStrikesDesnecessarios(df_tratado, df_opcoes):
    df_acao = df_tratado[["Mes", "PrecoAbertura"]];
    df_opcoes = df_opcoes[["Mes", "Strike"]];
    df_opcoes['Strike'] = df_opcoes['Strike'].astype(float)

    print(df_acao.head(20));
    print(df_opcoes.head(20));

    df_opcoes["PrecoAcao"] = df_opcoes['Mes'].apply(lambda x:ObterPrecoAcaoMesAnterior(df_acao, x));
    print(df_opcoes.head(20));

    #for x in df_opcoes:
    #    print(x)
        #print(df_acao.loc[df_acao['Mes'] == 3, 'PrecoAbertura'])



    #df_opcoes = df_opcoes[df_opcoes['Strike'] <= preco];
    print(df_opcoes['Strike'].idxmax())
    df_opcoes = df_opcoes.groupby('Mes').agg(['max']);
    return df_opcoes;

pd.set_option('display.max_columns', None)
cotacao2020 = './data/changed/2020.txt'
ano = '2020';
papeis=[{'Papel':'PETR4','Emissora':'PETR','Especificacao':'PN','SiglaOpcao':'PETR'},{'Papel':'VALE5','Emissora':'VALE','Especificacao':'PN','SiglaOpcao':'VALE'}];

df_total = ReadFile(cotacao2020);
df_total = df_total[df_total.TipoRegistro == 1];
df_total['Vencimento'] = df_total['Vencimento'].astype(str)
df_total['Vencimento'] = df_total['Vencimento'].apply(lambda x : x[:8])
df_total = df_total.replace('99991231', np.nan);
df_total['DataPregao'] = pd.to_datetime(df_total['DataPregao'],format="%Y/%m/%d");
df_total['Vencimento'] = pd.to_datetime(df_total['Vencimento'],format="%Y/%m/%d", errors='coerce');

df_acoes = FiltrarAcao(papeis[0]['Papel'],df_total.copy());
df_opcoes = FiltrarOpcao(papeis[0]['Emissora'],papeis[0]['Especificacao'],df_total.copy());


df_vencimento = ObterDataVencimento(df_opcoes.copy(),papeis[0]['SiglaOpcao'],ano);
print(df_vencimento.head(10));

df_consolidado = ObterPrecoAcaoVencimento(df_acoes.copy(), df_vencimento.copy());
print(df_consolidado.head(10))

df_consolidado["Ano"] = df_consolidado['DataPregao'].apply(lambda x: int(str(x)[0:4]));
df_consolidado = df_consolidado[["Ano","Mes","Papel","DataPregao","PrecoAbertura","Strike"]];
df_consolidado = df_consolidado.rename(columns={"PrecoAbertura": "PrecoAcaoDia"});
df_consolidado["PrecoAcaoMesAnterior"] = df_consolidado['Mes'].apply(lambda x:ObterPrecoAcaoMesAnterior(df_consolidado, x));

print(df_consolidado)

#df_tratado_opcao = ObterPrecoOpcaoVencimentoAnterior(df_opcoes.copy(), df_vencimento.copy(), papeis[0]['SiglaOpcao'])

#df_tratado_opcao = RemoverStrikesDesnecessarios(df_tratado.copy(), df_tratado_opcao.copy());

#print(df_tratado_opcao.head(12));

#df_tratado_opcao = df_tratado_opcao[df_tratado_opcao['Papel'] == 'PETRI250']


#print(df_tratado.head(10))

#ax = sns.lineplot(x="Mes", y="PrecoAbertura", data=df_tratado);
#plt.show()



#remover tail df.drop(df.tail(2).index,inplace=True)

