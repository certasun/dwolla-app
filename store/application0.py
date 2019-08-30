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
application = Flask(__name__)
mail_settings = {
    "MAIL_SERVER" : 'smtp.gmail.com',
    "MAIL_PORT" : 587,
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
mail.init_app(application)
DWOLLA_SECRET = "qR7smUqNapsNLeAv3UNyVB1kpPhVnZBQEUk42fHBeDJejTHiIa"
DWOLLA_KEY = 'eddj4apa27lHlL4uMuwkkGsGiQ9IHH9MT3LrMvvvDhq1lLJwv1'
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
DWOLLA_UNVERIFIED_LIMIT = 500
DWOLLA_VERIFIED_LIMIT = 30000
PLAID_BALANCE = 100000
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

@application.route('/emailnew', methods = ['GET', 'POST'])
def templateEmailnew():
    email = "officialTest8@test.com"
    email_link = "http://localhost:5000/linkwithid/a0Yg0000006ENn2EAG"
    id = "a0Yg0000006ENn2EAG"
    templateLoader = jinja2.FileSystemLoader(searchpath = "/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    projID = get_proj_from_sf(email)
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
    #with open('static/img/free_ico_twitter.jpg', 'rb') as fp:
    #    msg.get_payload()[1].add_related(fp.read(), 'image', 'jpg', cid = twitter_cid)
    #with open('static/img/free_ico_instagram.jpg', 'rb') as fp:
    #    msg.get_payload()[1].add_related(fp.read(), 'image', 'jpg', cid = ig_cid)
    with open('outgoing.msg', 'wb') as f:
        f.write(bytes(msg))
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(mail_settings['MAIL_USERNAME'],mail_settings['MAIL_PASSWORD'])
    smtp.sendmail(mail_settings['MAIL_USERNAME'], "nathan@certasun.com", msg.as_string())
    smtp.quit()
    return '', 200


@application.route('/', methods = ['GET', "POST"])
@application.route('/landingpagelayout', methods = ['GET', 'POST'])
def landing_page():
    #session.clear()
    form = nameForm()
    if form.validate_on_submit():
        email = form.name.data
        query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
        if query['records'][0]['Projects__r'] == None:
            return redirect(url_for('invalidEmail'))
        elif query['records'][0]['Projects__r']['totalSize'] > 1:
            session['email'] = email
            return redirect(url_for('multipleRecords', email = email, query = query))
        elif query['records'][0]['Projects__r']['totalSize'] == 1:
            session['email'] = email
            return redirect(url_for('passObjID', id = query['records'][0]['Projects__r']['records'][0]['id']))
        return redirect(url_for('passObj', email = email))
    return render_template('index3.html', form = form)

#SET WEB HOOK SUBSCRIPTION FROM DWOLLA TO GIVEN URL
@application.route('/setWebHook')
def setWebHook():
     webhook_request_body = {
       'url' : 'https://enq2v93k6nzo.x.pipedream.net',
       'secret' : 'This is from Dwolla'
     }
     subscription = app_token.post('webhook-subscriptions', webhook_request_body)
     return "WEBHOOK SET"
#GET RID OF ALL DWOLLA WEBHOOK SUBSCRIPTIONS
@application.route('/killwebhooks')
def killWebHooks():
    webhook_subs = app_token.get('webhook-subscriptions')
    for i in range(len(webhook_subs.body['_embedded']['webhook-subscriptions'])):
        app_token.delete(webhook_subs.body['_embedded']['webhook-subscriptions'][i]['_links']['self']['href'])
    return "DONE"
#CHECKS TRANSFER STATIS AND REDIRECTS TO CORRECT PAGE BASED ON TRANSFER STATUS
@application.route('/thanks')
def thanks():
        #return render_template('newEnd.html', reason = session['transfer_status'])
    #IF WHILE CREATING CUSTOMER THE CUSTOMER WASNT VERIFIED THIS WILL SHOW CUSTOMER THAT PAYMENT IS
    #PENDING AND TRANSFER WILL NEED TO BE DONE MANUALLY VIA CHASE
    if session['transfer_status'] == 'unverified_manual_needed':
        return render_template('newEnd.html', big_message = "Thank You", reason = "Your Payment is Now Pending")
    #TRANSFER WAS SUCCESSFULLY INITIATED THROUGH DWOLLA AND IS NOW PENDING
    #SALEFORCE WILL BE UPDATED TO SHOW PAYMENT IS IN FLIGHT
    if session['transfer_status'] == 'pending':
        if session['passAccount']:
            if session['passAccount']['duePayment'] == DOWN_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Down_Pmt_Status__c': 'In Flight'})
            if session['passAccount']['duePayment'] == PERMIT_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Permit_Pmt_Status__c': 'In Flight'})
            if session['passAccount']['duePayment'] == FINAL_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Final_Pmt_Status__c': 'In Flight'})
            return render_template('newEnd.html', big_message = "Thank You", reason ="Your payment is now pending")
    if session['transfer_status'] == 'stripe_paid_true':
        if session['passAccount']:
            if session['passAccount']['duePayment'] == DOWN_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Down_Pmt_Status__c': 'In Flight'})
            if session['passAccount']['duePayment'] == PERMIT_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Permit_Pmt_Status__c': 'In Flight'})
            if session['passAccount']['duePayment'] == FINAL_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Final_Pmt_Status__c': 'In Flight'})
            return render_template('newEnd.html', big_message = "Thank You")
            #TRANSFER STATUS WASNT
    elif session['transfer_status'] != 'pending' and session['transfer_status'] != 'unverified_manual_needed':
        return render_template('newEnd.html',big_message = "Error", reason = "Insufficient Funds")

@application.route('/failed')
def failed():
    return render_template('failed.html')
#START PAGE TAKES EMAIL FROM FORM AND PASSES IT ON
@application.route('/testNewStart', methods = ['GET', 'POST'])
def newStart():
    thisform = nameForm()
    if thisform.validate_on_submit():
        form_email = thisform.name.data
        return redirect(url_for('passObj', email = form_email))
    return render_template('startPage.html', form = thisform)
#CAN BE ACCESSED EITHER FROM A LINK OR FROM THE startPage
#FIRST WILL CLEAR THE SESSION FOR DATA INTEGRITY
#WILL THEN GET THE CONTACT NAME FROM SALESFORCE BY USING THE EMAIL PROVIDED
@application.route('/linkwithname/<email>', methods = ['GET', "POST"])
def passObj(email):
    session.clear()
    form = verificationForm()
    session['email'] = email
    #query = sf.query("select Name, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "'")
    #DEPRACATED FOR MORE ACCURATE BELOW
    #contact = sf.query("select Name from Contact where Email LIKE'%" + email +"%'")
    query2 = sf.query("select Account.Name from contact where email = '" + email +"'")
    #IF THERE WASNT A CONTACT WITH THAT EMAIL YOU WILL BE REDIRECTED OTHERWISE THE NAME IS TAKEN FROM THE RECORD
    if query2['totalSize'] > 0:
        A_NAME = query2['records'][0]['Account']['Name']
        session['name'] = A_NAME
        A_NAME_LIST = A_NAME.split()
    else:
        return redirect(url_for('InvalidName'))
    #create an account object
    passAccount = runQueries(session['name'], A_NAME_LIST[0], A_NAME_LIST[1])
    #there wasnt a sf_project for the given sf_contact
    if passAccount == 1:
        return redirect(url_for('InvalidName'))
    #there was more than 1 sf_project for the given sf_contact so they must choose which one they want
    if passAccount == 2:
        return redirect(url_for('multipleRecords', email = email))
    session['passAccount'] = passAccount.toJSON()
    #setting error codes to default settings
    session['Validation_Error'] = 'No Error'
    session['transfer_status'] = "BLANK"
    #query dwolla for a customer wiht the email
    cus = app_token.get('customers', search = email)
    #customer doesnt exist he must be created
    if cus.body['total'] == 0:
        #set pre verified to zero because he cant be preverified if he doesnt yet exist
        pre_verified = 0
    #customer does exist and has already been verified
    elif cus.body['_embedded']['customers'][0]['status'] == 'verified':
        pre_verified = 1
    else:
        #customer has been created but has not been verified
        pre_verified = 0
    #make sure Account OBJ exists
    if passAccount:
        #get the value for the charge
        send_payment = passAccount.getnextpayment()
        session['send_payment'] = send_payment
        #get additional data from sf to show on page
        name_address = sf.query("select name, MailingAddress, email from contact where email LIKE '%" +email+ "%'")
        pp.pprint(name_address)
        a_city = name_address['records'][0]['MailingAddress']['city']
        a_state = name_address['records'][0]['MailingAddress']['state']
        a_street = name_address['records'][0]['MailingAddress']['street']
        a_zip = name_address['records'][0]['MailingAddress']['postalCode']
        location = {
        'city' : a_city,
        'state' : a_state,
        'street' : a_street,
        'zip' : a_zip
        }
        return render_template('ach-credit.html', accountobj = passAccount, payment = send_payment, email = email, location = location, pre_verified = pre_verified)
        #return render_template('testCSS.html', pre_verified = pre_verified, pub_key = pub_key,
         #account_name = passAccount.name, payment =send_payment, accountobj=passAccount)
    else:
         return redirect(url_for('newStart'))

@application.route('/linkwithid/<id>', methods = ['GET', "POST"])
def passObjID(id):
    form = verificationForm()
    session['proj_ID'] = id
    email = session['email']
    #query = sf.query("select Name, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "'")
    #DEPRACATED FOR MORE ACCURATE BELOW
    #contact = sf.query("select Name from Contact where Email LIKE'%" + email +"%'")
    query2 = sf.query("select Account.Name from contact where email = '" + email +"'")
    pp.pprint(query2)
    A_NAME = query2['records'][0]['Account']['Name']
    session['name'] = A_NAME
    A_NAME_LIST = A_NAME.split()
    #IF THERE WASNT A CONTACT WITH THAT EMAIL YOU WILL BE REDIRECTED OTHERWISE THE NAME IS TAKEN FROM THE RECORD
    #create an account object
    passAccount = runQueriesID(session['name'], A_NAME_LIST[0], A_NAME_LIST[1], id)
    #there wasnt a sf_project for the given sf_contact
    #there was more than 1 sf_project for the given sf_contact so they must choose which one they want
    session['passAccount'] = passAccount.toJSON()
    #setting error codes to default settings
    session['Validation_Error'] = 'No Error'
    session['transfer_status'] = "BLANK"
    #query dwolla for a customer wiht the email
    cus = app_token.get('customers', search = email)
    #customer doesnt exist he must be created
    if cus.body['total'] == 0:
        #set pre verified to zero because he cant be preverified if he doesnt yet exist
        pre_verified = 0
    #customer does exist and has already been verified
    elif cus.body['_embedded']['customers'][0]['status'] == 'verified':
        pre_verified = 1
    else:
        #customer has been created but has not been verified
        pre_verified = 0
    #make sure Account OBJ exists
    if passAccount:
        #get the value for the charge
        send_payment = passAccount.getnextpayment()
        session['send_payment'] = send_payment
        #get additional data from sf to show on page
        name_address = sf.query("select name, MailingAddress, email from contact where email LIKE '%" +email+ "%'")
        pp.pprint(name_address)
        a_city = name_address['records'][0]['MailingAddress']['city']
        a_state = name_address['records'][0]['MailingAddress']['state']
        a_street = name_address['records'][0]['MailingAddress']['street']
        a_zip = name_address['records'][0]['MailingAddress']['postalCode']
        location = {
        'city' : a_city,
        'state' : a_state,
        'street' : a_street,
        'zip' : a_zip
        }
        return render_template('ach-credit.html', accountobj = passAccount, payment = send_payment, email = email, location = location, pre_verified = pre_verified)
        #return render_template('testCSS.html', pre_verified = pre_verified, pub_key = pub_key,
         #account_name = passAccount.name, payment =send_payment, accountobj=passAccount)
    else:
         return redirect(url_for('newStart'))


#stripe credit card charge implementation
@application.route('/charge', methods = ['GET', 'POST'])
def credit_handler():
    #get the stripe token
    token = request.form['stripeToken']
    #create a charge with the data from the form
    charge = stripe.Charge.create(
        amount=request.form['amount'],
        currency='usd',
        description=request.form['description'],
        source=token,
        metadata = {'email': request.form['email'],
                    'payType':request.form['payType'],
                    'proj_id' : request.form['proj_ID']}
    )
    #get the project ID from sf in order to update the payment status if the charge went through
    if charge['paid'] == True:
        proj_ID = charge['metadata']['proj_iD']
        change_payment_status_in_sf(request.form['payType'], proj_ID, "In Flight")
        session['transfer_status'] = 'stripe_paid_true'
    return redirect(url_for('thanks'))


@application.route('/handle_validation_form', methods = ["GET", "POST"])
def handle_validation_form():
    SSN = request.form['s']
    DOB = request.form['d']
    session['L4S'] = SSN
    session['DOB'] = DOB
    return '', 200

#method to create a Account obj from sf data
def runQueries(name, fname, lname):
    #input is account name related to the contact email given in original form that account name is used to find the correct project and set all of the data accordingly
    Account_Name_query = sf.query("select Name, (select Name from projects__r) from account where name = '"+ name +"'")
    #query = sf.query("select Name, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "'")
    #No projects exist
    pp.pprint(Account_Name_query)
    if Account_Name_query['records'][0]['Projects__r'] == None:
        return 1
        #No projecs exist
    if Account_Name_query['totalSize'] == 0:
        return 1
    #multiple projects exist
    if Account_Name_query['records'][0]['Projects__r']['totalSize'] > 1:
        return 2
    Account_Name = Account_Name_query['records'][0]['Projects__r']['records'][0]['Name']
    thisAccount = ACCOUNT(Account_Name, fname, lname)
    query = sf.query("select Name, (select id, Cash_Down_pmt__c, Cash_Down_Pmt_Status__c, Permit_pmt__C, Cash_Permit_Pmt_Status__c, Cash_final_Pmt__c, Cash_final_pmt_status__c from projects__r) from Account where Name = '" + name + "'")
    #query payment details and set object accordingly
    thisAccount.ID = query['records'][0]['Projects__r']['records'][0]['Id']
    thisAccount.dp = query['records'][0]['Projects__r']['records'][0]['Cash_Down_Pmt__c']
    thisAccount.dpSTAT = query['records'][0]['Projects__r']['records'][0]['Cash_Down_Pmt_Status__c']
    thisAccount.pp = query['records'][0]['Projects__r']['records'][0]['Permit_Pmt__c']
    thisAccount.ppSTAT = query['records'][0]['Projects__r']['records'][0]['Cash_Permit_Pmt_Status__c']
    thisAccount.fp = query['records'][0]['Projects__r']['records'][0]['Cash_Final_Pmt__c']
    thisAccount.fpSTAT = query['records'][0]['Projects__r']['records'][0]['Cash_Final_Pmt_Status__c']
    #want to find which of the three possible payments needs to be paid next and set it as the next duepayment
    if thisAccount.dpSTAT == DUE_STATUS or thisAccount.dpSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = DOWN_PAYMENT_CONST
        return thisAccount
    elif thisAccount.ppSTAT == DUE_STATUS or thisAccount.ppSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = PERMIT_PAYMENT_CONST
        return thisAccount
    elif thisAccount.fpSTAT == DUE_STATUS or thisAccount.fpSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = FINAL_PAYMENT_CONST
        return thisAccount
    else:
        thisAccount.duePayment = "NA"
    return thisAccount

def runQueriesID(name, fname, lname, id):
    #input is account name related to the contact email given in original form that account name is used to find the correct project and set all of the data accordingly
    Account_Name_query = sf.query("select Name, (select Name from projects__r) from account where name = '"+ name +"'")
    #query = sf.query("select Name, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "'")
    #No projects exist
    Account_Name = Account_Name_query['records'][0]['Projects__r']['records'][0]['Name']
    thisAccount = ACCOUNT(Account_Name, fname, lname)
    query = sf.query("select Name, id, Cash_Down_pmt__c, Cash_Down_Pmt_Status__c, Permit_pmt__C, Cash_Permit_Pmt_Status__c, Cash_final_Pmt__c, Cash_final_pmt_status__c from Project__c where id = '" + id + "'")
    #query payment details and set object accordingly
    pp.pprint(query)
    thisAccount.ID = query['records'][0]['Id']
    thisAccount.dp = query['records'][0]['Cash_Down_Pmt__c']
    thisAccount.dpSTAT = query['records'][0]['Cash_Down_Pmt_Status__c']
    thisAccount.pp = query['records'][0]['Permit_Pmt__c']
    thisAccount.ppSTAT = query['records'][0]['Cash_Permit_Pmt_Status__c']
    thisAccount.fp = query['records'][0]['Cash_Final_Pmt__c']
    thisAccount.fpSTAT = query['records'][0]['Cash_Final_Pmt_Status__c']
    #want to find which of the three possible payments needs to be paid next and set it as the next duepayment
    if thisAccount.dpSTAT == DUE_STATUS or thisAccount.dpSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = DOWN_PAYMENT_CONST
        return thisAccount
    elif thisAccount.ppSTAT == DUE_STATUS or thisAccount.ppSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = PERMIT_PAYMENT_CONST
        return thisAccount
    elif thisAccount.fpSTAT == DUE_STATUS or thisAccount.fpSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = FINAL_PAYMENT_CONST
        return thisAccount
    else:
        thisAccount.duePayment = "NA"
    return thisAccount


#invalidEmail was given ask for email again
@application.route('/InvalidName', methods = ['GET', 'POST'])
def InvalidName():
    thisform = nameForm()
    if thisform.validate_on_submit():
        form_email = thisform.name.data
        return redirect(url_for('passObj', email = form_email))
    return render_template('Invalid.html', form = thisform)


#more than one project exists for the given contact customer must choose which project they would like to pay for
@application.route('/multipleRecords/<email>')
def multipleRecords(email):
    query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
    accountList = list()
    pp.pprint(query)
    for i in range(query['records'][0]['Projects__r']['totalSize']):
        account_dict = {'Name':query['records'][0]['Projects__r']['records'][i]['Name'], 'ID': query['records'][0]['Projects__r']['records'][i]['Id']}
        accountList.append(account_dict)
    return render_template('multipleRecordsNew.html', accounts = accountList)
#original Dwolla verification failed additional infor can be taken from this form in order to attempt to retry the dwolla customer verification
@application.route('/retrycreateverifiedcustomer', methods = ['GET', 'POST'])
def retrycreateverifiedcustomer():
    form = retryForm()
    if form.validate_on_submit():
        retry_request_body = {
        'firstName' : form.firstName.data,
        'lastName' : form.lastName.data,
        'email' : form.retry_email.data,
        'type' : 'personal',
        'address1' : form.street_address.data,
        'city' : form.city.data,
        'state' : form.state_Code.data,
        'postalCode' : form.zip.data,
        'dateOfBirth' : form.DOB.data,
        'ssn' : form.SSN.data
        }
        customer_url = create_verified_dwolla_customer(retry_request_body)
    return render_template('retrycustomerverification.html', form = form)

#DEPRACATED
#create a json to be sent in a request to dwolla in order to create a customer
def createVerifiedCustomerRequestBody():
    identity_response = client.Identity.get(session['access_token'])
    for i in range(len (identity_response['accounts'])):
        if identity_response['accounts'][i]['account_id'] == session['ACCOUNT_ID']:
            identity_index = i
    nameslist = session['name'].split()
    email = identity_response['accounts'][identity_index]['owners'][0]['emails'][1]['data']
    street = identity_response['accounts'][identity_index]['owners'][0]['addresses'][0]['data']['street']
    city = identity_response['accounts'][identity_index]['owners'][0]['addresses'][0]['data']['city']
    state = identity_response['accounts'][identity_index]['owners'][0]['addresses'][0]['data']['region']
    zip = identity_response['accounts'][identity_index]['owners'][0]['addresses'][0]['data']['postal_code']
    customer_create_request_body ={
    'firstName': nameslist[0],
    'lastName': nameslist[1],
    'email': email,
    'type':'personal',
    'address1': street,
    'city': city,
    'state': state,
    'postalCode': zip,
    'dateOfBirth': '1997-06-04',#TEST
    'ssn': '1111'#TEST
    }
    return customer_create_request_body

#create a json to be sent in the request to dwolla for a customer whose current charge that is under 5k because of this the custoemr doesnt need to be veriffied at this time
def create_unverified_dwolla_request_body():
    name_address = sf.query("select name, email from contact where email LIKE '%" + session['email'] + "%'")
    if name_address['totalSize'] == 1:
        full_name_from_sf = name_address['records'][0]['Name']
        full_name_list = full_name_from_sf.split()
        first_name_from_sf = full_name_list[0]
        last_name_from_sf = full_name_list[1]
        email_from_sf = name_address['records'][0]['Email']
        customer_create_request_body ={
        'firstName':first_name_from_sf,
        'lastName': last_name_from_sf,
        'email': email_from_sf,
        }
        return customer_create_request_body
    else:
        alert("Something Went Wrong")
        return redirect(url_for('newStart'))


def create_verified_dwolla_customer():
    #check if customer exists in dwolla
    customer_response = app_token.get('customers', search = session['email'])
    #if charge is above our limit for even a verified customer we encrypt user data and store to be entered manually
    if session['passAccount']['chargeAmount'] > DWOLLA_VERIFIED_LIMIT:
        customer_request_body = create_unverified_dwolla_request_body()
        customer_not_verified_encode_upload_send(customer_request_body)
        session['verification_status'] = 'unverified_manual_needed'
        session['create_customer_status'] = 'NA'
        return
    #customer already exists in dowlla
    elif customer_response.body['total'] > (0):
        customer_url = 'https://api-sandbox.dwolla.com/customers/' + customer_response.body['_embedded']['customers'][0]['id']
        session['create_customer_status'] = 'Already In System'
        #custoemr is verified
        if customer_response.body['_embedded']['customers'][0]['status'] == 'verified':
            session['verification_status'] = 'verified'
        #customer is unverified but already create and must be updated to verified because charge amount is above unverified limit
        if session['passAccount']['chargeAmount'] > DWOLLA_UNVERIFIED_LIMIT and customer_response.body['_embedded']['customers'][0]['status'] == 'unverified':
            #create the json to be sent in the request
            customer_create_request_body = create_verified_request_body_from_SF()
            update = app_token.post(customer_url, customer_create_request_body)
            #customer update failed encrypt data and store for manual entry
            if update.body['status'] == 'unverified':
                customer_not_verified_encode_upload_send(customer_create_request_body)
                session['verification_status'] = 'unverified_manual_needed'
                return
    #custoemr does not alreadt exist
    else:
        #customer doesnt exist and charge is less than 5k so no need to verify
        if session['passAccount']['chargeAmount'] < DWOLLA_UNVERIFIED_LIMIT:
                customer_create_request_body =create_unverified_dwolla_request_body()
        #customer doesnt exist and charge is more than 5k so customer must be verified
        else:
                customer_create_request_body = create_verified_request_body_from_SF()
        try:
            #post request to dwolla to create the custoemr
            customer = app_token.post('customers', customer_create_request_body)
            customer_url = customer.headers['location']
            session['create_customer_status'] = 'Passed'
        except Exception as e:
            #print(e)
            session['create_customer_status'] = 'Failed'
            return
    #use customer url returned by request to get customer info
    get_customer = app_token.get(customer_url)
    #customer must be verified
    if session['passAccount']['chargeAmount'] >= DWOLLA_UNVERIFIED_LIMIT:
        #verification attempt failed data encrypted and stored for manual entry
        if get_customer.body['status'] == 'unverified' and 'update' not in locals():
            customer_not_verified_encode_upload_send(customer_create_request_body)
            session['verification_status'] = 'unverified_manual_needed'
        #customer verification was successful
        elif get_customer.body['status'] == 'verified':
            session['verification_status'] = 'verified'
    #customer doesnt need to be verified
    elif session['passAccount']['chargeAmount'] < DWOLLA_UNVERIFIED_LIMIT:
        #customer isnt verified but its ok dwolla can still handle transaction because the charge is under 5k
        if get_customer.body['status'] == 'unverified':
            session['verification_status'] = 'unverified_manual_not_needed'
    return customer_url

#customer verification was unsuccessful data is then encrypted and store for manual entry
def customer_not_verified_encode_upload_send(customer_create_request_body):
    auth_response = client.Auth.get(session['access_token'])
    for i in range(len(auth_response['numbers']['ach'])):
        if auth_response['numbers']['ach'][i]['account_id'] == session['ACCOUNT_ID']:
            account_num = auth_response['numbers']['ach'][i]['account']
            routing_num = auth_response['numbers']['ach'][i]['routing']
            note_str = "account: " + account_num + " routing: " + routing_num
            proj_ID =  sf.query("select id from project__c where Name LIKE '%" + customer_create_request_body['lastName'] + "%'")
            proj_ID = proj_ID['records'][0]['Id']
            note_str_bytes = str.encode(note_str)
            cipher_text_bytes = cipher_suite.encrypt(note_str_bytes)
            cipher_text = str(cipher_text_bytes)
            sf.project__c.update(proj_ID, {'Payment_Notes__c': cipher_text})
            email_sender("nathan@certasun.com", "verification fail", cipher_text, 0)
    return

#decodes data
@application.route('/decode', methods = ['GET', 'POST'])
def customer_not_verified_decode():
    form = decodeForm()
    if form.validate_on_submit():
        cipher_text = form.hash.data
        cipher_text_list = cipher_text.split("\'")
        decodable = cipher_text_list[1].encode()
        plain_text_bytes = cipher_suite.decrypt(decodable)
        plain_text = plain_text_bytes.decode()
        print(plain_text)
    return render_template('decode.html', form = form)

#creates the json to be sent to dwolla in order to create a verified custoemr with data taken from salesforce not plaid
@application.route('/create_verified_dwolla_customer_from_SF', methods = ['GET', 'POST'])
def create_verified_request_body_from_SF():
    name_address = sf.query("select name, MailingAddress, email from contact where email LIKE '%" + session['email'] + "%'")
    pp.pprint(name_address)
    if name_address['totalSize'] == 1:
        full_name_from_sf = name_address['records'][0]['Name']
        full_name_list = full_name_from_sf.split()
        first_name_from_sf = full_name_list[0]
        last_name_from_sf = full_name_list[1]
        email_from_sf = name_address['records'][0]['Email']
        street = name_address['records'][0]['MailingAddress']['street']
        city = name_address['records'][0]['MailingAddress']['city']
        state = name_address['records'][0]['MailingAddress']['stateCode']
        zip = name_address['records'][0]['MailingAddress']['postalCode']
        customer_create_request_body ={
        'firstName':first_name_from_sf,
        'lastName': last_name_from_sf,
        'email': email_from_sf,
        'type':'personal',
        'address1': street,
        'city': city,
        'state': state,
        'postalCode': zip,
        'dateOfBirth': session['DOB'],
        'ssn': session['L4S']
        }
        return customer_create_request_body
    else:
        alert("Something Went Wrong")
        return redirect(url_for('newStart'))

#create and attach a funding source to the given customer
def create_customer_funding_source(customer_url, request_body):
    #get the giiven customers funding sources
    current_customers_funding_sources = app_token.get('%s/funding-sources' % customer_url)
    #check if the funding source you wish to create is actually one that already exists
    for i in range(len(current_customers_funding_sources.body['_embedded']['funding-sources'])):
        if current_customers_funding_sources.body['_embedded']['funding-sources'][i]['name'] == request_body['name']:
            customer_funding_source_url = current_customers_funding_sources.body['_embedded']['funding-sources'][i]['_links']['self']['href']
            return customer_funding_source_url
    #funding source doesnt alreay exist
    try:
        #post request to dwolla to add a fundign source to the custoemr
        customer_funding_source = app_token.post('%s/funding-sources' % customer_url, request_body)
        customer_funding_source_url = customer_funding_source.headers['location']
    except Exception as e:
        session['transfer_status'] = 'Error linking to Bank Account'
        customer_funding_source_url = session['transfer_status']
    return customer_funding_source_url

#gets the certasuns account to deposit into
def getMasterAccountFundingSourceURL():
    root = app_token.get('/')
    account_url = root.body['_links']['account']['href']
    account_funding_source = app_token.get('%s/funding-sources' % account_url)
    account_funding_source_url = account_funding_source.body['_embedded']['funding-sources'][0]['_links']['self']['href']
    return account_funding_source_url

def createTransfer(transfer_request_body):
    try:
        #get balance from plaid
        balance_response = client.Accounts.balance.get(session['access_token'])
    except plaid.errors.PlaidError as e:
        session['transfer_status'] = "Balance Check Fail"
        return session['transfer_status']
    #match up to the account chosen account
    for i in range(len(balance_response['accounts'])):
        if balance_response['accounts'][i]['account_id'] == session['ACCOUNT_ID']:
            balance_index = i
            break
    #make sure that the custoemrs available balance according to plaid is more than the charge amount
    if  PLAID_BALANCE < session['passAccount']['chargeAmount']:#balance_response['accounts'][balance_index]['balances']['available'] < session['passAccount']['chargeAmount']:
        session['transfer_status'] = 'Insufficient Funds'
        return session['transfer_status']
    #balance is higher than charge
    else:
        try:
            #post request to dwoolla to initiate transfer, then get the transfer statuc
            transfer = app_token.post('transfers', transfer_request_body)
            transfer_url = transfer.headers['location']
            getTransfer = app_token.get(transfer_url)
            transfer_status = getTransfer.body['status']
            session['transfer_status'] = transfer_status
        except Exception as ex:
            session['Validation_Error'] = ex.body['_embedded']['errors'][0]['message']
            print(session['Validation_Error'])
            transfer_status = session['Validation_Error']
        return transfer_status

#called by PLAID lINK
def pending_Dwolla():
    #get the custoemr url by either retrieving the customer or creating a new one
    customer_url = create_verified_dwolla_customer()
    #creation of customer failed because of an exception sent back by dwolla when making the post request
    if session['create_customer_status'] == 'Failed':
        transfer_status = 'Failed to create customer'
        session['transfer_status'] = transfer_status
        return transfer_status
    #verification failed so transaction must be handled manually
    elif session['verification_status'] == 'unverified_manual_needed':
        session['transfer_status'] = session['verification_status']
        return session['transfer_status']
    plaid_token = session['access_token']
    plaid_account_id = session['ACCOUNT_ID']
    try:
        dwolla_response = client.Processor.dwollaBankAccountTokenCreate(plaid_token, plaid_account_id)
    except Exception as e:
        alert(e)
        session['transfer_status'] == "Error Connecting to Bank Account"
        return session['transfer_status']
    processor_token = dwolla_response['processor_token']
    #gets account# and routing
    auth_response = client.Auth.get(session['access_token'])
    for i in range(len(auth_response['accounts'])):
        if auth_response['accounts'][i]['account_id'] == session['ACCOUNT_ID']:
            index = i
    funding_source_request_body = {
      'plaidToken' : processor_token
      ,'name' : auth_response['accounts'][index]['official_name']
    }
    #create the funding source
    customer_funding_source_url = create_customer_funding_source(customer_url, funding_source_request_body)
    #Error resulted from an exception from dwolla after post request from funding source
    if customer_funding_source_url == 'Error linking to Bank Account':
        return customer_funding_source_url
    #ccreated funding source successfully
    else:
        #get Certasun account
        account_funding_source_url = getMasterAccountFundingSourceURL()
        #format the charge amount into the correct format for the dwolla request body
        Dwolla_Charge = str('{0:.2f}'.format(session['passAccount']['chargeAmount']))
        transfer_request_body = {
                    '_links': {
                        'source': {
                            'href': customer_funding_source_url
                        },
                        'destination': {
                            'href' : account_funding_source_url
                        }
                    },
                    'amount':{
                        'currency' : 'USD',
                        'value' : Dwolla_Charge
                    },
                    'metadata': {
                    'payment_type' : session['passAccount']['duePayment'],
                    'proj_ID': session['passAccount']['ID']
                    }
            }
        #initiate transfer and return the status
        transfer_status = createTransfer(transfer_request_body)
        return transfer_status

#method called by PLAID LINK
@application.route('/get_access_token_Dwolla', methods=['GET','POST'])
def get_access_token_Dwolla():
  public_token = request.form['public_token']
  ACCOUNT_ID = request.form['account_id']
  try:
      exchange_response = client.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    session['transfer_status'] = 'Verification Problem'
    return jsonify(format_error(e))
  access_token = exchange_response['access_token']
  session['access_token'] = access_token
  session['ACCOUNT_ID'] = ACCOUNT_ID
  #PLaid was successful now going on to dwolla
  transfer_status = pending_Dwolla()
  return render_template('testCSS.html', accountobj = toOBJ(session['passAccount']))

@application.route('/sessVars')
def getSessVars():
    if session['Validation_Error'] != 'No Error':
        return session['Validation_Error']
    else:
        return 'No Error'

#webhook event from dwolla that customer verification was successful
#email can be sent to the customer with a link to make that initial down payment
def webhook_customer_verified(customer, request):
    email_to_send = sf.query("select email from contact where name LIKE '%" +customer.body['firstName']+" "+customer.body['lastName'] +"%'")
    email_to_send = email_to_send['records'][0]['Email']
    email_to_send = email_to_send.replace('@', '%40', 1)
    text = customer.body['firstName'] + " " + customer.body['lastName'] + " " + "has been verified"
    plainText = "VISIT PAY CERTASUN VIA ACH TO PAY NOW"
    html = '<p> VISIT <a href = "127.0.0.1:5000/linkwithname/' + email_to_send + '">PAY CERTASUN VIA ACH<a> TO PAY NOW<p>'
    email_sender(mailto, "DWOLLA CUSTOMER VERIFIED", plainText, html)
    return
#webhook event from dowlla initial attempt to verify the customer failed
def webhook_customer_reverification_needed(customer, request):
    text = "ERROR verifying " + customer.body['firstName']+ " "+ customer.body['lastName'] + " status: " + request.json['topic']
    if request.json['topic'] == 'customer_reverification_needed':
        plainText = "Customer Verification failed LINK TO RETRY"
        html = "<p><a href = '127.0.0.1:5000/retrycreateverifiedcustomer'> LINK TO RETRY<a><p>"
    else:
        plainText = text
        html = 0
    email_sender(mailto, "DWOLLA VERIFICATION ERROR", plainText, html)
    return

#webhook event from dwolla that bank tranfer has failed
#updates payment status back to due
#and sends an email that the payment failed
def webhook_bank_transfer_failed(customer, request, transfer):
    #transfer = app_token.get(request.json['_links']['resource']['href'])
    retrieved_payment_type = transfer.body['metadata']['payment_type']
    proj_ID = transfer.body['metadata']['proj_ID']
    #this is to be sent to whoever at certasun what happend was the transfer failed and for whatever reason the contact info from dowlla doesnt match that
    # in salesforce
    if proj_ID == "NOT FOUND":
        pp.pprint (customer.body)
        plainText = """Customer: """ + customer.body['firstName'] + " " + customer.body['lastName'] + """
        Email: """ + customer.body['email'] + """
        Address: """ + customer.body['address1'] + " " + customer.body['city'] + " " + customer.body['state'] + " " + customer.body['state']
        email_sender("nathan@certasun.com", "BANK TRANSFER FAILED BUT EMAIL NOT IN SALESFORCE", plainText, 0)
        return
    status = change_payment_status_in_sf(retrieved_payment_type, proj_ID, "Due")
    date_time = transfer.body['created'].split("T")
    time_time = date_time[1].split(".")
    true_time = time_time[0]
    plainText = "Bank Transfer Fail, Customer:"  + customer.body['firstName'] + " " + customer.body['lastName'] + """
Payment Description: $""" + transfer.body['amount']['value'] + """ to Certasun for """ +transfer.body['metadata']['payment_type'] + """
Sent On: """ + date_time[0] + """ At: """ + true_time
    email_sender(mailto, 'Dwolla Bank Transfer Fail', plainText, 0)
    return
#webhook sent by stripe if charge was successful the payment status will be updated in sf to recieved
# if unsuccessful the payment status wil be updated to due
@application.route('/webhook_stripe', methods = ['POST'])
def webhook_stripe():
    if request.method == 'POST':
        if request.json['type'] == "charge.succeeded":
            payer_email = request.json['data']['object']['metadata']['email']
            payType = request.json['data']['object']['metadata']['payType']
            proj_ID = request.json['data']['object']['metadata']['proj_ID']
            change_payment_status_in_sf(payType, proj_ID, "Received")
        if request.json['type'] == "charge.failed":
            payer_email = request.json['data']['object']['metadata']['email']
            payType = request.json['data']['object']['metadata']['payType']
            proj_ID = request.json['data']['object']['metadata']['proj_ID']
            change_payment_status_in_sf(payType, proj_ID, "Due")
    return '', 200




#takes an email and returns the corresponding project ID
def get_proj_from_sf(email):
    query = sf.query("select Name, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '"+email+"')")
    proj_ID = query['records'][0]['Projects__r']['records'][0]['Id']
    return proj_ID

#takes in a project ID and a payment type and status and changes the payment status for that payment type for that project to the input
def change_payment_status_in_sf(payment_type, proj_ID, change_to):
    if payment_type == DOWN_PAYMENT_CONST:
        sf.project__c.update(proj_ID, {'Cash_Down_Pmt_Status__c': change_to})
    elif payment_type == PERMIT_PAYMENT_CONST:
        sf.project__c.update(proj_ID, {'Cash_Permit_Pmt_Status__c': change_to})
    elif payment_type == FINAL_PAYMENT_CONST:
        sf.project__c.update(proj_ID, {'Cash_Final_Pmt_Status__c': change_to})
    else:
        return "ERROR"
    return "PASS"
#creates an email from info given and sends
def email_sender(mail_to, sub, text, html):
    msg = EmailMessage()
    msg['From'] = gmailaddress
    msg['To'] = mail_to
    msg['Subject'] = sub
    msg.set_content(text)
    if html != 0:
        msg.add_alternative(html, subtype = 'html')
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.login(gmailaddress, gmailpassword)
    mailServer.send_message(msg)
    mailServer.quit()
    return

#webhook from dwolla that transfer was successful will update payment status in sf to recieved
#and then send an email
def webhook_bank_transfer_completed(customer, request, transfer):
    proj_ID = transfer.body['metadata']['proj_ID']
    pp.pprint(transfer.body)
    retrieved_payment_type = transfer.body['metadata']['payment_type']
    change_payment_status_in_sf(retrieved_payment_type, proj_ID, "Received")
    plainText = """Thank you for your payment to Certasun,
    Payment Details: $""" + transfer.body['amount']['value'] + """ for """ + transfer.body['metadata']['payment_type']
    email_sender(customer.body['email'], "Thank You", plainText, 0)
    return

#webhook from dwolla that transfer was cancelled most likely by customer
#####UPDATE change status in sf
def webhook_transfer_cancelled(customer, request, transfer):
    proj_ID = transfer.body['metadata']['proj_ID']
    payment_type = transfer.body['metadata']['payment_type']
    change_payment_status_in_sf(payment_type, proj_ID, 'Due')
    sub = "DWOLLA TRANSFER CANCELLED BY CUSTOMER"
    plainText = """Transfer Cancelled by """ + customer.body['firstName'] + """ """ + customer.body['lastName'] + """
    Tranfer Description: """ + transfer.body['metadata']['payment_type'] + """
    Amount: $"""+ transfer.body['amount']['value']
    email_sender(mailto, sub, plainText, 0)
    return

#takes in webhook events and decides what to do with them
@application.route('/webhook', methods = ['POST'])
def webhook():
        if request.method == 'POST':
            gmailaddress = "wayno5650@gmail.com"
            gmailpassword = "Cush5656"
            customer = app_token.get(request.json["_links"]["customer"]['href'])
            mailto = sf.query("select email from contact where Name LIKE '%" + customer.body['firstName']+ " "+customer.body['lastName']+"%'")
            if request.json['topic'] == "customer_verified":
                webhook_customer_verified(customer, request)
            if request.json['topic'] == 'customer_reverification_needed' or request.json['topic'] == 'customer_verification_document_needed' or request.json['topic'] == 'customer_suspended':
                webhook_customer_reverification_needed(customer, request)
            if request.json['topic'] == 'bank_transfer_failed':
                transfer = app_token.get(request.json['_links']['resource']['href'])
                webhook_bank_transfer_failed(customer, request, transfer)
            if request.json['topic'] == "customer_bank_transfer_completed" or request.json['topic'] == "bank_transfer_completed":
                transfer = app_token.get(request.json['_links']['resource']['href'])
                webhook_bank_transfer_completed(customer, request, transfer)
            if request.json['topic'] == "bank_transfer_cancelled" or request.json['topic'] == "customer_bank_transfer_cancelled":
                transfer = app_token.get(request.json['_links']['resource']['href'])
                webhook_transfer_cancelled(customer, request, transfer)
            return '', 200
        else:
            abort(400)

#STRIPE IMPLEMENTATION DEPRACATED
@application.route('/get_access_token', methods = ['GET','POST'])
def get_access_token():
  global access_token
  public_token = request.form['public_token']
  ACCOUNT_ID = request.form['account_id']
  try:
    exchange_response = client.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  pretty_print_response(exchange_response)
  access_token = exchange_response['access_token']
  stripe_response = client.Processor.stripeBankAccountTokenCreate(access_token, ACCOUNT_ID)
  bank_account_token = stripe_response['stripe_bank_account_token']
  charge_amount = send_payment
  charge_amount = int(charge_amount)
  try:
    charge = stripe.Charge.create(
      amount = charge_amount,
      currency = 'usd',
      description='ACH Payment via plaid from ' + passAccount.name + ' for ' + passAccount.duePayment,
      source = bank_account_token,
    )
    return render_template('thanks.html')
    pass
  except stripe.error.CardError as e:
    output = {"result":e}
  except Exception as e:
        pass
  else:
        output = {"result":"1"}
  return render_template('testCSS.html')

@application.route('/auth', methods=['GET'])
def get_auth():
  try:
    auth_response = client.Auth.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(auth_response)
  return jsonify({'error': None, 'auth': auth_response})

@application.route('/transactions', methods=['GET'])
def get_transactions():
  # Pull transactions for the last 30 days
  start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
  end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
  try:
    transactions_response = client.Transactions.get(access_token, start_date, end_date)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  pretty_print_response(transactions_response)
  return jsonify({'error': None, 'transactions': transactions_response})


@application.route('/identity', methods=['GET'])
def get_identity():
  try:
    identity_response = client.Identity.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(identity_response)
  return jsonify({'error': None, 'identity': identity_response})

@application.route('/balance', methods=['GET'])
def get_balance():
  try:
    balance_response = client.Accounts.balance.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(balance_response)
  return jsonify({'error': None, 'balance': balance_response})

@application.route('/accounts', methods=['GET'])
def get_accounts():
  try:
    accounts_response = client.Accounts.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(accounts_response)
  return jsonify({'error': None, 'accounts': accounts_response})

@application.route('/assets', methods=['GET'])
def get_assets():
  try:
    asset_report_create_response = client.AssetReport.create([access_token], 10)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(asset_report_create_response)
  asset_report_token = asset_report_create_response['asset_report_token']
  # Poll for the completion of the Asset Report.
  num_retries_remaining = 20
  asset_report_json = None
  while num_retries_remaining > 0:
    try:
      asset_report_get_response = client.AssetReport.get(asset_report_token)
      asset_report_json = asset_report_get_response['report']
      break
    except plaid.errors.PlaidError as e:
      if e.code == 'PRODUCT_NOT_READY':
        num_retries_remaining -= 1
        time.sleep(1)
        continue
      return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

  if asset_report_json == None:
    return jsonify({'error': {'display_message': 'Timed out when polling for Asset Report', 'error_code': e.code, 'error_type': e.type } })

  asset_report_pdf = None
  try:
    asset_report_pdf = client.AssetReport.get_pdf(asset_report_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

  return jsonify({
    'error': None,
    'json': asset_report_json,
    'pdf': base64.b64encode(asset_report_pdf), })

@application.route('/item', methods=['GET'])
def item():
  global access_token
  item_response = client.Item.get(access_token)
  institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
  pretty_print_response(item_response)
  pretty_print_response(institution_response)
  return jsonify({'error': None, 'item': item_response['item'], 'institution': institution_response['institution']})

@application.route('/set_access_token', methods=['POST'])
def set_access_token():
  global access_token
  access_token = request.form['access_token']
  item = client.Item.get(access_token)
  return jsonify({'error': None, 'item_id': item['item']['item_id']})

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True))

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }


if __name__ == '__main__':
    application.run(debug=True)
