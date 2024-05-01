import unittest
import pandas as pd
from pandas import testing as tm
import numpy as np

from aplicativos.util import *


class TestInstadeliveryUtil(unittest.TestCase):
    def test_serie_dia_da_semana_com_lista_vazia(self):
        s_output = serie_dia_da_semana('minha-serie', [])
        assert s_output.name == 'minha-serie'

    def test_serie_dia_da_semana_com_lista_valida_formato_padrao(self):
        s_output = serie_dia_da_semana(
            'minha-serie', ['01/01/2024', '02/01/2024', '04/01/2024', '05/01/2024'])

        assert s_output.name == 'minha-serie'

        s_esperado = pd.Series(
            data=['segunda', 'terça', 'quinta', 'sexta'],
            index=['01/01/2024', '02/01/2024', '04/01/2024', '05/01/2024'],
            name='minha-serie')

        tm.assert_series_equal(s_output, s_esperado)

    def test_taxa_retencao(self):
        ''''Para cada dia presente no indice de TotalClientes
        calcula-se a taxa de retenção das séries
        TotalClientes e de NovosClientes.

        TotalCliente tem a quantidade de visitas por dia
        NovosClientes tem a quantidade de novos visitantes por dia (primeira visita)

        Não necessariamente o indice precisa ser data, pois a função observa apenas
        os indices comuns nas duas séries.
        '''
        _indice_comum = ['01/01/2024', '02/01/2024',
                         '04/01/2024', '05/01/2024']
        serieTotalClientes = pd.Series(
            index=_indice_comum + ['06/01/2024'],
            data=[10, 10, 2, 2, 10]
        )

        serieNovosClientes = pd.Series(
            index=_indice_comum,
            data=[5, 3, 2, 2]
        )

        s_esperado = pd.Series(
            index=_indice_comum + ['06/01/2024'],
            data=[50, 70, 0, 0, 100]
        )
        s_output = taxa_retencao(serieTotalClientes, serieNovosClientes)

        tm.assert_series_equal(s_output, s_esperado, check_dtype=False)

    def test_calcular_total(self):
        df = pd.DataFrame(
            data={
                'date': ['01/01/2024', '01/01/2024', '02/02/2024', '02/02/2024'],
                'valor': [3, 4, 1, 2]}
        )

        df_output = agrupar_soma(df, 'date', 'valor')

        df_esperado = pd.Series(
            index=['01/01/2024', '02/02/2024'],
            data=[7, 3]
        )

        tm.assert_series_equal(df_output, df_esperado,
                               check_names=False, check_dtype=False)


if __name__ == '__main__':
    unittest.main()
