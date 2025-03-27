# Train and Taxi Expense Processing

## Overview
This project automates the processing of train tickets and taxi receipts from email, generating monthly summary reports with proper descriptions and calculations. It supports configurable routes and can be customized to handle various train journeys and associated expenses.

## Features
- Automatically fetches train ticket emails from your inbox
- Downloads and organizes PDF attachments
- Calculates total expenses including train tickets and taxi fares
- Generates monthly summary reports in CSV format
- Supports multiple configurable routes with customizable keywords and prices

## Prerequisites
- Python 3.6 or higher
- Access to an email account via IMAP
- Required Python packages (install via `pip install -r requirements.txt`):
  - pandas
  - python-dotenv
  - imaplib (usually included with Python)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd train-taxi-expense-processing
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

5. Configure the following variables in your `.env` file:
- `EMAIL_USER`: Your email address
- `EMAIL_PASS`: Your email password or app-specific password
- `IMAP_SERVER`: Your IMAP server (e.g., imap.gmail.com)
- `SEARCH_YEAR`: Year to process (e.g., "2024")
- `SEARCH_MONTH`: Month to process (e.g., "Jan", "Feb", etc.)
- `SENDER_EMAIL`: Email address that sends the train tickets
- `TAXI_FARE`: Standard taxi fare amount to add per trip

6. Configure your train routes by adding the following for each route:
- `ROUTE_X_NAME`: Name of the route (e.g., "KENITRA - CASA PORT")
- `ROUTE_X_KEYWORDS`: Comma-separated keywords that identify this route in emails
- `ROUTE_X_PRICE`: Price of the train ticket for this route

Example route configuration:
```
ROUTE_1_NAME="KENITRA - CASA PORT"
ROUTE_1_KEYWORDS="KENITRA - CASA PORT,Kenitra Casa Port,KENITRA CASA PORT"
ROUTE_1_PRICE=60

ROUTE_2_NAME="CASA PORT - KENITRA"
ROUTE_2_KEYWORDS="CASA PORT - KENITRA,Casa Port Kenitra,CASA PORT KENITRA"
ROUTE_2_PRICE=100
```

You can add as many routes as needed by incrementing the route number.

## Usage

1. Ensure your `.env` file is properly configured

2. Run the script:
```bash
python main.py
```

3. The script will:
   - Connect to your email account
   - Search for relevant train ticket emails
   - Download PDF attachments to `attachments/YYYY-MMM/` directory
   - Generate a summary CSV file in `data/YYYY-MMM-summary.csv`

## Output Format

The generated CSV file includes the following columns:
- DATE: Date of travel
- CLIENT: Client name (to be filled manually)
- PROJET: Project name (to be filled manually)
- TYPE DE FACTURATION: Type of billing (always "Transport")
- DESCRIPTION: Description of expenses (e.g., "2 billets de train et taxi aller-retour")
- TYPE: Type of expense (to be filled manually)
- MONTANT: Total amount including train tickets and taxi fare

## Directory Structure
```
.
├── attachments/          # Downloaded PDF attachments
│   └── YYYY-MMM/        # Organized by year and month
├── data/                # Generated CSV reports
├── .env                 # Configuration file
├── main.py             # Main script
└── README.md           # This file
```

## Notes
- The script automatically looks for train routes based on your configuration in the .env file
- Multiple train routes can be defined with different prices
- Email keywords are used to identify which route a particular ticket belongs to
- PDF attachments are saved with a date prefix for better organization
- The summary CSV groups multiple tickets on the same day

## How Route Configuration Works
The script uses the route configurations to:
1. Search for emails containing keywords for any configured route
2. Identify which specific route a ticket belongs to based on email content
3. Apply the correct price for that route in the expense summary
4. Generate appropriate descriptions in the summary report

You can add, modify, or remove routes by editing the .env file without changing the code.

## Contributing
Feel free to submit issues and enhancement requests!

## License
[Add your license information here]
