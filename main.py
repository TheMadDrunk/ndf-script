import imaplib
import email
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load credentials from .env
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER")

# Configurable parameters
# Month to search for in emails (e.g., "Jan" for January)
SEARCH_MONTH = os.getenv("SEARCH_MONTH")

# Year to search for in emails
SEARCH_YEAR = os.getenv("SEARCH_YEAR")

# Email address to filter emails from
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

# Default taxi fare amount if not specified in environment
TAXI_FARE = float(os.getenv("TAXI_FARE", 30))  # Default: 30

# Load route configurations
def load_route_configs():
    """Load route configurations from environment variables."""
    routes = {}
    route_index = 1
    
    while True:
        route_name = os.getenv(f"ROUTE_{route_index}_NAME")
        if not route_name:
            break
            
        keywords = os.getenv(f"ROUTE_{route_index}_KEYWORDS", "").split(",")
        price = float(os.getenv(f"ROUTE_{route_index}_PRICE", 0))
        
        if keywords and price > 0:
            routes[route_name] = {
                "keywords": [k.strip() for k in keywords],
                "price": price
            }
        
        route_index += 1
    
    return routes

# Load route configurations
ROUTE_CONFIGS = load_route_configs()

# Create search keywords from all route keywords
SEARCH_KEYWORDS = []
for route_config in ROUTE_CONFIGS.values():
    SEARCH_KEYWORDS.extend(route_config["keywords"])

# Folders
ATTACHMENT_DIR = f"attachments/{SEARCH_YEAR}-{SEARCH_MONTH}"
os.makedirs(ATTACHMENT_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

def connect_to_email():
    """Connect to IMAP server and select inbox."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    return mail

def get_next_month_and_year(month, year):
    """Get the next month and year."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    current_month_index = months.index(month)
    if current_month_index == 11:  # December
        next_month = months[0]  # January
        next_year = str(int(year) + 1)
    else:
        next_month = months[current_month_index + 1]
        next_year = year
        
    return next_month, next_year

def search_emails(mail):
    """Search for emails in the given month from a specific sender containing route keywords."""
    (next_month, next_year) = get_next_month_and_year(SEARCH_MONTH, SEARCH_YEAR)
    
    # Create search criteria for all keywords
    search_criteria_parts = []
    for keyword in SEARCH_KEYWORDS:
        if keyword.strip():  # Skip empty keywords
            search_criteria_parts.append(
                f'FROM {SENDER_EMAIL} BODY "{keyword.strip()}" '
                f'SINCE "1-{SEARCH_MONTH}-{SEARCH_YEAR}" '
                f'BEFORE "1-{next_month}-{next_year}"'
            )
    
    search_criteria = " OR ".join(search_criteria_parts)
    print(f"Searching with criteria: {search_criteria}")
    result, data = mail.search(None, search_criteria)
    print(f"Search result: {result}, {data}")
    return data[0].split()

def find_matching_route(email_body):
    """Find the matching route based on keywords in the email body."""
    for route_name, config in ROUTE_CONFIGS.items():
        for keyword in config["keywords"]:
            if keyword.strip() in email_body:
                return route_name, config["price"]
    return None, 0

def extract_email_data(mail, email_ids):
    """Extract relevant data from emails and download PDF attachments."""
    email_data = []  # List to store detailed information for each email

    for e_id in email_ids:
        result, data = mail.fetch(e_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract email date with flexible parsing
        email_date = msg["Date"]
        try:
            date_obj = datetime.strptime(email_date, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            try:
                date_obj = datetime.strptime(email_date, "%d %b %Y %H:%M:%S %z")
            except ValueError:
                print(f"Warning: Could not parse date '{email_date}', skipping...")
                continue

        date_str = date_obj.strftime("%d/%m/%Y")
        
        # Download PDF attachments
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename and filename.lower().endswith('.pdf'):
                # Create a safe filename with date and original name
                safe_filename = f"{date_obj.strftime('%Y%m%d')}_{filename}"
                filepath = os.path.join(ATTACHMENT_DIR, safe_filename)
                
                # Save the attachment
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                print(f"Saved attachment: {safe_filename}")
        
        # Extract email body and process ticket information
        email_body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                email_body = part.get_payload(decode=True).decode()
                break
        
        # Find matching route and price
        route_found, ticket_price = find_matching_route(email_body)

        if route_found:
            # Store email information
            email_data.append({
                'DATE': date_str,
                'CLIENT': '',  # To be filled manually
                'PROJET': '',  # To be filled manually
                'TYPE DE FACTURATION': 'Transport',
                'BILLET': 1,
                'ROUTE': route_found,
                'TYPE': '',  # To be filled manually
                'MONTANT': ticket_price
            })

    return email_data

def write_summary_csv(email_data):
    """Write the detailed summary to a CSV file."""
    if not email_data:
        print("No email data to process")
        return
        
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(email_data)
    
    # Group by date to combine tickets for the same day
    grouped = df.groupby('DATE').agg({
        'CLIENT': 'first',
        'PROJET': 'first',
        'TYPE DE FACTURATION': 'first',
        'TYPE': 'first',
        'MONTANT': 'sum',  # Sum the ticket prices
        'BILLET': 'sum',
        'ROUTE': lambda x: ', '.join(set(x))  # Combine unique routes
    }).reset_index()

    # Update description with correct ticket count and routes
    grouped['DESCRIPTION'] = grouped.apply(
        lambda row: f"{int(row['BILLET'])} billet{'s' if row['BILLET'] > 1 else ''} de train ({row['ROUTE']}) et taxi aller-retour",
        axis=1
    )
    
    # Add taxi fare
    grouped['MONTANT'] = grouped['MONTANT'] + TAXI_FARE
    
    # Sort by date
    grouped = grouped.sort_values('DATE')
    
    # Reorder columns to match desired format
    columns = ['DATE', 'CLIENT', 'PROJET', 'TYPE DE FACTURATION', 'DESCRIPTION', 'TYPE', 'MONTANT']
    grouped = grouped[columns]
    
    # Save to CSV
    output_file = f"data/{SEARCH_YEAR}-{SEARCH_MONTH}-summary.csv"
    grouped.to_csv(output_file, index=False)
    print(f"CSV summary created: {output_file}")

if __name__ == "__main__":
    if not ROUTE_CONFIGS:
        print("No route configurations found in .env file. Please configure at least one route.")
        exit(1)
        
    mail = connect_to_email()
    print("Connected to email")
    email_ids = search_emails(mail)
    print(f"Found {len(email_ids)} matching emails")
    email_data = extract_email_data(mail, email_ids)
    print(f"Extracted data from {len(email_data)} emails")
    write_summary_csv(email_data)
    mail.logout()
