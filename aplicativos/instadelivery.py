from datetime import datetime
import pandas as pd
from aplicativos import util

BALCAO = 1
DELIVERY = 2
MESA = 3

COLUNAS_DROPAR = ['client', 'store_id', 'operator_name',
                  'offline', 'address', 'observation', 'reference',
                  'source', 'driver_name', 'zipcode', 'short_id_value', 'instagram_points',
                  'mercadopago_id', 'mercadopago_status', 'mercadopago_payer_id', 'mercadopago_date_created', 'mercadopago_status_text',
                  'ifood_display_id', 'ifood_shipping_order_id', 'ifood_discount', 'ifood_order_id',
                  'pix_id', 'pix_status', 'pix_code', 'pix_image_url'
                  ]


def dropar_colunas(df):
    return df.drop(columns=COLUNAS_DROPAR)


def obter_pedidos_clientes(base_df, tipo=1):
    '''Obtem os clientes de um Dataframe.
    tipo = 1 são clientes novos
    tipo = 0 são clientes já cadastrado'''
    return base_df.loc[base_df.client_first_order == tipo]


def quantidade_pedidos_hora(df):
    '''Cria um Dataframe indexiado pela data com as colunas das horas de expediente '''
    return (df
            .groupby(
                by=[df.created_only_date,
                    df.created_only_time
                    .map(lambda x: datetime.strptime(x, '%H:%M:%S').strftime('%H'))]
            )
            .id.count().unstack().fillna(0))


def obter_pedidos_validos(df):
    return df.loc[df.cancellation_code.isna()]


def obter_pedidos_balcao(df):
    return df.loc[(df.delivery_method == BALCAO) & df.cancellation_code.isna()]


def obter_pedidos_delivery(df):
    return df.loc[(df.delivery_method == DELIVERY) & df.cancellation_code.isna()]


def obter_pedidos_mesa(df):
    return df.loc[(df.delivery_method == MESA) & df.cancellation_code.isna()]


def obter_resumo(df: pd.DataFrame) -> pd.DataFrame:
    indice_data_s = df.created_only_date.unique()
    balcao_df = obter_pedidos_balcao(df)
    mesa_df = obter_pedidos_mesa(df)
    delivery_df = obter_pedidos_delivery(df)

    resumo_df = pd.DataFrame(data={
        'dia_semana':     util.serie_dia_da_semana('created_only_date', df['created_only_date']),
        'taxa_retencao':  util.taxa_retencao(df.groupby(['created_only_date'])['client_id'].count(), obter_pedidos_clientes(df, 1).groupby(['created_only_date'])['client_id'].count()),
        'qtd_pedidos':    df.groupby(['created_only_date'])['id'].count(),
        'qtd_novos_clientes':   obter_pedidos_clientes(df, 1).loc[df.delivery_method != MESA].groupby(['created_only_date'])['client_id'].count(),
        'qtd_pedidos_balcao':   balcao_df.groupby(['created_only_date'])['id'].count(),
        'qtd_pedidos_delivery': delivery_df.groupby(['created_only_date'])['id'].count(),
        'qtd_pedidos_mesa':     mesa_df.groupby(['created_only_date'])['id'].count(),
        'vlr_total':            util.agrupar_soma(df),
        'vlr_total_balcao':     util.agrupar_soma(balcao_df),
        'vlr_total_delivery':   util.agrupar_soma(delivery_df),
        'vlr_total_mesa':       util.agrupar_soma(mesa_df),
        'ticket_medio':         round(util.agrupar_soma(df) / df.groupby('created_only_date')['id'].count(), 2),
        'ticket_medio_balcao':  round(util.agrupar_soma(balcao_df) / balcao_df.groupby('created_only_date')['id'].count(), 2),
        'ticket_medio_delivery': round(util.agrupar_soma(delivery_df) / delivery_df.groupby('created_only_date')['id'].count(), 2),
        'ticket_medio_mesa':    round(util.agrupar_soma(mesa_df) / mesa_df.groupby('created_only_date')['id'].count(), 2)
    }, index=indice_data_s).fillna(0)

    resumo_df = resumo_df.sort_index(axis=1)
    resumo_df.qtd_novos_clientes = resumo_df.qtd_novos_clientes.astype(int)
    resumo_df.qtd_pedidos_balcao = resumo_df.qtd_pedidos_balcao.astype(int)
    resumo_df.qtd_pedidos_mesa = resumo_df.qtd_pedidos_mesa.astype(int)
    resumo_df.qtd_pedidos_delivery = resumo_df.qtd_pedidos_delivery.astype(int)

    return resumo_df
