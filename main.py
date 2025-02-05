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
SEARCH_MONTH = os.getenv("SEARCH_MONTH")  # Example: "Jan" for January
SEARCH_YEAR = os.getenv("SEARCH_YEAR")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SUBJECT_KEYWORDS = ["KENITRA - CASA PORT", "CASA PORT - KENITRA"] # Both directions

# Folders
ATTACHMENT_DIR = f"attachments/{SEARCH_YEAR}-{SEARCH_MONTH}"
os.makedirs(ATTACHMENT_DIR, exist_ok=True)

def connect_to_email():
    """Connect to IMAP server and select inbox."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    return mail

def get_next_month_and_year(month, year):
    """Get the next month and year."""
    if month == "Dec":
        return "Jan", str(int(year) + 1)
    else:
        return "Feb", year

def search_emails(mail):
    """Search for emails in the given month from a specific sender containing either keyword."""
    (next_month, next_year) = get_next_month_and_year(SEARCH_MONTH, SEARCH_YEAR)
    
    # Create two separate search criteria for each direction
    search_criteria_1 = f'FROM {SENDER_EMAIL} BODY "{SUBJECT_KEYWORDS[0]}" SINCE "1-{SEARCH_MONTH}-{SEARCH_YEAR}" BEFORE "1-{next_month}-{next_year}"'
    search_criteria_2 = f'FROM {SENDER_EMAIL} BODY "{SUBJECT_KEYWORDS[1]}" SINCE "1-{SEARCH_MONTH}-{SEARCH_YEAR}" BEFORE "1-{next_month}-{next_year}"'
    search_criteria = f'{search_criteria_1} OR {search_criteria_2}'
    print(f"Searching with criteria: {search_criteria}")
    result, data = mail.search(None, search_criteria)
    print(f"Search result: {result}, {data}")
    return data[0].split()

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
        
        billets = 0
        ticket_price = 0
        if "KENITRA - CASA PORT" in email_body:
            billets+=1
            ticket_price += 60
        elif "CASA PORT - KENITRA" in email_body:
            billets+=1
            ticket_price += 100

        # Store email information
        email_data.append({
            'DATE': date_str,
            'CLIENT': '',  # To be filled manually
            'PROJET': '',  # To be filled manually
            'TYPE DE FACTURATION': 'Transport',
            'BILLET': billets,
            'TYPE': '',  # To be filled manually
            'MONTANT': ticket_price
        })

    return email_data

def write_summary_csv(email_data):
    """Write the detailed summary to a CSV file."""
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
    }).reset_index()
    print("df",df)
    print("grouped",grouped)
    # Update description with correct ticket count
    grouped['DESCRIPTION'] = grouped['BILLET'].apply(
        lambda row: f"{row} billets de train et taxi aller-retour"
    )
    
    # Add taxi fare (30dh per day)
    grouped['MONTANT'] = grouped['MONTANT'] + 30  # Add fixed taxi fare
    
    # Sort by date
    grouped = grouped.sort_values('DATE')
    
    # Reorder columns to match desired format
    columns = ['DATE', 'CLIENT', 'PROJET', 'TYPE DE FACTURATION', 'DESCRIPTION', 'TYPE', 'MONTANT']
    grouped = grouped[columns]
    
    # Save to CSV
    grouped.to_csv(f"data/{SEARCH_YEAR}-{SEARCH_MONTH}-summary.csv", index=False)
    print(f"CSV summary created: data/{SEARCH_YEAR}-{SEARCH_MONTH}-summary.csv")

if __name__ == "__main__":
    mail = connect_to_email()
    print("Connected to email")
    email_ids = search_emails(mail)
    print("Emails found")
    email_data = extract_email_data(mail, email_ids)
    print("Email data extracted")
    write_summary_csv(email_data)
    print("Summary CSV created")
    mail.logout()
