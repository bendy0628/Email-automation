import os
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def generate_email_variations(full_name, domain):
    name_parts = full_name.split()
    
    variations = set()  
    
    if len(name_parts) == 1:
        first_name = name_parts[0]
        variations.update([ 
            f"{first_name}@{domain}",                     
            f"{first_name[0]}@{domain}",                  
        ])
    elif len(name_parts) == 2:
        first_name, last_name = name_parts
        variations.update([ 
            f"{first_name}{last_name}@{domain}",          
            f"{first_name}.{last_name}@{domain}",         
            f"{first_name[0]}{last_name}@{domain}",       
            f"{first_name}{last_name[0]}@{domain}",       
            f"{first_name}.{last_name[0]}@{domain}",      
            f"{first_name[0]}.{last_name}@{domain}",      
            f"{last_name}{first_name}@{domain}",          
            f"{last_name}.{first_name}@{domain}",         
            f"{last_name[0]}{first_name}@{domain}",       
            f"{last_name}{first_name[0]}@{domain}",       
            f"{last_name[0]}.{first_name}@{domain}",      
            f"{first_name}@{domain}",                     
            f"{last_name}@{domain}",                      
        ])
    elif len(name_parts) >= 3:
        first_name, *middle_names, last_name = name_parts
        middle_initials = "".join([name[0] for name in middle_names])
        variations.update([ 
            f"{first_name}{''.join(middle_names)}{last_name}@{domain}",  
            f"{first_name}.{'.'.join(middle_names)}.{last_name}@{domain}",  
            f"{first_name[0]}{middle_initials}{last_name}@{domain}",  
            f"{first_name}{middle_initials}{last_name}@{domain}",  
            f"{first_name[0]}.{middle_initials}.{last_name}@{domain}",  
            f"{first_name}{last_name}@{domain}",  
            f"{first_name}.{last_name}@{domain}",  
            f"{first_name[0]}{last_name}@{domain}",  
            f"{first_name}{last_name[0]}@{domain}",  
            f"{first_name[0]}.{last_name}@{domain}",  
            f"{last_name}{first_name}@{domain}",  
            f"{last_name}.{first_name}@{domain}",  
            f"{last_name[0]}{first_name}@{domain}",  
            f"{last_name}{first_name[0]}@{domain}",  
            f"{last_name[0]}.{first_name}@{domain}",  
            f"{first_name}@{domain}",                     
            f"{last_name}@{domain}",     
            f"{first_name}.{'.'.join(middle_names)}{last_name}@{domain}",
            
        ])
    
    return list(variations)

def authenticate_google_account():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(body, 'plain')
    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(service, sender_email, receiver_email, subject, body):
    try:
        message = create_message(sender_email, receiver_email, subject, body)
        send_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")

def main():
    sender_email = ""  
    subject = "Hello"
    body = "Hey there, this is a test email you can just ignore it thanks."
    service = authenticate_google_account()

    while True:
        full_name = input("\nEnter the full name (e.g., 'ali ahmed' or 'ali muhammad ahmed'): ").strip()
        domain = input("Enter the domain name (e.g., 'lootah.com'): ").strip()

        email_variations = generate_email_variations(full_name, domain)

        print("\nGenerated email addresses:")
        for email in email_variations:
            print(email)

        for email in email_variations:
            send_email(service, sender_email, email, subject, body)

        

if __name__ == "__main__":
    main()

