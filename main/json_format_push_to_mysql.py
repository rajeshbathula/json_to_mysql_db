"""
This  program runs on JSON data filters nad agrt to get the user count by date.
command:

    python3.6 agrt_push_to_sql(input_location)

"""

import pandas as pd
import argparse
import sqlalchemy as db
from tabulate import tabulate
import glob,sys

def read_json_to_df(location: str):
    """
    this function will return pandas dataframe
    :param location: location of input files
    :return: DataFrame
    """
    try:
        src_excel_files = glob.glob("{}/*".format(location))
        if len(src_excel_files) > 0:
            return pd.concat(pd.read_json(f, lines=True) for f in src_excel_files)
        else:
            print('No Json files in input folder, kindly upload and rerun from project folder!')
            sys.exit()
    except Exception as e:
        print("kindly place Json files in input folder and try again!")
        sys.exit()


def user_engagement_df(df):
    """
    this function will return pandas dataframe
    dataframe that needs filtering user_engagement events
    :param df:
    :return: DataFrame
    """
    return df.loc[df['event_name']=='user_engagement']

def explode_event_params_and_filter(df):
    """
    this function will return pandas dataframe,
    dataframe will explode event_params column and retuns all the keys and values in new rows
    :param df:
    :return: DataFrame
    """
    try:
        df = df.explode('event_params')
        df = pd.DataFrame(([k,int(v2)] for k,v in df.pop('event_params').items()
                      if v['key'] == 'engagement_time_msec' and isinstance(v,dict)
                      for k1,v1 in v.items() if isinstance(v1, dict)
                      for k2, v2 in v1.items())
                     ,columns=[0,'engagement_time_msec'])
        return df.loc[df['engagement_time_msec'] >= 3000]
    except Exception as e:
        print(f"failed to normalise on column event_params with key engagement_time_msec with exception {e}")
        raise

def join_groupby_df(user_engagement_df,active_user_filter):
    """
    this function merges joins users that has engagement time more than 3s and
    joins to dataframe and aggrigates to get user count per day
    :param user_engagement_df:
    :param active_user_filter:
    :return:DataFrame
    """
    join_df =  pd.merge(user_engagement_df, active_user_filter, left_index=True, right_on=0)
    return  join_df.groupby(['event_date']).size().reset_index(name='active_user_count')

def filter_agrt_push_rec_mysql(input_location,db):
    """
    this function calls all the function which putputs final result
    joins to dataframe and aggrigates to get user count per day
    :param input_location:
    :return:DataFrame
    """
    df          = read_json_to_df(input_location)
    user_eng_df = user_engagement_df(df)
    df          = explode_event_params_and_filter(user_eng_df)
    df          = join_groupby_df(user_eng_df,df)
    to_mysql_db(df,db)
    query_mysql(db)
    if not db:
        print('ACTIVE USER COUNT BY DATE' , '\n' , df)
    print("Success!")

def to_mysql_db(df,db):
    """
    this function connects to sql and pushes data to mysql
    :param dataframe:
    :return msg:
    """
    if db:
        try:
            engine = connect_mysql(db)
            df.to_sql(name='active_user_count', con=engine, if_exists = 'append', index=False)
            engine.close()
            return True
        except Exception as e:
            print(f"Exception MySQL db {e}")
            print(df)
            sys.exit()

def query_mysql(db):
    """
    this function connects to docker container mysql and queries users table
    :return:Tabular format data
    """
    if db:
        try:

            sql_select_Query = "select * from active_user_count"
            engine = connect_mysql(db)
            result = engine.execute(sql_select_Query)
            print(tabulate(result.fetchall(), headers=['event_date', 'active_user_count'], tablefmt='psql'))
            return True
        except Exception as e:
            print(f"Error connecting MySQL db {e}")

def connect_mysql(database):
    """
    this function connects to docker container mysql
    """
    if database:
        try:

            config = {
                'host': 'localhost',
                'port': 3306,
                'user': 'newuser',
                'password': 'newpassword',
                'database': f'{database}'
            }
            db_user = config.get('user')
            db_pwd = config.get('password')
            db_host = config.get('host')
            db_port = config.get('port')
            db_name = config.get('database')
            connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
            engine = db.create_engine(connection_str)
            return engine.connect()
        except Exception as e:
            print("Error connecting MySQL db", e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DataTest')
    parser.add_argument('--input_location', required=False, default='./input/')
    parser.add_argument('--db', required=False, default=None)
    args = vars(parser.parse_args())
    filter_agrt_push_rec_mysql(args['input_location'],args['db'])
