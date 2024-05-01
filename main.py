import os
from cloudevents.http import CloudEvent
from google.cloud import storage
from io import BytesIO

import pandas_gbq
import consolidador
import functions_framework
import aplicativos.util as util
import pandas as pd


@functions_framework.cloud_event
def consolidar_plataformas(cloud_event: CloudEvent) -> tuple:
    """This function is triggered by a change in a storage bucket.

    Args:
        cloud_event: The CloudEvent that triggered this function.
    Returns:
        empty
    """

    DESTINATION_TABLE = os.environ.get(
        "DESTINATION_TABLE_CONSOLIDADOR_PLATAFORMAS")
    PROJECT_ID = os.environ.get("PROJECT_ID")

    data = cloud_event.data

    nome_bucket = data['bucket']
    nome_arquivo = data['name']

    if nome_arquivo.startswith("INSTADELIVERY"):
        print("Fluxo para INSTADELIVERY")
        consolidar = consolidador.consolidar_instadelivery
    elif nome_arquivo.startswith("QUERODELIVERY"):
        print("Fluxo para QUERODELIVERY")
        consolidar = consolidador.consolidar_querodelivery
    else:
        print(
            f"Arquivo {nome_arquivo} não corresponde a nenhum dos padrões esperados")
        return

    # Storage Adapter
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(nome_bucket)
    blob = bucket.blob(data['name'])

    buffer = BytesIO(blob.download_as_bytes())
    # ---

    resultadodf = consolidar(buffer)

    # Dominio
    # Define os tipos das colunas para definir o schema do BigQuery
    resultadodf.pedidoId = resultadodf.pedidoId.astype(str)
    resultadodf.usuarioId = resultadodf.usuarioId.astype(str)
    resultadodf.usuarioNome = resultadodf.usuarioNome.astype(str)
    resultadodf.celularUsuario = resultadodf.celularUsuario.astype(str)
    resultadodf.tipo_venda = resultadodf.tipo_venda.astype(int)
    resultadodf.qtdPedidosUsuario = resultadodf.qtdPedidosUsuario.astype(int)
    resultadodf.formaPagamento = resultadodf.formaPagamento.astype(str)
    resultadodf.primeiroPedido = resultadodf.primeiroPedido.astype(int)
    resultadodf.plataforma = resultadodf.plataforma.astype(str)
    resultadodf.segmento = resultadodf.segmento.astype(str)
    resultadodf.forma_pagamento = resultadodf.forma_pagamento.astype(str)
    # ---

    print(
        f"Consolidaçao do arquivo {nome_arquivo} concluida. Agora enviar para o BQ")
    pandas_gbq.to_gbq(resultadodf, destination_table=DESTINATION_TABLE,
                      project_id=PROJECT_ID, if_exists='append')
    print("upload concluido")

    return


@functions_framework.cloud_event
def adicionar_tamanho_item(cloud_event: CloudEvent) -> tuple:
    DESTINATION_TABLE = "itens-instadelivery"
    PROJECT_ID = os.environ.get("PROJECT_ID")

    data = cloud_event.data

    nome_bucket = data['bucket']
    nome_arquivo = data['name']

    # Storage Adapter
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(nome_bucket)
    blob = bucket.blob(nome_arquivo)

    buffer = BytesIO(blob.download_as_bytes())
    # ---
    df = pd.read_csv(buffer)
    df['tamanho'] = df.item_id.apply(util.obter_tamanho_do_item_id)

    pandas_gbq.to_gbq(df, destination_table=DESTINATION_TABLE,
                      project_id=PROJECT_ID, if_exists='append')


@functions_framework.cloud_event
def adicionar_id_sabor_complementos(cloud_event: CloudEvent) -> tuple:
    DESTINATION_TABLE = "complementos-instadelivery"
    PROJECT_ID = os.environ.get("PROJECT_ID")
    data = cloud_event.data

    nome_bucket = data['bucket']
    nome_arquivo = data['name']

    # Storage Adapter
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(nome_bucket)
    blob = bucket.blob(nome_arquivo)

    buffer = BytesIO(blob.download_as_bytes())
    # ---
    df = pd.read_csv(buffer)

    df['id_sabor'] = df.complement_id.apply(util.obter_sabor_do_complement_id)
    df['nome_sabor'] = df.id_sabor.apply(util.obter_nome_sabor)

    pandas_gbq.to_gbq(df, destination_table=DESTINATION_TABLE,
                      project_id=PROJECT_ID, if_exists='append')