# CSVToExcel Manual Function App

This Azure Function app provides a manual HTTP-triggered endpoint that converts CSV files from a blob container into a single Excel file. The Excel file is then uploaded back to the blob container, and a URL is returned to the caller.

## Features

- HTTP-triggered Azure Function that can be called manually
- Converts multiple CSV files into a single Excel file with multiple sheets
- Works with Azure Blob Storage for file operations
- Returns a direct URL to the generated Excel file

## Prerequisites

- Python 3.10 or later
- Azure Functions Core Tools v4
- Azure Storage Account with a blob container

## Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start the function app locally:
   ```
   func start
   ```

## Configuration

No environment variables need to be set as all required information is passed as part of the request.

## Usage

Make a POST request to the ConvertCsvToExcel endpoint with the following JSON payload:

```json
{
  "excel_filename": "YourExcelFilename",
  "container_name": "your-container-name",
  "connection_string": "your-storage-account-connection-string"
}
```

### Parameters

- `excel_filename`: The name of the Excel file to create (without extension)
- `container_name`: The name of the blob container that contains the CSV files
- `connection_string`: The connection string for the Azure Storage account

### Response

A successful response will return a JSON object with the URL to the generated Excel file:

```json
{
  "status": "success",
  "excel_url": "https://yourstorageaccount.blob.core.windows.net/your-container/YourExcelFilename.xlsx"
}
```

## CSV File Structure

The function expects CSV files to be stored in a directory named `csvfiles` within the specified blob container. Each CSV file will be converted to a separate sheet in the Excel file, with the sheet name derived from the CSV filename (without extension).

## Error Handling

The function returns appropriate HTTP status codes for different error conditions:
- 400: Missing required parameters
- 404: No CSV files found in the container
- 500: Internal server error (with error message)

## Deployment

Deploy to Azure using the Azure Functions extension for VS Code or the Azure Functions Core Tools.
