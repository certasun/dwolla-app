from flask import Flask, session, render_template, request, redirect, url_for
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
from wtforms import StringField, SubmitField
import json
from flask_mail import Mail, Message
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
application = Flask(__name__)
mail_settings = {
    "MAIL_SERVER" : 'smtp.gmail.com',
    "MAIL_PORT" : 465,
    "MAIL_USE_TLS" : False,
    "MAIL_USE_TLS" : True,
    "MAIL_USERNAME" : 'wayno5650@gmail.com',
    "MAIL_PASSWORD" : 'Cush5656'
}
application.config.update(mail_settings)
mail = Mail(application)
DWOLLA_KEY = 'iS0W3WhluuWJxkMUiinjKZxiL95s0gkY0QUqqlSDclFokjnNi5'
DWOLLA_SECRET = 'Ma6b5vHZG5egY4jWo7JkJHhqUgxMnc2WwV0ROINtuEJ9Q6J3pj'
ACCESS_SECRET_KEY = 'tc07v1nNDGw6SOWO1xtx0pOSDQpaxYmx1Zd6j2A'
application.config['SECRET_KEY'] = '5791628bb0b13ce0c67dfde280ba245'
pub_key = 'pk_test_5PPWDFa356A5VTg8k3qXKIQE'
secret_key = 'sk_test_YfkekeTtUjhcaJEccJojqD6q'
stripe.api_key = secret_key
PLAID_CLIENT_ID='5d07c2f19585840015a41676'
PLAID_SECRET='3554c62d5732888c8099296d93cdfb'
PLAID_SECRET_SAND = '2ceef8e0abfc857bb801f7dffd06a9'
PLAID_PUBLIC_KEY='89066d105257beb46bc1873e92467e'
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')
client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET_SAND, public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')
dwolla_client = dwollav2.Client( key = DWOLLA_KEY, secret = DWOLLA_SECRET, environment = 'sandbox')
DWOLLA_ACCOUNT_FUNDING_SOURCE_ID =  '94e5a2f5-0bb3-4cf6-9e32-8081be3040c5'
sf_user = 'nwayn@certasun.com'
sf_pass = 'Meerkat3250'
sf_consumer_key = '3MVG9vrJTfRxlfl7JrAPVnSBJscooRaBSEHaV0RU0Nh26ID0am9ZyHz5wQ99NhDv_uBXnw9lUy6rsXLa0byTU'
sf_consumerr_secret = 'F851D4F3EAA855D44D1A0B3FC543053B26FB333A212A444EDF13528CF755854D'
sf_token = 'LXaurDjGHUkmaAtU4fHwySPL'
sf_token_updatedsan = 'MRkY20HRIBUTBbTM5U58eezT'
sf_token_prod = 'Diyzed7ZdrCePEwAEoDeRulVu'
pp = pprint.PrettyPrinter(indent=1)
sf = Salesforce(sf_user +".updatedsan", sf_pass, sf_token_updatedsan, domain = 'test')
sf_prod = Salesforce(sf_user, sf_pass, sf_token_prod)
DOWN_PAYMENT_CONST = "Down Payment"
PERMIT_PAYMENT_CONST = "Permit Payment"
FINAL_PAYMENT_CONST = "Final Payment"
DUE_STATUS = "Due"
NOT_DUE_STATUS = "Not Due"
letter = 't'
query = sf.query("select Id from project__c where name LIKE '%"+letter+"%'")
pp.pprint(query)
