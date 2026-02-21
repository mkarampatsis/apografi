import requests
from requests.adapters import HTTPAdapter, Retry
import sys, os
from dotenv import load_dotenv
from smtplib import SMTP as SMTP # this invokes the secure SMTP protocol (port 465, uses SSL)
from email.mime.text import MIMEText

from models.sdad.embedded import (
  SubOrganizationDoc, OrganizationDoc, ContactDoc, CountryDoc, CityDoc,
  FekDoc, MainAddressDoc, supervisorUnitCodeDoc, PurposeDoc, 
  UnitTypeDoc, SecondaryAddressesDoc, SpatialDoc
)

load_dotenv()

SMTPSERVER = os.getenv('EMAIL_SMTPSERVER')
USERNAME = os.getenv('EMAIL_USERNAME')
PASSWORD = os.getenv('EMAIL_PASSWORD')
SENDER = os.getenv('EMAIL_SENDER')
DESTINATION = os.getenv('EMAIL_DESTINATION').split(",")

subjects = {
  "dictionaries":"Thryallis - Συγχρονισμός Λεξικών ΣΔΑΔ",
  "organizations":"Thryallis - Συγχρονισμός Φορέων ΣΔΑΔ",
  "organizational_units":"Thryallis - Συγχρονισμός Μονάδων ΣΔΑΔ",
  "sync_organizations_sdad_with_psped":"Thryallis - Συγχρονισμός Φορέων ΣΔΑΔ με ΠΣΠΕΔ",
  "sync_organizational_units_sdad_with_psped":"Thryallis - Συγχρονισμός Μονάδων ΣΔΑΔ με ΠΣΠΕΔ"
}

messages = {
  "dictionaries": '''
      <p>Ο συγχρονισμός των λεξικών από ΣΔΑΔ ολοκληρώθηκε</p>
      <p>Ώρα που ξεκίνησε: %s</p>
      <p>Ώρα που τελείωσε: %s</p>
  ''' ,
  "organizations": '''
      <p>Ο συγχρονισμός των φορέων από ΣΔΑΔ ολοκληρώθηκε</p>
      <p>Ώρα που ξεκίνησε: %s</p>
      <p>Ώρα που τελείωσε: %s</p>
  ''' ,
  "organizational_units":'''
      <p>Ο συγχρονισμός των μονάδων από ΣΔΑΔ ολοκληρώθηκε</p>
      <p>Ώρα που ξεκίνησε: %s</p>
      <p>Ώρα που τελείωσε: %s</p>
  ''',
  "sync_organizations_sdad_with_psped":'''
      <p>Ο συγχρονισμός των φορεών από ΣΔΑΔ σε ΠΣΠΕΔ ολοκληρώθηκε</p>
      <p>Ώρα που ξεκίνησε: %s</p>
      <p>Ώρα που τελείωσε: %s</p>
  '''
  ,
  "sync_organizational_units_sdad_with_psped":'''
      <p>Ο συγχρονισμός των μονάδων από ΣΔΑΔ σε ΠΣΠΕΔ ολοκληρώθηκε</p>
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

    conn = SMTP("mailgate.cosmotemail.gr", 587)
    conn.set_debuglevel(False)  # enable debug to see server responses

    conn.ehlo()
    conn.starttls()
    conn.ehlo()  # required after STARTTLS

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



def normalize_embedded(item):
   
  if item.get("subOrganizationOf"):
    item["subOrganizationOf"] = SubOrganizationDoc(**item["subOrganizationOf"])

  if item.get("organizationType"):
    item["organizationType"] = OrganizationDoc(**item["organizationType"])

  if item.get("contactPoint"):
    item["contactPoint"] = ContactDoc(**item["contactPoint"])

  if item.get("foundationFek"):
    item["foundationFek"] = FekDoc(**item["foundationFek"])

  if item.get("mainAddress"):
    addr = item["mainAddress"]
    item["mainAddress"] = MainAddressDoc(
      fullAddress=addr.get("fullAddress"),
      postCode=addr.get("postCode"),
      country=CountryDoc(**addr["country"]) if addr.get("country") else None,
      city=CityDoc(**addr["city"]) if addr.get("city") else None,
    )

  if item.get("secondaryAddresses"):
    value = item['secondaryAddresses']
    item["secondaryAddresses"] = [
      SecondaryAddressesDoc(
        fullAddress=addr["fullAddress"],
        postCode=addr["postCode"],
        country=CountryDoc(**addr["country"]) if addr.get("country") else None,
        city=CityDoc(**addr["city"]) if addr.get("city") else None,
      ) for addr in value
    ]
  
  if item.get("spatial"):
    value = item['spatial']
    item["spatial"] = [SpatialDoc(**item) for item in value] 
  
  if item.get("supervisorUnitCode"):
    item["supervisorUnitCode"] = supervisorUnitCodeDoc(**item["supervisorUnitCode"]) 

  if item.get("purpose"):
    value = item['purpose']
    item["purpose"] = [PurposeDoc(**item) for item in value]

  if item.get("unitType"):
    item["unitType"] = UnitTypeDoc(**item["unitType"]) 

  return item

