import azure.functions as func
import datetime
import json
import logging
import os
import tempfile
import textwrap
from typing import List, Dict, Any
import pandas as pd
from io import BytesIO
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient

app = func.FunctionApp()

def download_csv_files_from_blob(connection_string: str, container_name: str) -> Dict[str, pd.DataFrame]:
    """
    Download all CSV files from the 'csvfiles' directory in the specified blob container.
    This is equivalent to: all_files = glob.glob(os.path.join(path, "*.csv")) in the original code,
    but instead of the local file system, we're reading from Azure Blob Storage.
    
    Args:
        connection_string: The connection string for the Azure Storage account.
        container_name: The name of the blob container.
        
    Returns:
        A dictionary mapping filenames to pandas DataFrames.
    """
    logging.info(f"Connecting to blob container {container_name}")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    # List all blobs in the 'csvfiles' directory - this is equivalent to 
    # glob.glob(os.path.join(path, "*.csv")) in the original code
    csv_files = {}
    all_files_found = []
    
    for blob in container_client.list_blobs(name_starts_with="csvfiles/"):
        if blob.name.endswith('.csv'):
            all_files_found.append(blob.name)
            logging.info(f"Found CSV file: {blob.name}")
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall()
            
            # Parse the CSV data - equivalent to df = pd.read_csv(f) in original code
            df = pd.read_csv(BytesIO(blob_data))
            # We use the basename to match the original code's behavior with local files
            csv_files[os.path.basename(blob.name)] = df
    
    logging.info(f"Total CSV files found in csvfiles directory: {len(all_files_found)}")
    return csv_files

def create_excel_from_csv_files(csv_files: Dict[str, pd.DataFrame], excel_filename: str) -> bytes:
    """
    Create an Excel file with multiple sheets from the provided CSV DataFrames,
    following the exact logic from the original csvToExcel function.
    
    Args:
        csv_files: A dictionary mapping filenames to pandas DataFrames.
        excel_filename: The name to give to the Excel file.
        
    Returns:
        The Excel file as bytes.
    """
    logging.info(f"Creating Excel file with {len(csv_files)} sheets")
    xls_name = str(excel_filename)  # Just like in original code
    
    # Create a BytesIO object to store the Excel file
    excel_buffer = BytesIO()
    
    # Create Excel file with each CSV as a separate sheet
    # Using xlsxwriter as the engine to match the original code
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        logging.info('These files have a character length greater than 33:')
        
        for filename, df in csv_files.items():
            # Use the CSV filename (without extension) as the sheet name
            sheet_name = os.path.splitext(filename)[0]
            
            # Check if the sheet name is within Excel's 31 character limit (exactly like original)
            if len(sheet_name) <= 31:  # Using 31 not 33 because Excel's limit is 31
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Log the filenames with long names
                logging.info(sheet_name)  # Same as print() in original
                logging.info('---------------------------------------------')
                
                # Exactly the same logic as original code
                others = sheet_name
                others = textwrap.shorten(others, width=30, placeholder='')
                df.to_excel(writer, sheet_name=others)
                
                logging.info(others)  # Same as print(others) in original
        
        logging.info('These tabs are now named above:  \n \n')
        logging.info('Job Complete!')
    
    # Get the bytes of the Excel file
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def upload_excel_to_blob(excel_data: bytes, connection_string: str, container_name: str, excel_filename: str) -> str:
    """
    Upload the Excel file to the specified blob container.
    
    Args:
        excel_data: The Excel file as bytes.
        connection_string: The connection string for the Azure Storage account.
        container_name: The name of the blob container.
        excel_filename: The name to give to the Excel file.
        
    Returns:
        The URL of the uploaded Excel file.
    """
    logging.info(f"Uploading Excel file {excel_filename} to blob container {container_name}")
    
    # Ensure the filename has .xlsx extension
    if not excel_filename.endswith('.xlsx'):
        excel_filename += '.xlsx'
    
    # Upload the Excel file to blob storage
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    # Upload to the root of the container
    blob_client = container_client.get_blob_client(excel_filename)
    blob_client.upload_blob(excel_data, overwrite=True)
    
    # Generate a URL with SAS token for the blob
    return blob_client.url

@app.route(route="ConvertCsvToExcel", auth_level=func.AuthLevel.FUNCTION)
def ConvertCsvToExcel(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Parse request body
        req_body = req.get_json()
        excel_filename = req_body.get('excel_filename')
        container_name = req_body.get('container_name')
        connection_string = req_body.get('connection_string')
        
        # Validate required parameters
        if not excel_filename or not container_name or not connection_string:
            return func.HttpResponse(
                "Please provide excel_filename, container_name, and connection_string in the request body.",
                status_code=400
            )
            
        logging.info(f"Starting CSV to Excel conversion for: {excel_filename}")
        
        # Download all CSV files from the blob container's csvfiles directory
        # This is equivalent to glob.glob(os.path.join(path, "*.csv")) in the original code
        csv_files = download_csv_files_from_blob(connection_string, container_name)
        
        if not csv_files:
            return func.HttpResponse(
                "No CSV files found in the csvfiles directory of the specified blob container.",
                status_code=404
            )
        
        logging.info(f"Found {len(csv_files)} CSV files to process")
            
        # Create an Excel file from the CSV files
        # This is equivalent to the csvToExcel function in the original code
        excel_data = create_excel_from_csv_files(csv_files, excel_filename)
        
        # Upload the Excel file to blob storage
        # This is a new step not in the original code since we're working with Azure Blob Storage
        excel_url = upload_excel_to_blob(excel_data, connection_string, container_name, excel_filename)
        
        # Return the URL to the Excel file
        return func.HttpResponse(
            json.dumps({
                "status": "success", 
                "message": "Job Complete!",
                "excel_url": excel_url,
                "file_count": len(csv_files)
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )