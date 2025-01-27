import pandas as pd
from datetime import datetime
from aplicativos import instadelivery
from aplicativos import querodelivery
from aplicativos import util


def consolidar_instadelivery(arquivo):
    instadf = pd.read_csv(arquivo)
    return consolidar_df_instadelivery(instadf)


def consolidar_df_instadelivery(instadf: pd.DataFrame):
    insta_colunas_pedidos = [
        'id',
        'client_id',
        'client_name',
        'client_phone',
        'delivery_method',
        'total',
        'client_first_order',
        'client_total_orders',
        'created_date',  # criacao do pedido
        'updated_at',  # ultima atualizacao registrada
        'payment_id', 'payment_name'
    ]

    instadf = instadelivery.obter_pedidos_validos(
        instadf)[insta_colunas_pedidos].drop_duplicates(subset=['id'])

    instadf.id = instadf.id.astype(str)
    instadf.client_id = instadf.client_id.astype(str)
    instadf.client_name = instadf.client_name.fillna('').astype(str)
    instadf.client_phone = instadf.client_phone.fillna(0).astype(int).astype(str)
    instadf.total = instadf.total.astype(float)
    instadf.client_first_order = instadf.client_first_order.astype(bool)
    instadf.client_total_orders = instadf.client_total_orders.astype(int)

    instadf['plataforma'] = 'INSTADELIVERY'
    instadf['segmento'] = instadf.delivery_method.apply(
        lambda x: util.obter_nome_segmento(x))
    instadf['forma_pg'] = instadf.payment_id.apply(
        lambda x: util.obter_nome_forma_pagamento(util.obter_forma_pagamento_usado_no_app(x)))

    instadf.created_date = instadf.created_date.apply(
        lambda data: datetime.strptime(data, '%d/%m/%Y %H:%M:%S'))
    instadf.updated_at = instadf.updated_at.apply(
        lambda data: datetime.strptime(data, '%Y-%m-%d %H:%M:%S'))

    return pd.DataFrame(data={
        'pedidoId': instadf['id'],
        'usuarioId': instadf['client_id'],
        'usuarioNome': instadf['client_name'],
        'celularUsuario': instadf['client_phone'],
        'total': instadf['total'],
        'total_pago_cliente': instadf['total'],
        'taxa_plataforma': 0.0,
        'tipo_venda': instadf['delivery_method'],
        'qtdPedidosUsuario': instadf['client_total_orders'],
        'datahora': instadf['created_date'],
        'formaPagamento': instadf['payment_name'],
        'primeiroPedido': instadf['client_first_order'],
        'plataforma': instadf['plataforma'],
        'segmento': instadf['segmento'],
        'forma_pagamento': instadf['forma_pg'],
    })


def consolidar_querodelivery(arquivo):
    querodf = pd.read_csv(arquivo)
    return consolidar_df_querodelivery(querodf)


def consolidar_df_querodelivery(querodf):
    quero_colunas_pedidos = [
        'pedidoId',
        'usuarioId',
        'usuarioNome',
        'celularUsuario',
        'precoTotal',
        'tipo_venda',
        'usuarioQtdPedidosEntreguesPlace',
        'createdAt',  # criacao do pedido
        'updatedAt',  # ultima atualizacao registrada
        'formaPagamento'
    ]

    querodf = querodelivery.obter_pedidos_validos(
        querodf)[quero_colunas_pedidos]\
        .drop_duplicates(subset=['pedidoId'])\
        .fillna('')\
        .reset_index()

    querodf.pedidoId = querodf.pedidoId.astype(str)
    querodf.usuarioId = ""#querodf.usuarioId.astype(str)
    querodf.usuarioNome = ""#querodf.usuarioNome.astype(str)
    querodf.celularUsuario = ""#querodf.celularUsuario.astype('Int64').astype(str)

    querodf['client_first_order'] = querodf.usuarioQtdPedidosEntreguesPlace.apply(
        lambda x: x == 0)

    querodf['plataforma'] = 'QUERODELIVERY'
    querodf['segmento'] = querodf.tipo_venda.apply(
        lambda x: util.obter_nome_segmento(x))
    querodf['forma_pg'] = querodf.formaPagamento.apply(
        lambda x: util.obter_nome_forma_pagamento(util.obter_forma_pagamento_usado_no_app(x)))

    querodf['datahora'] = pd.to_datetime(querodf['createdAt'], format="%Y-%m-%dT%H:%M:%S.%fZ").dt.tz_localize(
        'UTC').dt.tz_convert('America/Sao_Paulo').dt.tz_localize(None).apply(lambda d: d.replace(microsecond=0))
    
    return pd.DataFrame(data={
        'pedidoId': querodf['pedidoId'],
        'usuarioId': querodf['usuarioId'],
        'usuarioNome': querodf['usuarioNome'],
        'celularUsuario': querodf['celularUsuario'],
        'total': querodf['precoTotal'],
        'total_pago_cliente': querodf.apply(querodelivery_aplicar_taxa_no_total_em_pagamento_tipo_credito, axis=1),
        'taxa_plataforma': querodf['precoTotal'].apply(querodelivery_aplicar_taxa_de_plataforma),
        'tipo_venda': querodf['tipo_venda'],
        'qtdPedidosUsuario': 0,
        'datahora': querodf['datahora'],
        'formaPagamento': querodf['formaPagamento'],
        'primeiroPedido': querodf['client_first_order'],
        'plataforma': querodf['plataforma'],
        'segmento': querodf['segmento'],
        'forma_pagamento': querodf['forma_pg'],
    })


TAXA_ACRESCIMO_NO_PAGAMENTO_TIPO_CREDITO = 4/100
TAXA_VENDA_QUERODELIVERY = 8/100


def querodelivery_aplicar_taxa_no_total_em_pagamento_tipo_credito(row):
    _col_total_ = 'precoTotal'
    return row[_col_total_] + (row[_col_total_] * TAXA_ACRESCIMO_NO_PAGAMENTO_TIPO_CREDITO) if row['forma_pg'] == 'CREDITO' else row[_col_total_]


def querodelivery_aplicar_taxa_de_plataforma(row):
    return row * TAXA_VENDA_QUERODELIVERY
