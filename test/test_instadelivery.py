import unittest
import pandas as pd
import numpy as np

from aplicativos.instadelivery import *


class TestInstadelivery():

    def test_obter_pedidos_balcao(self):

        df_input = pd.DataFrame({
            'A': [1, 2, 3],
            'delivery_method': [1, 2, 2],
            'cancellation_code': [pd.NA, pd.NA, 1000]
        })

        df_output = obter_pedidos_balcao(df_input)

        self.assertTrue(any(df_output['delivery_method'] == 1))
        self.assertEqual(df_output.shape[0], 1)
        self.assertEqual(df_output['A'].values, [1])

    def test_obter_pedidos_delivery(self):

        df_input = pd.DataFrame({
            'A': [1, 2, 3],
            'delivery_method': [1, 2, 2],
            'cancellation_code': [pd.NA, pd.NA, 1000]
        })

        df_output = obter_pedidos_delivery(df_input)

        self.assertTrue(any(df_output['delivery_method'] == 2))
        self.assertEqual(df_output.shape[0], 1)
        self.assertEqual(df_output['A'].values, [2])

    def test_obter_pedidos_mesa(self):

        df_input = pd.DataFrame({
            'A':                    [1,     2,     3,    10,    11],
            'delivery_method':      [1,     2,     3,    3,     3],
            'cancellation_code':    [pd.NA, pd.NA, 1000, pd.NA, pd.NA]
        })

        df_output = obter_pedidos_mesa(df_input)

        self.assertTrue(any(df_output['delivery_method'] == 3))
        self.assertEqual(df_output.shape[0], 2)
        self.assertTrue(np.array_equal(df_output['A'].values, [10, 11]))

    def test_obter_resumo(self):
        pedidos_df = pd.read_csv(
            './data_raw/2023/consolidado-pedidos-instadelivery-2023.csv')
        _pedidos_validos_df = pedidos_df[pedidos_df.cancellation_code.isna()]
        df = obter_resumo(_pedidos_validos_df)

        assert all(df['vlr_total'] == (df['vlr_total_balcao'] +
                   df['vlr_total_delivery'] + df['vlr_total_mesa']))


if __name__ == '__main__':
    unittest.main()
