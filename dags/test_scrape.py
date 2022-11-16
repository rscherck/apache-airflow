import os
import logging

from datetime import datetime

from airflow.models import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python import PythonOperator
from airflow.providers.microsoft.azure.transfers.local_to_wasb import LocalFilesystemToWasbOperator

from common_packages.process import Process

log = logging.getLogger(__name__)

DAG_ID = "upload_local_file_to_wasb"
FILE_NAME = '/opt/airflow/test.txt'

with DAG(
    DAG_ID,
    schedule_interval="@once",
    start_date=datetime(2021, 1, 1),
    catchup=False,
) as dag:
    log.info('*****************************')
    log.info(os.getcwd())
    log.info(os.listdir(os.curdir))
    log.info('*****************************')

    dt = datetime.utcnow()
    dt_string = dt.strftime("%Y.%m.%d_%H.%M")

    def create_file():
        try:
            fp = open(FILE_NAME, 'wt')
            fp.write('hello world')
            fp.write(dt_string)
            fp.close()
        except Exception as e:
            raise AirflowException(e)

    def delete_file():
        try:
            os.remove(FILE_NAME)
        except Exception as e:
            raise AirflowException(e)  

    def do_work():
        Process.get_data()

    task_create_file = PythonOperator(
        task_id='create_file',
        python_callable=create_file
    )

    task_upload_file_to_blob_storage = LocalFilesystemToWasbOperator(task_id="upload_file",
        file_path=FILE_NAME,
        wasb_conn_id='azure_blob',
        container_name='inputdata',
        blob_name=r"test-{}.txt".format(dt_string),
        create_container=True
    )

    task_process = PythonOperator(
        task_id='process',
        python_callable=do_work
    )

    task_delete_file = PythonOperator(
        task_id='delete_file',
        python_callable=delete_file
    )
    
    task_create_file >> task_upload_file_to_blob_storage >> task_process >> task_delete_file