from aplicativos import util
import pandas as pd

COLUNAS_DROPAR = []
BALCAO = 1
DELIVERY = 2


def dropar_colunas(df):
    return df.drop(columns=COLUNAS_DROPAR)


def obter_pedidos_clientes(base_df, tipo=1):
    '''Obtem os clientes de um Dataframe.
    tipo = 1 são clientes novos
    tipo = 0 são clientes já cadastrado'''
    return base_df.loc[base_df.client_first_order == tipo]


def obter_pedidos_validos(df):
    return df.loc[(df.status == 'ENTREGUE')]


def obter_pedidos_balcao(df):
    return df.loc[(df.tipo_venda == BALCAO) & (df.status == 'ENTREGUE')]


def obter_pedidos_delivery(df):
    return df.loc[(df.tipo_venda == DELIVERY) & (df.status == 'ENTREGUE')]


_id = 'pedidoId'
_cliente_id = 'usuarioId'
_total = 'precoTotal'
_data = 'created_only_date'
_primeira_compra = 'usuarioQtdPedidosEntreguesPlace'


def obter_resumo(pedidos_df):
    indice_data_s = pedidos_df[_data].unique()
    delivery_df = obter_pedidos_delivery(pedidos_df)
    balcao_df = obter_pedidos_balcao(pedidos_df)

    groupby_data = pedidos_df.groupby([_data])

    df = pd.DataFrame(data={
        'dia_semana': util.serie_dia_da_semana(_data, pedidos_df[_data]),

        'qtd_pedidos': groupby_data[_id].count(),
        'qtd_pedidos_balcao': balcao_df.groupby([_data])[_id].count(),
        'qtd_pedidos_delivery': delivery_df.groupby([_data])[_id].count(),

        'vlr_total': groupby_data[_total].sum(),
        'vlr_total_balcao': balcao_df.groupby(_data)[_total].sum(),
        'vlr_total_delivery': delivery_df.groupby(_data)[_total].sum(),

        'ticket_medio': round(groupby_data[_total].sum() / groupby_data[_id].count(), 2),
        'ticket_medio_balcao': round(balcao_df.groupby([_data])[_total].sum() / balcao_df.groupby([_data])[_id].count(), 2),
        'ticket_medio_delivery': round(delivery_df.groupby([_data])[_total].sum() / delivery_df.groupby([_data])[_id].count(), 2),

        'qtd_novos_clientes': pedidos_df.loc[pedidos_df[_primeira_compra] == 0].groupby([_data])[_cliente_id].count().reindex(pedidos_df[_data].unique(), fill_value=0),

        # contagem de todos os clientes E contagem dos novos clientes
        'taxa_retencao': util.taxa_retencao(groupby_data[_cliente_id].count(), pedidos_df.loc[pedidos_df[_primeira_compra] == True].groupby([_data])[_cliente_id].count()),

    }, index=indice_data_s).fillna(0)
    df = df.sort_index(axis=1, ascending=False)
    df.qtd_pedidos = df.qtd_pedidos.astype(int)
    df.qtd_pedidos_balcao = df.qtd_pedidos_balcao.astype(int)
    df.qtd_pedidos_delivery = df.qtd_pedidos_delivery.astype(int)
    df.qtd_novos_clientes = df.qtd_novos_clientes.astype(int)

    return df
