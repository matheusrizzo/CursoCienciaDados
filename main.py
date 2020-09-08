import pandas as pd;
import matplotlib.pyplot as plt;
import seaborn as sns;

def ReadFile(path):
    colspecs = [(0, 2), (2, 10), (12, 24), (24, 27), (39, 41), (82,95), (69,82)]
    colnames = ['TipoRegistro', 'DataPregao', 'Papel', 'TipoMercado', 'Especificacao', 'MenorPreco', 'MaiorPreco']
    df = pd.read_fwf(path, colspecs=colspecs, names=colnames, skiprows=1, headers=None)
    return df

def FiltrarAcao(df):
    df_acoes = df[df['TipoMercado'] == 10]
    df_acoes['MenorPreco'] = df_acoes['MenorPreco'].apply(lambda x: x/100);
    df_acoes['MaiorPreco'] = df_acoes['MaiorPreco'].apply(lambda x: x/100);
    return df_acoes

def GerarVariacao(df):
    df['Variacao'] = round(((df['MaiorPreco'] - df['MenorPreco'])/df['MenorPreco'])*100,2)
    return df;

def LimparColunas(df):
    df = df[['Papel', 'Variacao', 'Especificacao']];
    return df;

def FiltrarAcoesON_PN(df):
    df = df.loc[(df['Especificacao'].str.contains("PN")) | (df['Especificacao'].str.contains("ON"))]
    return df;

def AgruparPapeis(df):
    df = df.groupby([df['Papel'],df['Especificacao']],as_index=False).sum();
    return df;

pd.set_option('display.max_columns', None)
cotacao2020 = './data/changed/2020.txt'
cotacao2019 = './data/changed/2019.txt'
cotacao2018 = './data/changed/2018.txt'
cotacao2017 = './data/changed/2017.txt'
cotacao2016 = './data/changed/2016.txt'
cotacao2015 = './data/changed/2015.txt'
#ano = '2020';

df_total = ReadFile(cotacao2020);
df_total2019 = ReadFile(cotacao2019);
df_total2018 = ReadFile(cotacao2018);
df_total2017 = ReadFile(cotacao2017);
df_total2016 = ReadFile(cotacao2016);
df_total2015 = ReadFile(cotacao2015);

df_total = df_total.append(df_total2019, ignore_index=True);
df_total = df_total.append(df_total2018, ignore_index=True)
df_total = df_total.append(df_total2017, ignore_index=True)
df_total = df_total.append(df_total2016, ignore_index=True)
df_total = df_total.append(df_total2015, ignore_index=True)

df_total = df_total[df_total.TipoRegistro == 1];
df_total['DataPregao'] = pd.to_datetime(df_total['DataPregao'],format="%Y/%m/%d");

df_acoes = FiltrarAcao(df_total.copy());
df_acoes = GerarVariacao(df_acoes.copy());
df_acoes = LimparColunas(df_acoes.copy());
df_acoes = FiltrarAcoesON_PN(df_acoes.copy());
df_acoes = AgruparPapeis(df_acoes.copy());
df_acoes = df_acoes.sort_values(by=['Variacao'],ascending=False)
df_acoes = df_acoes.head(15);
minTotal = df_acoes['Variacao'].min()*0.7;
maxTotal = df_acoes['Variacao'].max();
print(df_acoes)

ax = sns.catplot(x="Variacao", y="Papel", kind="bar", data=df_acoes);
ax.set(xlim=(minTotal, maxTotal));

plt.show()
