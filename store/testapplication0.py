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
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
webdriverpath = os.path.join('\\Users', 'NathanWayne', 'Desktop', 'TestCSVPY', 'chromedriver.exe')
browser = webdriver.Chrome(executable_path = 'chromedriver.exe')
wait = WebDriverWait(browser, 30)

application = Flask(__name__)
mail_settings = {
    "MAIL_SERVER" : 'smtp.gmail.com',
    "MAIL_PORT" : 465,
    "MAIL_USE_TLS" : False,
    "MAIL_USE_TLS" : True,
    "MAIL_USERNAME" : 'wayno5650@gmail.com',
    "MAIL_PASSWORD" : 'Cush5656'
}
F_key = Fernet.generate_key()
shakey = b'hFII8Cjt5yJZZDhginbe0tleSP7hT1GNM8k3-LkhI_c='
cipher_suite = Fernet(shakey)
application.config.update(mail_settings)
mail = Mail(application)
DWOLLA_KEY = 'eddj4apa27lHlL4uMuwkkGsGiQ9IHH9MT3LrMvvvDhq1lLJwv1'
DWOLLA_SECRET = 'qR7smUqNapsNLeAv3UNyVB1kpPhVnZBQEUk42fHBeDJejTHiIa'
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
sf_token = 'gmrlB5Pl79Nykd1UP4rl3tOC'
pp = pprint.PrettyPrinter(indent=4)
sf = Salesforce(sf_user +".plaidtest", sf_pass, sf_token, domain = 'test')
DOWN_PAYMENT_CONST = "Down Payment"
PERMIT_PAYMENT_CONST = "Permit Payment"
FINAL_PAYMENT_CONST = "Final Payment"
DUE_STATUS = "Due"
NOT_DUE_STATUS = "Not Due"
app_token = dwolla_client.Auth.client()
gmailaddress = "wayno5650@gmail.com"
gmailpassword = "Cush5656"
mailto = "nathan@certasun.com"
DWOLLA_UNVERIFIED_LIMIT = 50
DWOLLA_VERIFIED_LIMIT = 30000
email_start = 'officialtest4'
emailext = "@test.com"
emailurl = email_start + "%40test.com"
#def test_new_customer_create_and_update():
proj_ID = sf.query("select ID from project__c where Name = 'Official Test - 7524 Inverway'");
contactID = sf.query("select ID from contact where Name = 'Official Test'")
pp.pprint(proj_ID['records'][0]['Id'])
proj_ID = proj_ID['records'][0]['Id']
contactID = contactID['records'][0]['Id']
print(contactID)
sf.project__c.update(proj_ID, {'Cash_Down_Pmt_Status__c': 'Due'})
sf.project__c.update(proj_ID, {'Cash_Permit_Pmt_Status__c': 'Due'})
sf.project__c.update(proj_ID, {'Cash_Final_Pmt_Status__c': 'Due'})
sf.contact.update(contactID, {'email': email_start + emailext})
browser.get('http://localhost:5000/linkwithname/'+emailurl)
plaid_link_button = browser.find_element_by_xpath('//*[@id="linkButton"]')
plaid_link_button.click()
browser.switchTo.frame(1);
element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="plaid-link-container"]/div/div[1]/div/div/div[2]/div[2]/div/button')))
agree_button = browser.find_element_by_xpath('//*[@id="plaid-link-container"]/div/div[1]/div/div/div[2]/div[2]/div/button')
agree_button.click()
element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="plaid-link-container"]/div/div[1]/div/div/div[2]/div[2]/div/li[1]')))
chase_button = browser.find_element_by_xpath('//*[@id="plaid-link-container"]/div/div[1]/div/div/div[2]/div[2]/div/li[1]')
chase_button.click()
plaid_username_field = browser.find_element_by_xpath('//*[@id="username"]')
plaid_username_field.send_keys('user_good')
plaid_password_field = browser.find_element_by_xpath('//*[@id="password"]')
plaid_password_field.send_keys('pass_good')
user_pass_submit = browwser.find_element_by_xpath('//*[@id="plaid-link-container"]/div/div[1]/div/div[2]/div[3]/form/button')
user_pass_submit.click()



browser.get('http//localhost:5000/linkwithname/'+emailurl)
SSN = browser.find_element_by_xpath('//*[@id="L4S"]')
SSN.send_keys('1111')
DOB = browser.find_element_by_xpath('//*[@id="DOB"]')
DOB.send_keys('1997-12-12')
submit_verification = browser.find_element_by_xpath('//*[@id="validate_button"]')
submit_verification.click()
element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="linkButton"]')))
plaid_link_button.click()
element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="plaid-link-container"]/div/div[1]/div/div/div[2]/div[2]/div/button')))
agree_button.click()
element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="plaid-link-container"]/div/div[1]/div/div/div[2]/div[2]/div/li[1]')))
chase_button.click()
plaid_username_field.send_keys('user_good')
plaid_password_field.send_keys('pass_good')
user_pass_submit.click()
