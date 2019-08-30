from flask import Flask
from flask_mail import Mail
import os
import pprint
import stripe
application = Flask(__name__)
application.config['SECRET_KEY'] = "5791628bb0b13ce0c676dfde280ba245"
mail_settings = {
    "MAIL_SERVER" : 'smtp.gmail.com',
    "MAIL_PORT" : 587,
    "MAIL_USE_TLS" : True,
    "MAIL_USERNAME" : 'wayno5650@gmail.com',
    "MAIL_PASSWORD" : 'Cush5656'
}
application.config.update(mail_settings)
mail = Mail(application)
mail.init_app(application)
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
pp = pprint.PrettyPrinter(indent=2)
stripe.api_key = 'sk_test_YfkekeTtUjhcaJEccJojqD6q'
app_settings ={
'DWOLLA_SECRET' : "hgSkU7DT6g0eOOdQAx9uDcxpofe52AdM3dzRnEMYUeWMA6awYn",
'DWOLLA_KEY' : 'MV2YxoL4xaazgVJk1bWpQgUeR6q0kCxg5lnipDL7YoJZdw8V0J',
'STRIPE_API_KEY' : stripe.api_key,
'PLAID_CLIENT_ID' : '5d07c2f19585840015a41676',
'PLAID_SECRET' : '3554c62d5732888c8099296d93cdfb',
'PLAID_SECRET_SAND' : '2ceef8e0abfc857bb801f7dffd06a9',
'PLAID_PUBLIC_KEY' : '89066d105257beb46bc1873e92467e',
'PLAID_BALANCE' : 10000,
'PLAID_ENV' : PLAID_ENV,
'DWOLLA_ACCOUNT_FUNDING_SOOURCE_ID' : '94e5a2f5-0bb3-4cf6-9e32-8081be3040c5',
'SF-USER' : 'nwayn@certasun.com',
'SF-PASS' : 'Meerkat3250',
'SF-TOKEN' : 'LXaurDjGHUkmaAtU4fHwySPL',
'DOWN_PAYMENT_CONST' : 'Down Payment',
'PERMIT_PAYMENT_CONST' : 'Permit Payment',
'FINAL_PAYMENT_CONST' : "Final Payment",
'DUE_STATUS' : 'Due',
'NOT_DUE_STATUS' : 'Not Due',
'IN_FLIGHT_STATUS' : 'In Flight',
'RECEIVED_STATUS' : 'Received',
'N/A_STATUS' : 'N/A',
'GMAIL_ADDRESS' : 'wayno5650@gmail.com',
'GMAIL_PASSWORD' : 'Cush5656',
'OUTLOOK_ADDRESS' : "nathan@certasun.com",
'SMTP_USERNAME' : "AKIATZ6Y4YOTZWCBF56T",
'SMTP_PASSWORD' : "BItZz8Wcas9aFuZcZnRh8IVRlLXpKdl4ardA8UXOsCmr",
'AWS_SES_ENDPOINT' : "email-smtp.us-east-1.amazonaws.com",
'DWOLLA_UNVERIFIED_LIMIT' : 4000,
'DWOLLA_VERIFIED_LIMIT' : 30000,
}
from DwollaApplication1 import routes
