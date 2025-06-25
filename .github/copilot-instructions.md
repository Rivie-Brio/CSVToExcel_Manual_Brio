<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# CSVToExcel_Manual_Brio Function App

This is an Azure Functions app written in Python that converts CSV files from a blob container into a single Excel file with multiple sheets.

## Key Components:

- HTTP-triggered Azure Function that processes requests manually
- Blob storage operations for retrieving CSV files and storing Excel output
- Pandas for data processing and Excel file creation
- Secure handling of connection strings and container information

## Function Flow:

1. Receive HTTP request with Excel filename, container name, and connection string
2. Download all CSV files from the "csvfiles" directory in the specified blob container
3. Process each CSV file into a DataFrame
4. Create an Excel file with each CSV as a separate sheet
5. Upload the Excel file to the root of the blob container
6. Return the URL to the uploaded Excel file

## Best Practices:

- Follow Azure Functions best practices for efficient execution
- Implement proper error handling and logging
- Use secure methods for handling connection strings
- Follow Pandas best practices for efficient data processing
- Implement retries for Azure Storage operations when appropriate
