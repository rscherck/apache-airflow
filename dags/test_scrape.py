import os
import logging
import pandas as pd
import requests

from datetime import datetime
from airflow.models import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python import PythonOperator
from airflow.providers.microsoft.azure.transfers.local_to_wasb import LocalFilesystemToWasbOperator

from common.process import Process

log = logging.getLogger(__name__)

DAG_ID = "upload_local_file_to_wasb"
iso = "ERCOT"
dt = datetime.utcnow()
dt_string = dt.strftime("%Y.%m.%d_%H.%M")

with DAG(
    DAG_ID,
    schedule_interval="@once",
    start_date=datetime(2021, 1, 1),
    catchup=False,
) as dag:
    log.info('*****************************')
    log.info(os.getcwd())
    log.info(os.listdir(os.curdir))
    log.info(dt_string)
    log.info('*****************************')

    FILE_PATH = "/opt/airflow/"
    FILE_NAME = "ERCOT-Interconnection-Queue_{}.xlsx".format(
        dt_string)

    FULL_FILE_PATH = FILE_PATH + FILE_NAME

    def scrape_file():
        try:
            url = r'https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=15933&_=1666627196055'
            page = requests.get(url, allow_redirects=True)
            data = page.json()

            projects = data['ListDocsByRptTypeRes']['DocumentList']

            df = pd.json_normalize(projects)

            gis_df = df.loc[df['Document.FriendlyName'].str.contains(
                "GIS_Report")]

            newest_queue = gis_df.loc[gis_df['Document.PublishDate']
                                      == gis_df['Document.PublishDate'].max()]

            doc_id = newest_queue['Document.DocID'].item()

            download_url = r"https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={}".format(
                doc_id)

            page = requests.get(
                download_url, allow_redirects=True, verify=False)

            output = open(FILE_NAME, 'wb')
            output.write(page.content)
            output.close()

        except Exception as e:
            raise AirflowException(e)

    # def delete_file():
    #     try:
    #         os.remove(FULL_FILE_PATH)
    #     except Exception as e:
    #         raise AirflowException(e)

    def do_work():
        Process.get_data()

    task_upload_file_to_blob_storage = LocalFilesystemToWasbOperator(task_id="upload_file",
                                                                     file_path=FULL_FILE_PATH,
                                                                     wasb_conn_id='azure_blob',
                                                                     container_name='inputdata',
                                                                     blob_name="{}/{}/{}/{}".format(iso, dt.strftime(
                                                                         "%Y"), dt.strftime("%m"), FILE_NAME),
                                                                     create_container=True
                                                                     )

    task_process = PythonOperator(
        task_id='process',
        python_callable=do_work
    )

    # task_delete_file = PythonOperator(
    #     task_id='delete_file',
    #     python_callable=delete_file
    # )

    task_scrape_file = PythonOperator(
        task_id='scrape_file',
        python_callable=scrape_file
    )

    task_scrape_file >> task_upload_file_to_blob_storage >> task_process
