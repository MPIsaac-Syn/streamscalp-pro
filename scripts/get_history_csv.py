import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# Define the stock symbol and time range
symbol = "AAPL"
range_days = 7  # Fetch last 7 days of data
output_file = "historical_data.csv"

# Calculate the start and end dates
end_date = datetime.now()
start_date = end_date - timedelta(days=range_days)

def get_historical_data():
    """Fetch historical data and format it properly for CSV export"""
    print(f"Fetching {symbol} data from {start_date.date()} to {end_date.date()}...")
    
    # Fetch historical data with 1-minute granularity
    data = yf.download(symbol, start=start_date, end=end_date, interval="1m", progress=False)
    
    if data.empty:
        print("No data retrieved. Check your internet connection or try a different date range.")
        return None
    
    # Print column information for debugging
    print(f"Original columns: {data.columns}")
    
    # Reset index to make Datetime a column instead of an index
    data = data.reset_index()
    
    # Add a Ticker column
    data['Ticker'] = symbol
    
    # Handle multi-level columns if they exist
    if isinstance(data.columns[0], tuple):
        # Convert multi-level column names to single-level
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    
    # Reorder columns to match desired output format
    columns_to_include = ['Datetime', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    # Ensure all required columns exist
    for col in columns_to_include:
        if col not in data.columns:
            print(f"Warning: Column '{col}' not found in data. Available columns: {data.columns.tolist()}")
    
    # Only include columns that exist in the data
    available_columns = [col for col in columns_to_include if col in data.columns]
    data = data[available_columns]
    
    # Drop the 'Adj Close' column if it exists
    if 'Adj Close' in data.columns:
        data = data.drop('Adj Close', axis=1)
    
    return data

# Get and process the data
historical_data = get_historical_data()

if historical_data is not None:
    # Save to CSV with proper formatting
    historical_data.to_csv(output_file, index=False)
    
    # Verify the file was created
    if os.path.exists(output_file):
        print(f"CSV file for {symbol} 1-minute data (past week) generated successfully!")
        print(f"File saved as: {output_file}")
        
        # Safely print column names by converting them to strings first
        column_names = [str(col) for col in historical_data.columns]
        print(f"Headers: {', '.join(column_names)}")
        print(f"Total rows: {len(historical_data)}")
        
        # Print a sample of the data
        print("\nSample of the data (first 3 rows):")
        print(historical_data.head(3).to_string())
    else:
        print(f"Error: Failed to create {output_file}")