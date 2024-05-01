import unittest
import pandas as pd
import datetime
from pandas.testing import assert_series_equal

import consolidador


class TestConsolidador(unittest.TestCase):

    def test_querodelivery_aplicar_taxa_cartao(self):
        df_entrada = pd.DataFrame(
            {'precoTotal': [10.5, 10.5, 50.2],
             'forma_pg': ['CREDITO', 'DEBITO', 'CREDITO']}
        )
        s_saida_esperado = pd.Series([10.92, 10.5, 52.208])

        s_saida = df_entrada.apply(
            consolidador.querodelivery_aplicar_taxa_no_total_em_pagamento_tipo_credito, axis=1)

        assert_series_equal(s_saida, s_saida_esperado)

    def test_querodelivery_aplicar_taxa_de_plataforma(self):
        df_entrada = pd.DataFrame(
            {'precoTotal': [10.5, 10.5, 50.2],
             'forma_pg': ['CREDITO', 'DEBITO', 'CREDITO']}
        )
        s_saida_esperado = pd.Series([0.84, 0.84, 4.016])

        s_saida = df_entrada['precoTotal'].apply(
            consolidador.querodelivery_aplicar_taxa_de_plataforma)

        assert_series_equal(s_saida, s_saida_esperado, check_names=False)

    def test_consolidador(self):
        # Dados fornecidos
        data = [
            {
                'pedidoId': '6625b12780d9d94eebfb3bba',
                'codigo': 'V49JJ9',
                'carrinhoId': '647d2e949ba29100f336f9d9',
                'status': 'ENTREGUE',
                'usuarioId': '5eac6b6592e2eb0025c02738',
                'usuarioNome': 'Silvo',
                'celularUsuario': '5583999999999',
                'usuarioQtdPedidosEntreguesPlace': 7,
                'usuarioQtdPedidosEntreguesPlataforma': 85,
                'precoTotal': 56,
                'precoProdutos': 52,
                'quantidadeProdutos': 1,
                'solicitacaoCancelamentoEfetuado': False,
                'isPedidoPrimeiraCompraPlace': False,
                'formaPagamento': 'DINHEIRO',
                'tipo_venda': 2,
                'createdAt': '2024-04-22T00:36:55.253Z',
                'updatedAt': '2024-04-22T01:48:31.176Z',
                'minutosEntrega': 71,
                'previsaoMinutosEntrega': 62
            },
            {
                # o duplicado vai ser removido pela funçao
                'pedidoId': '6625b12780d9d94eebfb3bba',
                'codigo': 'V49JJ9',
                'carrinhoId': '647d2e949ba29100f336f9d9',
                'status': 'ENTREGUE',
                'usuarioId': '5eac6b6592e2eb0025c02738',
                'usuarioNome': 'Silvo',
                'celularUsuario': '5583999999999',
                'usuarioQtdPedidosEntreguesPlace': 7,
                'usuarioQtdPedidosEntreguesPlataforma': 85,
                'precoTotal': 56,
                'precoProdutos': 52,
                'quantidadeProdutos': 1,
                'solicitacaoCancelamentoEfetuado': False,
                'isPedidoPrimeiraCompraPlace': False,
                'formaPagamento': 'DINHEIRO',
                'tipo_venda': 2,
                'createdAt': '2024-04-22T00:36:55.253Z',
                'updatedAt': '2024-04-22T01:48:31.176Z',
                'minutosEntrega': 71,
                'previsaoMinutosEntrega': 62
            },
            {
                'pedidoId': '6625a6975ef791ae1607390d',
                'codigo': '90CUUK',
                'carrinhoId': '6625a5c9ae7aa352fb775e6c',
                'status': 'ENTREGUE',
                'usuarioId': '5dc32a997affd700322ac6bf',
                'usuarioNome': 'Silva',
                'celularUsuario': '5583888888888',
                'usuarioQtdPedidosEntreguesPlace': 0,
                'usuarioQtdPedidosEntreguesPlataforma': 69,
                'precoTotal': 64,
                'precoProdutos': 60,
                'quantidadeProdutos': 1,
                'solicitacaoCancelamentoEfetuado': False,
                'isPedidoPrimeiraCompraPlace': False,
                'formaPagamento': 'VISA_CREDITO',
                'tipo_venda': 1,
                'createdAt': '2024-04-21T23:51:51.325Z',
                'updatedAt': '2024-04-22T01:48:30.256Z',
                'minutosEntrega': 116,
                'previsaoMinutosEntrega': 49
            }
        ]

        # Criando o DataFrame
        df = pd.DataFrame(data)

        df_saida = consolidador.consolidar_df_querodelivery(df)

        assert_series_equal(
            pd.Series([7, 0]), df_saida['qtdPedidosUsuario'], check_names=False)
        
        assert_series_equal(pd.Series(
            [datetime.datetime(2024, 4, 21, 21, 36, 55,tzinfo=None), datetime.datetime(2024, 4, 21, 20, 51, 51,tzinfo=None)]), df_saida['datahora'], check_names=False)
        assert_series_equal(pd.Series(
            ['DINHEIRO', 'VISA_CREDITO']), df_saida['formaPagamento'], check_names=False)

        assert_series_equal(pd.Series(
            ['QUERODELIVERY', 'QUERODELIVERY']), df_saida['plataforma'], check_names=False)
        assert_series_equal(
            pd.Series(['DELIVERY', 'BALCAO']), df_saida['segmento'], check_names=False)
        assert_series_equal(pd.Series(
            ['DINHEIRO', 'CREDITO']), df_saida['forma_pagamento'], check_names=False)

        df_3bba = df_saida[df_saida.pedidoId == '6625b12780d9d94eebfb3bba']

        self.assertEqual(df_3bba.total.values, 56)
        self.assertEqual(df_3bba.primeiroPedido.values, False)
        self.assertEqual(df_3bba.total_pago_cliente.values, 56)
        self.assertEqual(df_3bba.taxa_plataforma.values, 4.48)

        df_390d = df_saida[df_saida.pedidoId == '6625a6975ef791ae1607390d']

        self.assertEqual(df_390d.total.values, 64)
        self.assertEqual(df_390d.primeiroPedido.values, True)
        self.assertEqual(df_390d.total_pago_cliente.values, 66.56)
        self.assertEqual(df_390d.taxa_plataforma.values, 5.12)

    def test_instadelivery_consolidador(self):
        data =[
            {
                'id': '0123',
                'client_id': '987654000',
                'client_name': 'Teste name',
                'client_phone': 83988885555,
                'delivery_method': 2,
                'total': 50,
                'client_first_order': 1, # eh o primeiro pedido
                'client_total_orders': 1, # o primeiro pedido ja consta no total
                'created_date': '01/01/2024 19:11:26',
                'updated_at': '2024-01-01 20:34:14',
                'payment_id': 2, 
                'payment_name': 'DINHEIRO',
                'cancellation_code': None # pedido valido
            },
        ]

        df = pd.DataFrame(data)

        consolidado = consolidador.consolidar_df_instadelivery(df)

        assert_series_equal(pd.Series(['0123'], name='pedidoId'), consolidado['pedidoId'])
        assert_series_equal(pd.Series(['987654000'], name='usuarioId'), consolidado['usuarioId'])
        assert_series_equal(pd.Series(['Teste name'], name='usuarioNome'), consolidado['usuarioNome'])
        assert_series_equal(pd.Series(['83988885555'], name='celularUsuario'), consolidado['celularUsuario'])
        assert_series_equal(pd.Series([50.0], name='total'), consolidado['total'])
        assert_series_equal(pd.Series([50.0], name='total_pago_cliente'), consolidado['total_pago_cliente'])
        assert_series_equal(pd.Series([0.0], name='taxa_plataforma'), consolidado['taxa_plataforma'])
        assert_series_equal(pd.Series([2], name='tipo_venda'), consolidado['tipo_venda'])
        assert_series_equal(pd.Series([1], name='qtdPedidosUsuario'), consolidado['qtdPedidosUsuario'])
        
        assert_series_equal(pd.Series(datetime.datetime(2024, 1, 1, 19, 11, 26), name='datahora'), consolidado['datahora'])
        assert_series_equal(pd.Series(['DINHEIRO'], name='formaPagamento'), consolidado['formaPagamento'])
        assert_series_equal(pd.Series([True], name='primeiroPedido'), consolidado['primeiroPedido'])
        assert_series_equal(pd.Series(['INSTADELIVERY'], name='plataforma'), consolidado['plataforma'])
        assert_series_equal(pd.Series(['DELIVERY'], name='segmento'), consolidado['segmento'])
        assert_series_equal(pd.Series(['DINHEIRO'], name='forma_pagamento'), consolidado['forma_pagamento'])

    def test_instadelivery_consolidador_varios_dados(self):
        data =[
            {
                'id': '0123',
                'client_id': '987654000',
                'client_name': 'Teste name',
                'client_phone': 83988885555,
                'delivery_method': 2,
                'total': 50,
                'client_first_order': 1, # eh o primeiro pedido
                'client_total_orders': 1, # o primeiro pedido ja consta no total
                'created_date': '01/01/2024 19:11:26',
                'updated_at': '2024-01-01 20:34:14',
                'payment_id': 2, 
                'payment_name': 'DINHEIRO',
                'cancellation_code': None # pedido valido
            },
            {
                'id': '0456',
                'client_id': '654321000',
                'client_name': 'Usuario teste',
                'client_phone': 83988884444,
                'delivery_method': 1,
                'total': 54.45,
                'client_first_order': 0, # eh o primeiro pedido
                'client_total_orders': 12, # o primeiro pedido ja consta no total
                'created_date': '02/02/2024 20:11:26',
                'updated_at': '2024-01-01 20:34:14',
                'payment_id': 2, 
                'payment_name': 'DINHEIRO',
                'cancellation_code': None # pedido valido
            },
            {
                'id': '0456', # pedidos duplicados são removidos na consolidacao
                'client_id': '654321000',
                'client_name': 'Usuario teste',
                'client_phone': 83988884444,
                'delivery_method': 1,
                'total': 54.45,
                'client_first_order': 0,
                'client_total_orders': 12,
                'created_date': '02/02/2024 20:11:26',
                'updated_at': '2024-01-01 20:34:14',
                'payment_id': 2, 
                'payment_name': 'DINHEIRO',
                'cancellation_code': None 
            },
        ]

        df = pd.DataFrame(data)

        consolidado = consolidador.consolidar_df_instadelivery(df)

        assert_series_equal(pd.Series(['0123','0456'], name='pedidoId'), consolidado['pedidoId'])
        assert_series_equal(pd.Series(['987654000','654321000'], name='usuarioId'), consolidado['usuarioId'])
        assert_series_equal(pd.Series(['Teste name','Usuario teste'], name='usuarioNome'), consolidado['usuarioNome'])
        assert_series_equal(pd.Series(['83988885555', '83988884444'], name='celularUsuario'), consolidado['celularUsuario'])
        assert_series_equal(pd.Series([50.0, 54.45], name='total'), consolidado['total'])
        assert_series_equal(pd.Series([50.0, 54.45], name='total_pago_cliente'), consolidado['total_pago_cliente'])
        assert_series_equal(pd.Series([0.0, 0.0], name='taxa_plataforma'), consolidado['taxa_plataforma'])
        assert_series_equal(pd.Series([2, 1], name='tipo_venda'), consolidado['tipo_venda'])
        assert_series_equal(pd.Series([1, 12], name='qtdPedidosUsuario'), consolidado['qtdPedidosUsuario'])
        
        assert_series_equal(pd.Series([datetime.datetime(2024, 1, 1, 19, 11, 26), datetime.datetime(2024, 2, 2, 20, 11, 26)], name='datahora'), consolidado['datahora'])
        assert_series_equal(pd.Series(['DINHEIRO', 'DINHEIRO'], name='formaPagamento'), consolidado['formaPagamento'])
        assert_series_equal(pd.Series([True, False], name='primeiroPedido'), consolidado['primeiroPedido'])
        assert_series_equal(pd.Series(['INSTADELIVERY', 'INSTADELIVERY'], name='plataforma'), consolidado['plataforma'])
        assert_series_equal(pd.Series(['DELIVERY', 'BALCAO'], name='segmento'), consolidado['segmento'])
        assert_series_equal(pd.Series(['DINHEIRO', 'DINHEIRO'], name='forma_pagamento'), consolidado['forma_pagamento'])
