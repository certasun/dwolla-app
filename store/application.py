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
sf_token = 'gmrlB5Pl79Nykd1UP4rl3tOC'
pp = pprint.PrettyPrinter(indent=4)
sf = Salesforce(sf_user +".plaidtest", sf_pass, sf_token, domain = 'test')
DOWN_PAYMENT_CONST = "Down Payment"
PERMIT_PAYMENT_CONST = "Permit Payment"
FINAL_PAYMENT_CONST = "Final Payment"
DUE_STATUS = "Due"
NOT_DUE_STATUS = "Not Due"
app_token = dwolla_client.Auth.client()
class nameForm(FlaskForm):
    name = StringField('Last Name')
    submit = SubmitField('SUBMIT')

class ACCOUNT:
    def __init__(self, name):
        self.name = name
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
            print(self.duePayment)
            self.chargeAmount = self.dp
            return self.dp
        if self.duePayment == PERMIT_PAYMENT_CONST:
            print(PERMIT_PAYMENT_CONST)
            self.chargeAmount = self.pp
            return self.pp
        if self.duePayment == FINAL_PAYMENT_CONST:
            self.chargeAmount = self.fp
            return self.fp
        return 0
    def toJSON(self):
        return self.__dict__

def toOBJ(myobj):
        OBJ =ACCOUNT(myobj['name'])
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

@application.route('/setWebHook')
def setWebHook():
     webhook_request_body = {
       'url' : 'https://engrropkjkfh9.x.pipedream.net',
       'secret' : 'This is from Dwolla'
     }
     subscription = app_token.post('webhook-subscriptions', webhook_request_body)
     return "WEBHOOK SET"

@application.route('/simulation')
def simulation():
    app_token.post()

@application.route('/thanks')
def thanks():
    if session['transfer_status'] == 'failed':
        return render_template('failed.html')
    if session['transfer_status'] == 'pending':
        if session['passAccount']:
            if session['passAccount']['duePayment'] == DOWN_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Down_Pmt_Status__c': 'In Flight'})
            if session['passAccount']['duePayment'] == PERMIT_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Permit_Pmt_Status__c': 'In Flight'})
            if session['passAccount']['duePayment'] == FINAL_PAYMENT_CONST:
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Final_Pmt_Status__c': 'In Flight'})
    return render_template('thanks.html')

@application.route('/failed')
def failed():
    return render_template('failed.html')

@application.route('/', methods = ['GET', 'POST'])
@application.route('/testNewStart', methods = ['GET', 'POST'])
def newStart():
    thisform = nameForm()
    webhook_subs = app_token.get('webhook-subscriptions')
    #TO DELETE WEBHOOKS
    #for i in range(len(webhook_subs.body['_embedded']['webhook-subscriptions'])):
    #    app_token.delete(webhook_subs.body['_embedded']['webhook-subscriptions'][i]['_links']['self']['href'])
    if thisform.validate_on_submit():
        name = thisform.name.data
        #To run query off of email instead of last name
        #testAccountName = sf.query("select Account.Name from Contact where Email LIKE'%" + name +"%'")
        #testquery1 = sf.query("select Cash_Down_pmt__c, Cash_Final_Pmt__c, Permit_pmt__C from Project__c where Account__r.Name LIKE '%"+testAccountName['records'][0]['Account']['Name']+"%'")
        #payments_from_email_query = {'DOWN_PMT':testquery1['records'][0]['Cash_Down_Pmt__c'], 'PERMIT_PAYMENT' : testquery1['records'][0]["Permit_Pmt__c"], 'FINAL_PAYMENT' : testquery1['records'][0]['Cash_Final_Pmt__c']}
        #print(payments_from_email_query)
        return redirect(url_for('passObj', name = name))
    return render_template('startPage.html', form = thisform)

@application.route('/linkwithname/<name>')
def passObj(name):
    passAccount = runQueries(name)
    if passAccount == 1:
        return redirect(url_for('InvalidName'))
    if passAccount ==2:
        return redirect(url_for('multipleRecords', name = name))
    session['passAccount'] = passAccount.toJSON()
    session['Validation_Error'] = 'No Error'
    session['transfer_status'] = "BLANK"
    if passAccount:
        send_payment = passAccount.getnextpayment()
        session['send_payment'] = send_payment
        return render_template('testCSS.html', pub_key = pub_key,
         account_name = passAccount.name, payment =send_payment, accountobj=passAccount)
    else:
         return redirect(url_for('newStart'))

def runQueries(name):
    Account_Name_query = sf.query("select name from project__c where name LIKE '%"+ name +"%'")
    if Account_Name_query['totalSize'] == 0:
        return 1
    if Account_Name_query['totalSize'] > 1:
        return 2
    Account_Name = Account_Name_query['records'][0]['Name']
    thisAccount = ACCOUNT(Account_Name)
    fullPaymentQuery = sf.query("select id, Cash_Down_pmt__c, Cash_Down_Pmt_Status__c, Permit_pmt__C, Cash_Permit_Pmt_Status__c, Cash_final_Pmt__c, Cash_final_pmt_status__c from project__c where name LIKE '%" + name + "%'")
    thisAccount.ID = fullPaymentQuery['records'][0]['Id']
    thisAccount.dp = fullPaymentQuery['records'][0]['Cash_Down_Pmt__c']
    thisAccount.dpSTAT = fullPaymentQuery['records'][0]['Cash_Down_Pmt_Status__c']
    thisAccount.pp = fullPaymentQuery['records'][0]['Permit_Pmt__c']
    thisAccount.ppSTAT = fullPaymentQuery['records'][0]['Cash_Permit_Pmt_Status__c']
    thisAccount.fp = fullPaymentQuery['records'][0]['Cash_Final_Pmt__c']
    thisAccount.fpSTAT = fullPaymentQuery['records'][0]['Cash_Final_Pmt_Status__c']
    if thisAccount.dpSTAT == DUE_STATUS or thisAccount.dpSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = DOWN_PAYMENT_CONST
        return thisAccount
    if thisAccount.ppSTAT == DUE_STATUS or thisAccount.ppSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = PERMIT_PAYMENT_CONST
        return thisAccount
    if thisAccount.fpSTAT == DUE_STATUS or thisAccount.fpSTAT == NOT_DUE_STATUS:
        thisAccount.duePayment = FINAL_PAYMENT_CONST
        return thisAccount
    thisAccount.duePayment = "NA"
    return thisAccount

@application.route('/InvalidName', methods = ['GET', 'POST'])
def InvalidName():
    thisform = nameForm()
    if thisform.validate_on_submit():
        name = thisform.name.data
        return redirect(url_for('passObj', name = name))
    return render_template('Invalid.html', form = thisform)

@application.route('/multipleRecords/<name>')
def multipleRecords(name):
    Account_Name_query = sf.query("select name from project__c where name LIKE '%"+ name +"%'")
    accountList = list()
    for i in range(Account_Name_query['totalSize']):
        accountList.append(Account_Name_query['records'][i]['Name'])
    return render_template('multipleRecords.html', accounts = accountList)

@application.route('/accountpicked/<account>')
def accountpicked(account):
    Down_payment_query = sf.query("select Cash_Down_Pmt__c, Permit_Pmt__c, Cash_Final_Pmt__c from project__c where name LIKE '%" + account + "%'")
    Down_payment = Down_payment_query['records'][0]['Cash_Down_Pmt__c']
    session['send_payment'] = Down_payment
    if Down_payment == 0.0:
        permit_payment = Permit_payment_query['records'][0]['Permit_Pmt__c']
        session['send_payment'] = permit_payment
        if permit_payment == 0.0:
            final_payment = exact_final_payment['records'][0]['Cash_Final_Pmt__c']
            session['send_payment'] = final_payment
    return redirect(url_for('index', payment = session['send_payment'], name = account))

@application.route('/index/<payment>/<name>')
def index(payment, name):
    return render_template('testCSS.html',pub_key=pub_key, payment = session['send_payment'], account_name = name )

@application.route('/get_access_token_Dwolla', methods=['GET','POST'])
def get_access_token_Dwolla():
  public_token = request.form['public_token']
  ACCOUNT_ID = request.form['account_id']
  try:
      exchange_response = client.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  access_token = exchange_response['access_token']
  session['access_token'] = access_token
  dwolla_response = client.Processor.dwollaBankAccountTokenCreate(access_token, ACCOUNT_ID)
  processor_token = dwolla_response['processor_token']
  request_body = {
    'plaidToken' : processor_token
    ,'name' : session['passAccount']['name'] + ' ACH'
  }
  webhook_request_body = {
    'url' : 'https://envxivvnruzfr.x.pipedream.net',
    'secret' : 'This is from Dwolla'
  }
  namelist = session['passAccount']['name'].split()
  contact = sf.query("select Email from contact where Name LIKE '%" + namelist[0] +"%'")
  Email = contact['records'][0]['Email']
  customer_create_request_body = {
            'firstName' : namelist[0],
            'lastName' : namelist[1],
            'email' : Email
  }
  customer_response = app_token.get('customers')
  customer_response_len = len(customer_response.body['_embedded']['customers'])
  bool = (-1)
  for i in range(customer_response_len):
      if Email == customer_response.body['_embedded']['customers'][i]['email']:
          bool = i
  if bool != (-1):
      customer_url = 'https://api-sandbox.dwolla.com/customers/' + customer_response.body['_embedded']['customers'][bool]['id']
  else:
      customer = app_token.post('customers', customer_create_request_body)
      customer_url = customer.headers['location']
  customer = app_token.get(customer_url)
  try:
      customer_funding_source = app_token.post('%s/funding-sources' % customer_url, request_body)
      customer_funding_source_url = customer_funding_source.headers['location']
  except Exception as e:
      customer_funding_source_url = e.body['_links']['about']['href']
      #remove_request_body = {'removed':True}
      #remove_funding_source = app_token.post(e.body['_links']['about']['href'], remove_request_body)
      #customer_funding_source_url = app_token.post('%s/funding-sources' % customer_url, request_body)
  root = app_token.get('/')
  account_url = root.body['_links']['account']['href']
  account_funding_source_url = app_token.get('%s/funding-sources' % account_url)
  Dwolla_Charge = str('{0:.2f}'.format(session['passAccount']['chargeAmount']/10))
  #test_failure_post = app_token.post(customer_funding_source_url, test_failure_request_body)
  transfer_request_body = {
              '_links': {
                  'source': {
                      'href': customer_funding_source_url
                  },
                  'destination': {
                      'href' : account_funding_source_url.body['_embedded']['funding-sources'][0]['_links']['self']['href']
                  }
              },
              'amount':{
                  'currency' : 'USD',
                  'value' : Dwolla_Charge
              }
      }
  try:
      transfer = app_token.post('transfers', transfer_request_body)
      transfer_url = transfer.headers['location']
      getTransfer = app_token.get(transfer_url)
      transfer_status = getTransfer.body['status']
      session['transfer_status'] = transfer_status
      remove_request_body = {'removed':True}
      #remove_funding_source = app_token.post(customer_funding_source_url, remove_request_body )
  except Exception as ex:
      session['Validation_Error'] = ex.body['_embedded']['errors'][0]['message']
  return render_template('testCSS.html', accountobj = toOBJ(session['passAccount']))

@application.route('/sessVars')
def getSessVars():
    if session['Validation_Error'] != 'No Error':
        return session['Validation_Error']
    return 'No Error'

@application.route('/webhook', methods = ['POST'])
def webhook():
        if request.method == 'POST':
            json_str = str(request.json)
            gmailaddress = "wayno5650@gmail.com"
            gmailpassword = "Cush5656"
            mailto = "nathan@certasun.com"
            msg = MIMEMultipart()
            msg['From'] = gmailaddress
            msg['To'] = mailto
            msg['Subject'] = "DWOLLA TEST"
            msg.attach(MIMEText(json_str, 'plain'))
            mailServer = smtplib.SMTP('smtp.gmail.com', 587)
            mailServer.starttls()
            mailServer.login(gmailaddress, gmailpassword)
            mailServer.send_message(msg)
            print('message sent')
            mailServer.quit()
            return '', 200
        else:
            abort(400)

#STRIPE IMPLEMENTATION
@application.route('/get_access_token', methods=['GET','POST'])
def get_access_token():
  print('get access token called')
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
