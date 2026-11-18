import inspect
import pandas as pd
from sqlalchemy import create_engine, text
import logging
import pytest
from test_configuration.etl_config import *
from common_utilities.utilities import *

logging.basicConfig(
    filename='application_log/etlprocess.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSchemaValidation:
    validation_utility = ValidationUtility()
    schema_validation = SchemaValidationUtility()

    @pytest.mark.schema_validation
    def test_schema_validation_for_fact_sales_table_column_names_check(self,connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Schema Validation Test {test_case_name}...")
        try:
            expected_column_names = ['sales_id','product_id','store_id','quantity','total_sales','sale_date']
            self.schema_validation.validate_column_names(
                db_conn=connect_mysql_database,
                table_name='fact_sales',
                expected_column_names=expected_column_names
            )
            logger.info(f"Successfully completed Schema Validation Test:\n {test_case_name}...")
        except Exception as e:
            logger.error(f"TestCase Failed \n{test_case_name}: {e}")
            pytest.fail()

    @pytest.mark.schema_validation
    def test_schema_validation_for_fact_inventory_table_column_names_check(self, connect_mysql_database):
        pass

    @pytest.mark.schema_validation
    def test_schema_validation_for_monthly_sales_summary_table_column_names_check(self, connect_mysql_database):
        pass

    @pytest.mark.schema_validation
    def test_schema_validation_for_inventory_level_by_stores_table_column_names_check(self, connect_mysql_database):
        pass

    @pytest.mark.schema_validation
    def test_schema_validation_for_fact_sales_table_data_type_check(self,connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting DataType Validation Test {test_case_name}...")
        try:
            expected_datatypes_dict = {'sales_id':["int64"],
                                      'product_id':["int64"],
                                      'store_id':["int64"],
                                      'quantity':["int64"],
                                      'total_sales':["int64",'float64'],
                                      'sale_date':["object"],
                                       }
            self.schema_validation.validate_column_datatypes(
                db_conn=connect_mysql_database,
                table_name='fact_sales',
                expected_datatypes_dict=expected_datatypes_dict
            )
            logger.info(f"Successfully completed Schema Validation Test \n{test_case_name}...")
        except Exception as e:
            logger.error(f"TestCase Failed \n{test_case_name}: {e}")
            pytest.fail()

    @pytest.mark.skip
    def test_schema_validation_for_fact_inventory_table_column_data_type_check(self, connect_mysql_database):
        pass

    @pytest.mark.skip
    def test_schema_validation_for_monthly_sales_summary_table_column_data_type_check(self, connect_mysql_database):
        pass

    @pytest.mark.skip
    def test_schema_validation_for_inventory_level_by_stores_table_column_data_type_check(self, connect_mysql_database):
        pass


    @pytest.mark.schema_validation
    def test_data_quality_referential_integrity_check_for_product_id_column_between_foreign_fact_sales_and_primary_table_stag_product (self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Schema Validation Test {test_case_name}...")

            #primary_db_conn,foreign_db_conn,primary_query,foreign_query,key_column_name,csv_path
        try:
            foreign_query = """select * from fact_sales"""
            primary_query = """select * from stag_product"""

            df_not_matched = self.schema_validation.validate_referential_integrity_check(
                primary_db_conn=connect_mysql_database,
                foreign_db_conn=connect_mysql_database,
                primary_query=primary_query,
                foreign_query=foreign_query,
                key_column_name='product_id',
                csv_path="differences/foreign_key_not_matched.csv"
            )
            assert df_not_matched.empty is True, "Foreign key validation failed."

            logger.info(f"Successfully completed Schema Validation Test {test_case_name}...")
        except Exception as e:
            logger.error(f"TestCase Failed {test_case_name}: {e}")
            pytest.fail()