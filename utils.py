import requests
from requests.adapters import HTTPAdapter, Retry
import sys
from smtplib import SMTP as SMTP # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText

from datetime import datetime

SMTPSERVER = "smtp.ntua.gr"
SENDER = 'no-reply@thryallis.ypes.gov.gr'
DESTINATION = ['antpsarakis@gmail.com','marka@central.ntua.gr']

USERNAME = "jraptaki"
PASSWORD = "l1vadak1a"

subjects = {
  "dictionaries":"Thryallis - Συγχρονισμός Λεξικών Απογραφής",
  "organizations":"Thryallis - Συγχρονισμός Φορέων Απογραφής",
  "organizational_units":"Thryallis - Συγχρονισμός Μονάδων Απογραφής",
}

messages = {
    "dictionaries": '''
        <p>Ο συγχρονισμός των λεξικών ολοκληρώθηκε</p>
        <p>Ώρα που ξεκίνησε: %s</p>
        <p>Ώρα που τελείωσε: %s</p>
    ''' ,
    "organizations": '''
        <p>Ο συγχρονισμός των φορέων ολοκληρώθηκε</p>
        <p>Ώρα που ξεκίνησε: %s</p>
        <p>Ώρα που τελείωσε: %s</p>
    ''' ,
    "organizational_units":'''
        <p>Ο συγχρονισμός των μονάδων ολοκληρώθηκε</p>
        <p>Ώρα που ξεκίνησε: %s</p>
        <p>Ώρα που τελείωσε: %s</p>
    '''
}
def url_get(URL):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount(URL, HTTPAdapter(max_retries=retries))
    headers = {"Accept": "application/json"}
    return session.get(URL, headers=headers)

def send_email(typeOf, start_time, end_time):
  try:
    print("Start sending email")
    text = messages[typeOf] % (start_time, end_time)
    subject = subjects[typeOf]
    
    msg = MIMEText(text, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = ", ".join(DESTINATION)

    conn = SMTP(SMTPSERVER, port=25)
    conn.set_debuglevel(False)
    conn.ehlo()
    conn.starttls()  # enable TLS
    # If authentication is required, uncomment and set USERNAME and PASSWORD
    conn.login(USERNAME, PASSWORD)

    try:
        conn.sendmail(SENDER, DESTINATION, msg.as_string())
        print("Message sent")
    except Exception as e:
        print("Send error:", e)
    finally:
        conn.quit()

  except Exception as e:
    sys.exit("Μail failed; %s" % str(e))  # give an error message