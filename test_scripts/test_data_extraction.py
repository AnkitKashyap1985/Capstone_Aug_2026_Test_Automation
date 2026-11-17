import inspect
from common_utilities.utilities import *

logging.basicConfig(
    filename='application_log/etlprocess.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDataExtraction:
    validation_utility = ValidationUtility()
    base_utility = BaseUtility()

    #@pytest.mark.skip
    def test_data_extraction_supplier_file_stag(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Extraction Test {test_case_name}...")
        try:
            query_actual = """select * from stag_supplier"""
            self.validation_utility.execute_validation(validation_type="FILE_TO_DB", test_case_name=test_case_name,
                                                       file_path="test_data/supplier_data.json",
                                                       file_type="json",
                                                       query_actual=query_actual, dbconn_actual=connect_mysql_database)
            logger.info(f"Successfully completed Data Extraction Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    #@pytest.mark.skip
    def test_data_extraction_inventory_file_stag(self,connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Extraction Test {test_case_name}...")
        try:
            query_actual = """select * from stag_inventory"""
            self.validation_utility.execute_validation(validation_type="FILE_TO_DB",test_case_name=test_case_name,
                                                       file_path="test_data/inventory_data.xml",
                                                       file_type="xml",query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)
            logger.info(f"Successfully completed Data Extraction Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    #@pytest.mark.skip
    def test_data_extraction_product_file_stag(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Extraction Test {test_case_name}...")
        self.base_utility.linux_utility_download_file_from_Linux_server()

        try:
            query_actual = """select * from stag_product"""
            self.validation_utility.execute_validation(validation_type="FILE_TO_DB",
                                                       test_case_name=test_case_name,
                                                       file_path=LOCAL_FILE_PATH,
                                                       file_type="csv",
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)
            logger.info(f"Successfully completed Data Extraction Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    def test_data_extraction_sales_file_stage(self, connect_mysql_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Extraction Test {test_case_name}...")

        try:
            query_actual = """select * from stag_sales"""
            self.validation_utility.execute_validation(validation_type="S3_TO_DB",
                                                       test_case_name=test_case_name,
                                                       bucket_name = BUCKET_NAME,
                                                       file_key=FILE_KEY,
                                                       query_actual=query_actual,
                                                       dbconn_actual=connect_mysql_database)
            logger.info(f"Successfully completed Data Extraction Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()

    #@pytest.mark.skip
    def test_data_extraction_stores_db_stag(self, connect_mysql_database,connect_oracle_database):
        test_case_name = inspect.currentframe().f_code.co_name
        logger.info(f"Starting Data Extraction Test {test_case_name}...")

        try:
            query_expected = """select store_id as "store_id",store_name as "store_name" from stores order by store_id"""
            query_actual = """select store_id, store_name from stag_stores order by store_id;"""
            self.validation_utility.execute_validation(
                validation_type="DB_TO_DB",
                test_case_name=test_case_name,
                query_expected=query_expected,
                dbconn_expected=connect_oracle_database,
                query_actual=query_actual,
                dbconn_actual=connect_mysql_database
            )
            logger.info(f"Successfully completed Data Extraction Test {test_case_name}...")

        except Exception as e:
            logger.error(f"TestCase Failed: {e}")
            pytest.fail()