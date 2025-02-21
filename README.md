# Train and Taxi Expense Processing

## Overview
This project automates the processing of train tickets and taxi receipts from email, generating monthly summary reports with proper descriptions and calculations. It specifically handles train tickets between Kenitra and Casa Port, along with associated taxi expenses.

## Features
- Automatically fetches train ticket emails from your inbox
- Downloads and organizes PDF attachments
- Calculates total expenses including train tickets and taxi fares
- Generates monthly summary reports in CSV format
- Supports both directions: Kenitra to Casa Port and Casa Port to Kenitra

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
- The script automatically calculates:
  - Kenitra to Casa Port: 60 DH per ticket
  - Casa Port to Kenitra: 100 DH per ticket
  - Additional taxi fare as specified in .env
- PDF attachments are saved with a date prefix for better organization
- The summary CSV groups multiple tickets on the same day

## Contributing
Feel free to submit issues and enhancement requests!

## License
[Add your license information here]
