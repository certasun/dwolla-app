from flask import Flask, session, render_template, request, redirect, url_for
from cryptography.fernet import Fernet
import stripe
import dwollav2
import plaid
import base64
import os
import datetime
import json
import time
from flask import jsonify, abort, session
from plaid import Client
from simple_salesforce import Salesforce
import pprint
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField
import json
from flask_mail import Mail, Message
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.headerregistry import Address
from email.message import EmailMessage
from email.mime.image import MIMEImage
from jinja2 import Environment, PackageLoader
import jinja2
import imghdr
from email.utils import make_msgid
import locale
from instance import config
application = Flask(__name__, instance_relative_config=True)
#application.config.from_object('config')
application.config.from_pyfile('config.py')
mail_settings = {
    "MAIL_SERVER" : 'smtp.gmail.com',
    "MAIL_PORT" : 587,
    "MAIL_USE_TLS" : False,
    "MAIL_USE_TLS" : True,
    "MAIL_USERNAME" : 'wayno5650@gmail.com',
    "MAIL_PASSWORD" : 'Cush5656'
}

shakey = b'hFII8Cjt5yJZZDhginbe0tleSP7hT1GNM8k3-LkhI_c='
DWOLLA_SECRET = "qR7smUqNapsNLeAv3UNyVB1kpPhVnZBQEUk42fHBeDJejTHiIa"
DWOLLA_KEY = 'eddj4apa27lHlL4uMuwkkGsGiQ9IHH9MT3LrMvvvDhq1lLJwv1'
ACCESS_SECRET_KEY = 'tc07v1nNDGw6SOWO1xtx0pOSDQpaxYmx1Zd6j2A'
SECRET_KEY = '5791628bb0b13ce0c67dfde280ba245'
pub_key = 'pk_test_5PPWDFa356A5VTg8k3qXKIQE'
secret_key = 'sk_test_YfkekeTtUjhcaJEccJojqD6q'
PLAID_CLIENT_ID='5d07c2f19585840015a41676'
PLAID_SECRET='3554c62d5732888c8099296d93cdfb'
PLAID_SECRET_SAND = '2ceef8e0abfc857bb801f7dffd06a9'
PLAID_PUBLIC_KEY='89066d105257beb46bc1873e92467e'
DWOLLA_ACCOUNT_FUNDING_SOURCE_ID =  '94e5a2f5-0bb3-4cf6-9e32-8081be3040c5'
sf_user = 'nwayn@certasun.com'
sf_pass = 'Meerkat3250'
sf_consumer_key = '3MVG9vrJTfRxlfl7JrAPVnSBJscooRaBSEHaV0RU0Nh26ID0am9ZyHz5wQ99NhDv_uBXnw9lUy6rsXLa0byTU'
sf_consumerr_secret = 'F851D4F3EAA855D44D1A0B3FC543053B26FB333A212A444EDF13528CF755854D'
sf_token = 'gmrlB5Pl79Nykd1UP4rl3tOC'
DOWN_PAYMENT_CONST = "Down Payment"
PERMIT_PAYMENT_CONST = "Permit Payment"
FINAL_PAYMENT_CONST = "Final Payment"
DUE_STATUS = "Due"
NOT_DUE_STATUS = "Not Due"
gmailaddress = "wayno5650@gmail.com"
gmailpassword = "Cush5656"
mailto = "nathan@certasun.com"
DWOLLA_UNVERIFIED_LIMIT = 50
DWOLLA_VERIFIED_LIMIT = 30000
PLAID_BALANCE = 10
cipher_suite = Fernet(shakey)
application.config.update(mail_settings)
mail = Mail(application)
mail.init_app(application)
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')
client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET_SAND, public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')
dwolla_client = dwollav2.Client( key = DWOLLA_KEY, secret = DWOLLA_SECRET, environment = 'sandbox')
pp = pprint.PrettyPrinter(indent=2)
app_token = dwolla_client.Auth.client()
stripe.api_key = secret_key
sf = Salesforce(sf_user +".plaidtest", sf_pass, sf_token, domain = 'test')
class nameForm(FlaskForm):
    name = StringField('Email')
    submit = SubmitField('SUBMIT')

class retryForm(FlaskForm):
    firstName = StringField('FirstName')
    lastName = StringField('lastName')
    street_address = StringField('Street Address')
    city = StringField('City')
    state_Code = StringField('State Code')
    zip = StringField('ZIP Code')
    retry_email = StringField('Email')
    DOB = StringField('DOB (YYYY-MM-DD)')
    SSN = PasswordField('SSN (Full 9 Digits)')
    submit = SubmitField('SUBMIT')

class decodeForm(FlaskForm):
    hash = PasswordField('hash')
    submit = SubmitField('submit')

class verificationForm(FlaskForm):
    SSN = PasswordField('Last 4 of SSN')
    DOB = DateField('DOB (YYYY-MM-DD)')
    submit = SubmitField('Submit')

class ACCOUNT:
    def __init__(self, name, fname, lname):

        self.name = name
        self.fname = fname
        self.lname = lname
        self.dp = 0
        self.pp = 0
        self.fp = 0
        self.dpSTAT = ""
        self.ppSTAT = ""
        self.fpSTAT = ""
        self.ID = 0
        self.duePayment = ""
        self.chargeAmount = 0

    def getnextpayment(self):
        if self.duePayment == DOWN_PAYMENT_CONST:
            self.chargeAmount = self.dp
            return self.dp
        if self.duePayment == PERMIT_PAYMENT_CONST:
            self.chargeAmount = self.pp
            return self.pp
        if self.duePayment == FINAL_PAYMENT_CONST:
            self.chargeAmount = self.fp
            return self.fp
        return 0
    def toJSON(self):
        return self.__dict__

    def getDuePayment(self):
        if self.dpSTAT == DUE_STATUS or self.dpSTAT == NOT_DUE_STATUS:
            self.duePayment = DOWN_PAYMENT_CONST
            return DOWN_PAYMENT_CONST
        elif self.ppSTAT == DUE_STATUS or self.ppSTAT == NOT_DUE_STATUS:
            self.duePayment = PERMIT_PAYMENT_CONST
            return PERMIT_PAYMENT_CONST
        elif self.fpSTAT == DUE_STATUS or self.fpSTAT == NOT_DUE_STATUS:
            self.duePayment = FINAL_PAYMENT_CONST
            return FINAL_PAYMENT_CONST
        else:
            self.duePayment = "NA"
        return "NA"

def toOBJ(myobj):
        OBJ = ACCOUNT(myobj['name'], myobj['fname'], myobj['lname'])
        OBJ.dp = myobj['dp']
        OBJ.pp = myobj['pp']
        OBJ.fp = myobj['fp']
        OBJ.dpSTAT = myobj['dpSTAT']
        OBJ.ppSTAT = myobj['ppSTAT']
        OBJ.fpSTAT = myobj['fpSTAT']
        OBJ.ID = myobj['ID']
        OBJ.duePayment = myobj['duePayment']
        OBJ.chargeAmount = myobj['chargeAmount']
        return OBJ

@application.route('/', methods = ['POST'])
def templateEmailnew():
    if request.method == "POST":
        pp.pprint(request.json)
        id = request.json['id']
        #email = request.json['email']
    id = 'a0Yg0000006ELA5EAO'
    email = "accountholder21@example.com"
    email_link = "http://localhost:5000/linkwithid/a0Yg0000006ENn2EAG"
    id = "a0Yg0000006ENn2EAG"
    templateLoader = jinja2.FileSystemLoader(searchpath = "/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    #projID = get_proj_from_sf(email)
    query = sf.query("select id, Name, Cash_Down_Pmt_Status__c, Cash_Down_Pmt__c, Cash_Permit_Pmt_Status__c, Permit_Pmt__c, Cash_Final_Pmt_Status__c, Cash_final_Pmt__c from Project__c where ID =  '"+id+"'")
    pp.pprint(query)
#    p_name = query['records'][0]['Name']
    p_down = query['records'][0]['Cash_Down_Pmt__c']
    p_down_stat = query['records'][0]['Cash_Down_Pmt_Status__c']
    p_permit = query['records'][0]['Permit_Pmt__c']
    p_permit_stat = query['records'][0]['Cash_Permit_Pmt_Status__c']
    p_final = query['records'][0]['Cash_Final_Pmt__c']
    p_final_stat = query['records'][0]['Cash_Final_Pmt_Status__c']
    proj_name = query['records'][0]['Name']
    address_query = sf.query("select Name, MailingAddress from contact where email = '"+email+"'")
    pp.pprint(address_query)
    address = address_query['records'][0]['MailingAddress']['street'] + " " + address_query['records'][0]['MailingAddress']['city'] + ", " + address_query['records'][0]['MailingAddress']['state']
    proj_name_list = proj_name.split()
    email_recipient_account = ACCOUNT(address_query['records'][0]['Name'], proj_name_list[0], proj_name_list[1])
    email_recipient_account.dp = p_down
    email_recipient_account.dpSTAT = p_down_stat
    email_recipient_account.pp = p_permit
    email_recipient_account.ppSTAT = p_permit_stat
    email_recipient_account.fp = p_final
    email_recipient_account.fpSTAT = p_final_stat
    duepayment = email_recipient_account.getDuePayment()
    next_payment = email_recipient_account.getnextpayment()
    locale.setlocale(locale.LC_ALL,'')
    next_payment = locale.currency(next_payment)
    logoImage_cid = make_msgid()
    bg1Image_cid = make_msgid()
    facebook_cid = make_msgid()
    twitter_cid = make_msgid()
    ig_cid = make_msgid()
    html = render_template('emailtemplate1.html', name = address_query['records'][0]['Name'], chargeAmount = next_payment, duePayment = duepayment, payment_link = email_link, address = address, logoImage_cid = logoImage_cid[1:-1], bg1Image_cid = bg1Image_cid[1:-1], facebook_cid = facebook_cid[1:-1]) #, twitter_cid = twitter_cid[1:-1], ig_cid = ig_cid[1:-1])
    msg = EmailMessage()
    msg['Subject'] = 'Pay Certasun'
    msg['From'] = mail_settings['MAIL_USERNAME']
    msg['To'] = "nathan@certasun.com"
    msg.preamble = "TESTING EMAIL WiTHH IMAGEWS"
    msg.set_content("")
    msg.add_alternative(html, subtype = 'html')
    with open('static/img/CertasunLogo.png', 'rb') as fp:
        msg.get_payload()[1].add_related(fp.read(), 'image','png',cid=logoImage_cid)
    with open('static/img/bg1.png', 'rb') as fp:
        msg.get_payload()[1].add_related(fp.read(), 'image', 'png', cid = bg1Image_cid)
    with open('static/img/free_ico_facebook.jpg', 'rb') as fp:
        msg.get_payload()[1].add_related(fp.read(), 'image', 'jpg', cid = facebook_cid)
    with open('outgoing.msg', 'wb') as f:
        f.write(bytes(msg))
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(mail_settings['MAIL_USERNAME'],mail_settings['MAIL_PASSWORD'])
    smtp.sendmail(mail_settings['MAIL_USERNAME'], "nathan@certasun.com", msg.as_string())
    smtp.quit()
    return '', 200





if __name__ == '__main__':
    application.run(debug=True)
