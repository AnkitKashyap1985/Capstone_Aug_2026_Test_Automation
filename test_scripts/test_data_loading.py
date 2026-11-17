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

class TestDataLoading:
    validation_utility = ValidationUtility()
    base_utility = BaseUtility()


    def test_data_loading_for_monthly_sales_summary(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Loading Test {test_case_name}...")
        try:
            query_expected = """select product_id, year, month, total_sales from monthly_sales_summary_source order by product_id"""
            query_actual = """select product_id, year, month, total_sales from monthly_sales_summary order by product_id"""
            self.validation_utility.execute_validation(validation_type = "DB_TO_DB",
                                                       test_case_name = test_case_name,
                                                       query_expected = query_expected,
                                                       dbconn_expected = connect_mysql_database,
                                                       query_actual = query_actual,
                                                       dbconn_actual = connect_mysql_database)

            logger.info(f"Successfully completed Data Loading Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()


    def test_data_loading_for_fact_inventory(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Loading Test {test_case_name}...")
        try:
            query_expected = """select product_id,store_id,quantity_on_hand,last_updated from fact_inventory order by last_updated"""
            query_actual = """select product_id,store_id,quantity_on_hand,CAST(last_updated AS DATE) AS last_updated from stag_inventory order by last_updated"""
            self.validation_utility.execute_validation(validation_type="DB_TO_DB",
                                                       test_case_name=test_case_name,
                                                       query_expected=query_expected,
                                                       dbconn_expected=connect_mysql_database,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)

            logger.info(f"Successfully completed Data Loading Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()


    def test_data_loading_for_fact_sales(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Loading Test {test_case_name}...")
        try:
            query_expected = """select sales_id,product_id,store_id,quantity,Cast(total_sales as double) as total_sales,sale_date from fact_sales order by sales_id"""
            query_actual = """select sales_id,product_id,store_id,quantity,sales_amount AS total_sales,CAST(sale_date AS DATE)AS sale_date from sales_with_details order by sales_id"""
            self.validation_utility.execute_validation(validation_type="DB_TO_DB",
                                                       test_case_name=test_case_name,
                                                       query_expected=query_expected,
                                                       dbconn_expected=connect_mysql_database,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)

            logger.info(f"Successfully completed Data Loading Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    def test_data_loading_for_inventory_level_by_stores(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Loading Test {test_case_name}...")
        try:
            query_expected = """select store_id,Cast(total_inventory as double) as total_inventory from inventory_levels_by_store order by store_id"""
            query_actual = """select store_id,total_inventory from aggregated_inventory_level order by store_id"""
            self.validation_utility.execute_validation(
                validation_type="DB_TO_DB",
                test_case_name=test_case_name,
                query_expected=query_expected,
                dbconn_expected=connect_mysql_database,
                query_actual=query_actual,
                dbconn_actual=connect_mysql_database
            )

            logger.info(f"Successfully completed Data Loading Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()