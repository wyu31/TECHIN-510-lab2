import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

try:
    print("Azure Blob Storage v12 Python quickstart sample")

    # Initialize the connection to Azure storage account
    storage_account_name = "seattleevents"
    container_name = "csvdata"
    blob_name = "events_with_weather.csv"
    local_csv_path = "/Users/yomaru/Desktop/TECHIN 510/Labs/TECHIN-510-lab2/events_with_weather.csv"

    # Create a BlobServiceClient using DefaultAzureCredential
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # Upload the CSV file to Blob Storage
    with open(local_csv_path, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    print(f"Uploaded {blob_name} to Azure Blob Storage container '{container_name}'")

except Exception as ex:
    print('Exception:')
    print(ex)