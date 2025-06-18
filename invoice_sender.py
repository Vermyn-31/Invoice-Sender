from pathlib import Path
from collections import defaultdict
import smtplib, ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Config Personal Details
sender_name = input("Enter your name: ")
gcash_number = input("Enter your contact number: ")
fb_link = input("Enter your Facebook link: ")

# Email configuration
port = 465
smtp_server = "smtp.gmail.com"
sender_email = input("Enter your email address: ")          
sender_password = input("Enter your email password (app password): ")
recipient_email = input("Enter the recipient's email address: ")    

# File path and order dictionary
fpath = Path.cwd().joinpath('invoice_text.txt')
order_name = defaultdict(list)

# Read and parse the file
with open(fpath, 'r') as f:
    for entry in f:
        entry = entry.strip()
        if entry:
            parts = entry.split('-')
            if len(parts) == 3:
                name, bundle, price = parts
                try:
                    order_name[name.strip()].append((bundle.strip(), int(price.strip())))
                except ValueError:
                    print(f"Invalid price format in line: {entry}")
            else:
                print(f"Skipping malformed line: {entry}")

# GCash and payment instructions
gcash_details = (
    "\nGCash Details 🫶\n"
    f"Number: {gcash_number}\n"
    f"Name: {sender_name}s\n\n"
    "For proof of payments, please send the screenshot to:\n"
    f"{fb_link}\n\n"
    "Please also include the following information for J&T Shipping\n"
    "Name: \n"
    "Contact Number: \n"
    "Address: \n"
)

# Footer note
footer_note = "Note that this is an automated message created to send the invoices. Please see the sent message."

# Create secure connection
context = ssl.create_default_context()

# Current date
today = date.today().isoformat()

# Calculate total earnings across all customers
total_earnings = 0

try:
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, sender_password)
        
        # First: Send individual invoices
        for name, orders in order_name.items():
            message_lines = [
                f"Subject: Invoice for {name} - {today}\n",
                f"Hello, here is the order summary for {name}:\n"
            ]
            customer_total = 0
            for bundle, price in orders:
                message_lines.append(f" - {bundle}: ₱{price}")
                customer_total += price
                total_earnings += price  
            
            message_lines.append(f"\nTotal: ₱{customer_total}")
            message_lines.append(gcash_details)
            message_lines.append(footer_note)

            email_body = "\n".join(message_lines)

            # Send the email
            server.sendmail(sender_email, recipient_email, email_body.encode('utf-8'))
            print(f"Successfully sent invoice for {name} to {recipient_email}")
        
        # Second: Send earnings summary
        summary_msg = MIMEMultipart()
        summary_msg['From'] = sender_email
        summary_msg['To'] = recipient_email
        summary_msg['Subject'] = f"Earnings Summary - {today}"
        
        summary_body = f"""
        <h2>Total Earnings Report</h2>
        <p>Date: {today}</p>
        <p>Total customers: {len(order_name)}</p>
        <p><strong>Total earnings: ₱{total_earnings}</strong></p>
        <p>Breakdown by customer:</p>
        <ul>
        """
        
        for name, orders in order_name.items():
            customer_total = sum(price for _, price in orders)
            summary_body += f"<li>{name}: ₱{customer_total}</li>"
        
        summary_body += """
        </ul>
        <p>This is an automated earnings report.</p>
        """
        
        summary_msg.attach(MIMEText(summary_body, 'html'))
        
        server.sendmail(sender_email, recipient_email, summary_msg.as_string())
        print(f"\nSuccessfully sent earnings summary (₱{total_earnings}) to {recipient_email}")
            
except Exception as e:
    print(f"Failed to send emails: {e}")