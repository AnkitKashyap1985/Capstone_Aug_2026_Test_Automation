import pandas as pd
from sqlalchemy import create_engine, text
import logging
import pytest
from test_configuration.etl_config import *
import os
import boto3
import paramiko
from io import StringIO


logging.basicConfig(
    filename='application_log/etlprocess.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

oracle_conn = create_engine(f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}")

mysql_conn = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

class BaseUtility:
    # Encapsulation
    def __read_file(self,file_path,file_type):
        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type == "json":
            df = pd.read_json(file_path)
        elif file_type == "xml":
            df = pd.read_xml(file_path,xpath=".//item")
        else:
            raise ValueError(f"Unsupported file type {file_type}")
        return df
    # Abstraction
    def read_file(self,file_path,file_type):
        return self.__read_file(file_path,file_type)

    def read_file_from_s3(self,bucket_name, file_key):
        try:
            logger.info(f"Reading file from S3 Bucket {bucket_name}")
            s3 = boto3.client('s3')
            response = s3.get_object(Bucket=bucket_name,Key=file_key)
            csv_content = response["Body"].read().decode("utf-8")
            data = StringIO(csv_content)
            df = pd.read_csv(data)
            logger.info(f"S3 data is {df}")
            return df

        except Exception as e:
            logger.error(f"S3 file read failed{e}")

    def linux_utility_download_file_from_Linux_server(self):
        try:
            logger.info(f"Downloading file from Linux Server")
            logger.info("File download from Linux Server has started...")
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(LINUX_HOSTNAME, username=LINUX_USERNAME, password=LINUX_PASSWORD)
            sftp = ssh_client.open_sftp()
            sftp.get(REMOTE_FILE_PATH, LOCAL_FILE_PATH)
            sftp.close()
            logger.info('File download from Linux Server has completed...')
        except Exception as e:
            logger.error(f"Linux file download failed{e}")



#Inheritance
class ValidationUtility(BaseUtility):

    def execute_validation(self,validation_type,test_case_name,file_path=None,file_type=None,query_actual=None,dbconn_actual=None,query_expected=None,dbconn_expected=None,bucket_name=None,file_key=None):

            if validation_type == "FILE_TO_DB":
                self.file_to_db(test_case_name, file_path, file_type, query_actual, dbconn_actual)
            elif validation_type == "DB_TO_DB":
                self.db_to_db(test_case_name,query_expected,dbconn_expected,query_actual,dbconn_actual)
            elif validation_type == "S3_TO_DB":
                self.s3_to_db(test_case_name,bucket_name,file_key,query_actual,dbconn_actual)

    def file_to_db(self,test_case_name,file_path,file_type,query_actual,dbconn_actual):
        try:
            df_expected = self.read_file(file_path,file_type)
            logger.info(f"Expected Data :{df_expected}")
            df_actual = pd.read_sql(query_actual, dbconn_actual)
            logger.info(f"Actual Data :{df_actual}")

            # Expected Minus Actual
            df_extra_expected = df_expected[~df_expected.apply(tuple,axis=1).isin(df_actual.apply(tuple,axis=1))]

            # Actual Minus Expected
            df_extra_actual = df_actual[~df_actual.apply(tuple,axis=1).isin(df_expected.apply(tuple,axis=1))]

            if not df_extra_expected.empty or not df_extra_actual.empty :
                os.makedirs("Differences",exist_ok=True)

                if not df_extra_expected.empty:
                    df_extra_expected.to_csv(f"Differences_{test_case_name}.csv",index=False)

                if not df_extra_actual.empty:
                    df_extra_actual.to_csv(f"Differences_{test_case_name}.csv",index=False)

            # Assertion
            assert df_actual.equals(df_expected), f"{test_case_name} Failed"
            logger.info(f"{test_case_name} Passed")

        except Exception as e:
            logger.error(f"{test_case_name} Validation Failed {e}")
            pytest.fail()

    def db_to_db(self, test_case_name, query_expected, dbconn_expected, query_actual, dbconn_actual):
        try:
            df_expected = pd.read_sql(query_expected, dbconn_expected)
            logger.info(f"Expected Data:\n{df_expected}")
            df_actual = pd.read_sql(query_actual, dbconn_actual)
            logger.info(f"Actual Data :\n{df_actual}")
            logger.info(f"Expected Dtypes:\n{df_expected.dtypes}")
            logger.info(f"Actual Dtypes:\n{df_actual.dtypes}")

            # Expected Minus Actual
            df_extra_expected = df_expected[~df_expected.apply(tuple,axis=1).isin(df_actual.apply(tuple,axis=1))]

            # Actual Minus Expected
            df_extra_actual = df_actual[~df_actual.apply(tuple,axis=1).isin(df_expected.apply(tuple,axis=1))]

            if not df_extra_expected.empty or not df_extra_actual.empty :
                os.makedirs("Differences",exist_ok=True)

                if not df_extra_expected.empty:
                    df_extra_expected.to_csv(f"Differences_{test_case_name}.csv",index=False)

                if not df_extra_actual.empty:
                    df_extra_actual.to_csv(f"Differences_{test_case_name}.csv",index=False)

            # Assertion
            assert df_actual.equals(df_expected), f"{test_case_name} Failed"
            logger.info(f"{test_case_name} Passed")

        except Exception as e:
            logger.error(f"{test_case_name} Validation Failed {e}")
            pytest.fail()


    def s3_to_db(self,test_case_name,bucket_name,file_key,query_actual,dbconn_actual):
        try:
            df_expected = self.read_file_from_s3(bucket_name,file_key)
            logger.info(f"Expected Data :{df_expected}")
            df_actual = pd.read_sql(query_actual, dbconn_actual)
            logger.info(f"Actual Data :{df_actual}")

            # Expected Minus Actual
            df_extra_expected = df_expected[~df_expected.apply(tuple,axis=1).isin(df_actual.apply(tuple,axis=1))]

            # Actual Minus Expected
            df_extra_actual = df_actual[~df_actual.apply(tuple,axis=1).isin(df_expected.apply(tuple,axis=1))]

            if not df_extra_expected.empty or not df_extra_actual.empty :
                os.makedirs("Differences",exist_ok=True)

                if not df_extra_expected.empty:
                    df_extra_expected.to_csv(f"Differences_{test_case_name}.csv",index=False)

                if not df_extra_actual.empty:
                    df_extra_actual.to_csv(f"Differences_{test_case_name}.csv",index=False)

            # Assertion
            assert df_actual.equals(df_expected), f"{test_case_name} Failed"
            logger.info(f"{test_case_name} Passed")

        except Exception as e:
            logger.error(f"{test_case_name} Validation Failed {e}")
            pytest.fail()



class FileUtility(BaseUtility):
    def check_file_exists(self, file_path):
        try:
            return os.path.isfile(file_path)
        except Exception as e:
            logger.error(f"File existence check failed {e}")

    def check_file_size(self, file_path):
        try:
            return os.path.getsize(file_path)>0
        except Exception as e:
            logger.error(f"File size check failed {e}")



# Data Quality Functions

class DataQuality(BaseUtility):
    # Duplicate Checks
    def check_duplicate_in_file(self,file_path,file_type):
        try:
            df = self.read_file(file_path,file_type)
            if df.duplicated().any():
                return False
            return True
        except Exception as e:
            logger.error(f"Duplicate check in file failed {e}")
            raise

    def check_duplicate_in_database(self,query,db_conn):
        try:
            df = pd.read_sql(query,db_conn)
            if df.duplicated().any():
                return False
            return True
        except Exception as e:
            logger.error(f"Duplicate check in DataBase failed {e}")
            raise

    def check_duplicate_for_specific_column_in_file(self,file_path,file_type,column_name):
        try:
            df = self.read_file(file_path,file_type)
            if df [column_name].duplicated().any():
                return False
            return True
        except Exception as e:
            logger.error(f"Duplicate check for column i file {column_name} failed {e}")
            raise

    def check_duplicate_for_specific_column_in_database(self,query,db_conn,column_name):
        try:
            df = pd.read_sql(query,db_conn)
            if df[column_name].duplicated().any():
                return False
            return True
        except Exception as e:
            logger.error(f"Duplicate check for column {column_name} failed {e}")
            raise

    # Null Check Functions

    def check_null_value_in_file(self,file_path,file_type):
        try:
            df = self.read_file(file_path,file_type)
            if df.isnull().values.any():
                return False
            return True
        except Exception as e:
            logger.error(f"Null value check failed {e}")
            raise

    def check_null_value_for_a_specific_column_in_file(self,file_path,file_type,column_name):
        try:
            df = self.read_file(file_path,file_type)
            if df[column_name].isnull().any():
                return False
            return True
        except Exception as e:
            logger.error(f"Null value check failed {e}")
            raise

    def check_null_value_in_database(self,query,db_conn):
        try:
            df = pd.read_sql(query,db_conn)
            if df.isnull().values.any():
                return False
            return True
        except Exception as e:
            logger.error(f"Null value check failed {e}")
            raise

    def check_null_value_for_a_specific_column_in_database(self,query,db_conn,column_name):
        try:
            df = pd.read_sql(query, db_conn)
            if df[column_name].isnull().any():
                return False
            return True
        except Exception as e:
            logger.error(f"Null value check failed {e}")
            raise



class SchemaValidationUtility(BaseUtility):
    def validate_column_names(self,db_conn,table_name,expected_column_names):
        query = f"select * from {table_name}"
        df = pd.read_sql(query,db_conn)
        actual_column_names = list(df.columns)
        assert actual_column_names == expected_column_names,(
            f"\n Column mismatch in table {table_name}"
            f"\n expected_columns: {expected_column_names}"
            f"\n actual column names: {actual_column_names}"
        )
    def validate_column_datatypes(self,db_conn,table_name,expected_datatypes_dict):
        query = f"select * from {table_name}"
        df = pd.read_sql(query,db_conn)
        for column_name,expected_datatype in expected_datatypes_dict.items():
            actual_data_type = df[column_name].dtype
            assert actual_data_type in expected_datatype, (
                f"\n Datatype mismatch in table {table_name}"
                f"\n for mismatch in column: {column_name}"
                f"\n Expected Datatype: {expected_datatype}"
                f"\n Actual Datatype: {actual_datatype}"
            )

    def validate_referential_integrity_check(self,primary_db_conn,foreign_db_conn,primary_query,foreign_query,key_column_name,csv_path):
        foreign_df = pd.read_sql(foreign_query,foreign_db_conn)
        primary_df = pd.read_sql(primary_query,primary_db_conn)
        df_not_matched = foreign_df[~foreign_df[key_column_name].isin(primary_df[key_column_name])]
        if not df_not_matched.empty:
            df_not_matched.to_csv(csv_path,index=False)
        return df_not_matched









