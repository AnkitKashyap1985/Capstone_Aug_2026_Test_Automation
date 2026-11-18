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

class TestDataTransformation:
    validation_utility = ValidationUtility()
    base_utility = BaseUtility()

    @pytest.mark.data_transformation
    def test_data_transformation_for_filter_sales_data(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Transformation Test {test_case_name}...")
        try:
            query_expected = """select sales_id,product_id,store_id,quantity,price,sale_date,region from stag_sales where sale_date>='2026-09-10'"""
            query_actual = """select sales_id,product_id,store_id,quantity,price,sale_date,region from filtered_sales"""
            self.validation_utility.execute_validation(validation_type = "DB_TO_DB",
                                                       test_case_name = test_case_name,
                                                       query_expected = query_expected,
                                                       dbconn_expected = connect_mysql_database,
                                                       query_actual = query_actual,
                                                       dbconn_actual = connect_mysql_database)

            logger.info(f"Successfully completed Data Transformation Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    @pytest.mark.data_transformation
    def test_data_transformation_for_router_high_sales_data(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Transformation Test {test_case_name}...")
        try:
            query_expected = """select sales_id,product_id,store_id,quantity,price,sale_date,region from stag_sales where region='High'"""
            query_actual = """select sales_id,product_id,store_id,quantity,price,sale_date,region from high_sales"""
            self.validation_utility.execute_validation(validation_type="DB_TO_DB",
                                                       test_case_name=test_case_name,
                                                       query_expected=query_expected,
                                                       dbconn_expected=connect_mysql_database,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)
            logger.info(f"Successfully completed Data Transformation Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    @pytest.mark.data_transformation
    def test_data_transformation_for_router_low_sales_data(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Transformation Test {test_case_name}...")
        try:
            query_expected = """select sales_id,product_id,store_id,quantity,price,sale_date,region from stag_sales where region='Low'"""
            query_actual = """select sales_id,product_id,store_id,quantity,price,sale_date,region from low_sales"""
            self.validation_utility.execute_validation(validation_type="DB_TO_DB",
                                                       test_case_name=test_case_name,
                                                       query_expected=query_expected,
                                                       dbconn_expected=connect_mysql_database,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)

            logger.info(f"Successfully completed Data Transformation Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    @pytest.mark.data_transformation
    def test_data_transformation_for_aggregator_sales(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Transformation Test {test_case_name}...")
        try:
            query_expected = """select product_id,year(sale_date)as year,month(sale_date)as month,sum(quantity*price)as total_sales 
                                from filtered_sales group by product_id,year(sale_date),month(sale_date)"""
            query_actual = """select product_id, year, month, total_sales from monthly_sales_summary_source"""
            self.validation_utility.execute_validation(validation_type="DB_TO_DB",
                                                       test_case_name=test_case_name,
                                                       query_expected=query_expected,
                                                       dbconn_expected=connect_mysql_database,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)

            logger.info(f"Successfully completed Data Transformation Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    @pytest.mark.data_transformation
    def test_data_transformation_for_joiner(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Transformation Test {test_case_name}...")
        try:
            query_expected = """select fs.sales_id,fs.quantity,fs.price,fs.quantity*fs.price as sales_amount,
            fs.sale_date,p.product_id,p.product_name,s.store_id,s.store_name from filtered_sales as fs 
            inner join stag_product as p on fs.product_id = p.product_id inner join stag_stores as s on fs.store_id = s.store_id"""
            query_actual = """Select sales_id,quantity,price,sales_amount,sale_date,product_id,product_name,store_id,store_name from sales_with_details"""
            self.validation_utility.execute_validation(validation_type="DB_TO_DB",
                                                       test_case_name=test_case_name,
                                                       query_expected=query_expected,
                                                       dbconn_expected=connect_mysql_database,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)

            logger.info(f"Successfully completed Data Transformation Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    @pytest.mark.data_transformation
    def test_data_transformation_aggregator_inventory(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Transformation Test {test_case_name}...")
        try:
            query_expected = """select store_id, sum(quantity_on_hand) as total_inventory from stag_inventory group by store_id"""
            query_actual = """select store_id, total_inventory from aggregated_inventory_level"""
            self.validation_utility.execute_validation(validation_type="DB_TO_DB",
                                                       test_case_name=test_case_name,
                                                       query_expected=query_expected,
                                                       dbconn_expected=connect_mysql_database,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)

            logger.info(f"Successfully completed Data Transformation Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()