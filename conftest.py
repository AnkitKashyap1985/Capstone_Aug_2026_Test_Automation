import pandas as pd
from sqlalchemy import create_engine, text
import logging
import pytest
from test_configuration.etl_config import *

logging.basicConfig(
    filename='test_log/etlprocess.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture()
def connect_mysql_database():
    logger.info("Connecting to MySQL database...")
    mysql_conn = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    logger.info("Connected to MySQL database...")
    yield mysql_conn
    #mysql_conn.close()
    logger.info("MySQL database has been terminated...")


@pytest.fixture()
def connect_oracle_database():
    logger.info("Connecting to Oracle database...")
    oracle_conn = create_engine(f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}")
    logger.info("Connected to Oracle database...")
    yield oracle_conn
    #oracle_conn.close()
    logger.info("Oracle database has been terminated...")