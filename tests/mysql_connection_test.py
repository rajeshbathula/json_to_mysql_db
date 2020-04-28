import os,unittest
from main.json_format_push_to_mysql import *
import pandas as pd

class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        agrt = os.path.join(THIS_DIR, './resources/final_agrt.csv')
        cls.final_agrt_df = pd.read_csv(agrt)
        cls.db = 'test_db'

    def test_mysql_connection(self):
        result = connect_mysql(self.db)
        self.assertNotEqual(result,None,"mysql not configured or not up!")

    def test_connect_mysql_table_exist(self):
        engine = connect_mysql(self.db)
        result = engine.dialect.has_table(engine, 'active_user_table')
        self.assertTrue(result,"No table exist!")

    def test_to_mysql_db(self):
        result = to_mysql_db(self.final_agrt_df,self.db)
        self.assertTrue(result,"No table exist!")

if __name__ == '__main__':
    unittest.main()