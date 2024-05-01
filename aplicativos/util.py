import pandas as pd
from datetime import datetime
import pytz
import numpy

# Estas sao as formas de pagamentos utilizadas
FORMAS_PAGAMENTO_DF = pd.read_csv('./dominio/formas_pagamento.csv')
CODIGO_APP_FORMA_PG_DF = pd.read_csv('./dominio/codigo_app_forma_pg.csv')
SEGMENTOS_DF = pd.read_csv('./dominio/segmentos.csv')
TAMANHOS_DF = pd.read_csv('./dominio/tamanhos.csv')
ITENS_DF = pd.read_csv('./dominio/itens.csv')
SABORES_DF = pd.read_csv('./dominio/sabores.csv')

def obter_sabor_do_complement_id(complement_id: int):
    if not complement_id: return pd.NA
    return SABORES_DF.loc[SABORES_DF.id == complement_id, 'id_interno'].values[0] if complement_id in SABORES_DF.id.values else pd.NA

def obter_nome_sabor(id: int):
    if not isinstance(id, numpy.number): return pd.NA
    return SABORES_DF.loc[SABORES_DF.id_interno == id, 'nome'].values[0] if id in SABORES_DF.id_interno.values else pd.NA


def obter_item_do_group_id(group_id: int):
    return ITENS_DF.loc[ITENS_DF.group_id == group_id, 'item'].values[0] if group_id in ITENS_DF.group_id.values else ''

def obter_tamanho_do_item_id(item_id: int):
    return TAMANHOS_DF.loc[TAMANHOS_DF.item_id == item_id, 'tamanho'].values[0] if item_id in TAMANHOS_DF.item_id.values else ''

def obter_nome_segmento(numero):
    # Verificar se o número está presente no DataFrame
    if numero in SEGMENTOS_DF['id'].values:
        # Obter o nome correspondente usando loc
        nome_forma_pagamento = SEGMENTOS_DF.loc[SEGMENTOS_DF['id']
                                                == numero, 'nome'].values[0]
        return nome_forma_pagamento
    else:
        print('segmento nao encontrado ' + str(numero))
        return ''


def obter_nome_forma_pagamento(numero):
    # Verificar se o número está presente no DataFrame
    if numero in FORMAS_PAGAMENTO_DF['id'].values:
        # Obter o nome correspondente usando loc
        nome_forma_pagamento = FORMAS_PAGAMENTO_DF.loc[FORMAS_PAGAMENTO_DF['id']
                                                       == numero, 'nome'].values[0]
        return nome_forma_pagamento
    else:
        return ''


def obter_forma_pagamento_usado_no_app(num):
    if str(num) in CODIGO_APP_FORMA_PG_DF['codigo_app'].values:
        # Obter o nome correspondente usando loc
        nome_forma_pagamento = CODIGO_APP_FORMA_PG_DF.loc[CODIGO_APP_FORMA_PG_DF['codigo_app']
                                                          == str(num), 'id_forma_pagamento'].values[0]
        return nome_forma_pagamento
    print('forma pagamento nao encontrado ' + str(num))
    return ''


def serie_dia_da_semana(nome, index_list, formato_data='%d/%m/%Y') -> pd.Series:
    dias_semana = ('segunda', 'terça', 'quarta',
                   'quinta', 'sexta', 'sabado', 'domingo')
    dias = {}
    for dt in index_list:
        dias[dt] = dias_semana[datetime.strptime(dt, formato_data).weekday()]
    return pd.Series(dias, name=nome)


def taxa_retencao(totalClientes_s, novosClientes_s):
    for idx in totalClientes_s.index:
        if (idx not in novosClientes_s.index):
            novosClientes_s[idx] = 0

    return round(((totalClientes_s - novosClientes_s) / totalClientes_s) * 100, 2)


def transformar_data_em_datetime(formato_data='%d/%m/%Y', tzorigem='GMT', tzdestino='America/Sao_Paulo'):
    # "%Y-%m-%dT%H:%M:%S.%fZ"
    return lambda data: datetime.strptime(data, formato_data).replace(tzinfo=pytz.timezone(tzorigem)).astimezone(pytz.timezone(tzdestino))


def agrupar_soma(df: pd.DataFrame, date_column='created_only_date', value_column='total') -> pd.Series:
    return df.groupby(date_column)[value_column].sum()
