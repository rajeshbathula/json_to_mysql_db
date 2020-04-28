import os,unittest
from main.json_format_push_to_mysql import *
from pandas.util.testing import assert_frame_equal

import pandas as pd

class TestMysql(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        THIS_DIR = os.path.dirname(os.path.abspath(__file__))
        raw_file = os.path.join(THIS_DIR, './resources/raw_input.json')
        cls.raw_df = pd.read_json(raw_file, lines=True)
        output_explode = os.path.join(THIS_DIR, './resources/output_explode.csv')
        cls.output_explode_df = pd.read_csv(output_explode)
        agrt = os.path.join(THIS_DIR, './resources/final_agrt.csv')
        cls.final_agrt_df = pd.read_csv(agrt)

    def test_explode_event_params_and_filter(self):
        user_eng_df = user_engagement_df(self.raw_df)
        result      = explode_event_params_and_filter(user_eng_df)
        expected    = self.output_explode_df
        result = result['engagement_time_msec'].iloc[0]
        expected = expected['engagement_time_msec'].iloc[0]
        self.assertEqual(result,expected)

    def test_join_groupby_df(self):
        user_eng_df = user_engagement_df(self.raw_df)
        x = explode_event_params_and_filter(user_eng_df)
        result      = join_groupby_df(user_eng_df,x)
        expected    = self.final_agrt_df
        assert_frame_equal(result.reset_index(drop=True),expected.reset_index(drop=True))

if __name__ == '__main__':
    unittest.main()