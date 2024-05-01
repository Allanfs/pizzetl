import unittest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

from aplicativos.querodelivery import *


class TestQueroDelivery(unittest.TestCase):

    def test_obter_pedidos_validos(self):
        d = {'status': ['ENTREGUE', 'NAO ENTREGUE',
                        'DIFERENTE'], 'id': [10, 20, 30]}
        df = pd.DataFrame(data=d)

        dfretorno = obter_pedidos_validos(df)

        dfesperado = pd.DataFrame({'status': 'ENTREGUE', 'id': [10]})
        assert_frame_equal(dfretorno, dfesperado)




if __name__ == '__main__':
    unittest.main()
