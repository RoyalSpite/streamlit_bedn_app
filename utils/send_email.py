import streamlit as st
import smtplib
from email.mime.text import MIMEText

def send_email(recipient, payload):
    
    sender = st.secrets['mastermail']['email']
    body = payload['body']
    
    msg = MIMEText(body, 'html')
    msg['Subject'] = payload['subject']
    msg['From'] = sender
    msg['To'] = recipient
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, st.secrets['mastermail']['password'])
            smtp_server.sendmail(sender, recipient, msg.as_string())
    except Exception as e:
        return "failed"
    else:
        return "success"
    
    
