from flask import Flask, session, render_template, request, redirect, url_for,jsonify, abort, session
import stripe
import dwollav2
import plaid
import base64
import os
import datetime
import json
import time
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
from DwollaApplication0.forms import nameForm, retryForm, decodeForm, verificationForm, ACCOUNT, toOBJ, setFrontEndStatus
from DwollaApplication0.webhooks import  webhook_customer_verified, webhook_customer_reverification_needed, webhook_bank_transfer_failed
from DwollaApplication0 import application, mail, app_settings, pp

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

#takes in webhook events and decides what to do with them
@application.route('/webhook', methods = ['POST'])
def webhook():
        sf = Salesforce(sf_user +".plaidtest", sf_pass, sf_token, domain = 'test')
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

#method that is invoked by the SF callout when a new project is created and it will create a formatted email
#to send to the customer so that they may reach the payment portal and initiate payments
@application.route('/newProj', methods = ['POST'])
def templateEmailnew():
    ### request is sent to this webservice from salesforce with a project Id
    if request.method == "POST":
        id = request.json['id']
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    # get the email belonging to the contact for whom the project is for
    contact_query = sf.query("select Name, ID, (select name, email, MailingAddress from contacts) from account where ID IN (select Account__c from project__c where project__c.Id  = '"+id+"')")
    #link that will be sent in the email in order for the customer to go to payment portal
    email_link = "http://eft-env.7eqxt8c8qq.us-east-2.elasticbeanstalk.com/linkwithid/" + id
    templateLoader = jinja2.FileSystemLoader(searchpath = "/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    ### get the rest of the data from the project in order to format the templated email
    query = sf.query("select id, Name, Cash_Down_Pmt_Status__c, Cash_Down_Pmt__c, Cash_Permit_Pmt_Status__c, Permit_Pmt__c, Cash_Final_Pmt_Status__c, Cash_final_Pmt__c from Project__c where ID =  '"+id+"'")
    #project down payment:
    p_down = query['records'][0]['Cash_Down_Pmt__c']
    #project down payment status:
    p_down_stat = query['records'][0]['Cash_Down_Pmt_Status__c']
    #project permit payment:
    p_permit = query['records'][0]['Permit_Pmt__c']
    #project permit payment status:
    p_permit_stat = query['records'][0]['Cash_Permit_Pmt_Status__c']
    #project final payment:
    p_final = query['records'][0]['Cash_Final_Pmt__c']
    #project final payment status:
    p_final_stat = query['records'][0]['Cash_Final_Pmt_Status__c']
    #concatonate a string to show the customers address
    address = str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['street']) + " " + str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['city']) + ", " + str(contact_query['records'][0]['Contacts']['records'][0]['MailingAddress']['state'])
    #Name of contact whom project belongs to:
    contact_name = contact_query['records'][0]['Contacts']['records'][0]['Name']
    #split the contact name to get first and last seperate
    contact_name_list = contact_name.split()
    #create an ACCOUNT object for this project
    email_recipient_account = ACCOUNT(contact_query['records'][0]['Name'], contact_name_list[0], contact_name_list[1])
    #set the objects down payment:
    email_recipient_account.dp = p_down
    #set objects down payment status:
    email_recipient_account.dpSTAT = setFrontEndStatus(p_down_stat)
    #set objects permit payment:
    email_recipient_account.pp = p_permit
    #set objects permit payment status:
    email_recipient_account.ppSTAT = setFrontEndStatus(p_permit_stat)
    #set objects final payment:
    email_recipient_account.fp = p_final
    #set objects final payment status:
    email_recipient_account.fpSTAT = setFrontEndStatus(p_final_stat)
    #use getDuePayment method to find out which payment will need to be paid next with logic in that method
    duepayment = email_recipient_account.getDuePayment()
    #use getnextpayment to get the value of the duepayment
    next_payment = email_recipient_account.getnextpayment()
    #locale is used to format currency
    locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
    #format the next_payment from a float to a currency string
    next_payment = locale.currency(next_payment)
    #### create id's to reference images that will be embedded in email
    logoImage_cid = make_msgid()
    bg1Image_cid = make_msgid()
    facebook_cid = make_msgid()
    twitter_cid = make_msgid()
    ig_cid = make_msgid()
    #############
    #create the templated email
    html = render_template('emailtemplate1.html', name = contact_name, chargeAmount = next_payment, duePayment = duepayment, payment_link = email_link, address = address, logoImage_cid = logoImage_cid[1:-1], bg1Image_cid = bg1Image_cid[1:-1], facebook_cid = facebook_cid[1:-1]) #, twitter_cid = twitter_cid[1:-1], ig_cid = ig_cid[1:-1])
    #instantiate an EmailMessage OBject
    msg = EmailMessage()
    #Email's subject:
    msg['Subject'] = 'Pay Certasun'
    #Email address message will be sent from
    msg['From'] = app_settings['OUTLOOK_ADDRESS']#mail_settings['MAIL_USERNAME']
        ############# change back but for testing send to my email ###################
    #Address Email will be sent to
    msg['To'] = "wayno5650@gmail.com"#email
    #############################################################################
    #Email messages preamble
    msg.preamble = "Certasun"
    #set the plain text as an empty string
    msg.set_content("")
    #set the templated html of the message
    msg.add_alternative(html, subtype = 'html')
    ############# Embed the images into the email msg###################
    with open('static/img/CertasunLogo.png', 'rb') as fp:
        msg.get_payload()[1].add_related(fp.read(), 'image','png',cid=logoImage_cid)
    with open('static/img/bg1.png', 'rb') as fp:
        msg.get_payload()[1].add_related(fp.read(), 'image', 'png', cid = bg1Image_cid)
    with open('static/img/free_ico_facebook.jpg', 'rb') as fp:
        msg.get_payload()[1].add_related(fp.read(), 'image', 'jpg', cid = facebook_cid)
    ######################################################################
    #write the message to the file
    with open('outgoing.msg', 'wb') as f:
        f.write(bytes(msg))
    #start up the smtp server
    smtp = smtplib.SMTP(app_settings['AWS_SES_ENDPOINT'], 25)
    smtp.ehlo()
    #start tls which means message will be encrypted
    smtp.starttls()
    #login to the AWS SES account
    smtp.login(app_settings['SMTP_USERNAME'], app_settings['SMTP_PASSWORD'])
    #send the message, first parameter is who it is from, 2nd is who is is two and the thirsd is the content of the message
    smtp.sendmail("nathan@certasun.com", msg['To'], msg.as_string())
    #shutdown the connection to the smtp server
    smtp.quit()
    #return a status code of 200
    return '', 200

#route for the main landing page where user may enter their email to access their payment portal
@application.route('/', methods = ['GET', "POST"])
@application.route('/landingpagelayout', methods = ['GET', 'POST'])
def landing_page():
    #open an API connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #instantiate the form that will be displayed on the PAGE
    #in this case the form will have 1 inpute which will be the email
    #and a submit button
    form = nameForm()
    #if the form is validated after submit button is hit this statement will execute
    if form.validate_on_submit():
        #clear all session variables so their are no data integrity issues
        session.clear()
        #get the email that was entered into the form
        email = form.name.data
        #query salesforce for the project associated with the contact that holds that email
        query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
        #statement is executed if there is no contact with that email or the contact with that email has no associated projects
        if query['totalSize'] == 0 or query['records'][0]['Projects__r'] == None:
            #redirect them to the invalidName page so a error message will appear telling them that the email is invalid and allowingg them to re enter their email
            return redirect(url_for('InvalidName'))
        #this statement will execute if the contact that holds the entered email has more than one project associated with it
        elif query['records'][0]['Projects__r']['totalSize'] > 1:
            #set a session variable to hold the email
            session['email'] = email
            #redirect to a page that gives a list of project names associated with that email so that the user will be able to chose which project they are looking to make a payment for
            return redirect(url_for('multipleRecords', email = email))
        #If the contact that holds that email has exactly one project associated with it this statement will execute
        elif query['records'][0]['Projects__r']['totalSize'] == 1:
            #again set a session variable to hold the email
            session['email'] = email
            #redirect user to method that will get all the info on the project and then display the user their payment portal
            return redirect(url_for('passObjID', id = query['records'][0]['Projects__r']['records'][0]['Id']))
    #index3.html is the landing page html document
    return render_template('index3.html', form = form)

#CHECKS TRANSFER STATIS AND REDIRECTS TO CORRECT PAGE BASED ON TRANSFER STATUS
@application.route('/thanks')
def thanks():
    #instatiate a connection to salesforce API
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #IF WHILE CREATING CUSTOMER THE CUSTOMER WASNT VERIFIED THIS WILL SHOW CUSTOMER THAT PAYMENT IS
    #PENDING AND TRANSFER WILL NEED TO BE DONE MANUALLY VIA CHASE
    if session['transfer_status'] == 'unverified_manual_needed':
        return render_template('newEnd.html', big_message = "Thank You", reason = "Your Payment is Now Pending")
    #TRANSFER WAS SUCCESSFULLY INITIATED THROUGH DWOLLA AND IS NOW PENDING
    #SALEFORCE WILL BE UPDATED TO SHOW PAYMENT IS IN FLIGHT
    elif session['transfer_status'] == 'pending':
        #make sure their is an account object in the session variable if so this statement will execute
        if session['passAccount']:
            #if the payment that was just made was the down payment this statement will execute
            if session['passAccount']['duePayment'] == app_settings['DOWN_PAYMENT_CONST']:
                #change the status inside of salesfore for the down payment to In flight indicating that the trasfer has been initiated but is not completed
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Down_Pmt_Status__c': 'In Flight'})
            #if the payment that was just made was the permit payment then this statement will execute
            if session['passAccount']['duePayment'] == app_settings['PERMIT_PAYMENT_CONST']:
                #change the status in salesfore for the permit payment to In flight indicating that transfer was initiated but not completed
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Permit_Pmt_Status__c': 'In Flight'})
            #if payment that was just made was final payment this statement will execute
            if session['passAccount']['duePayment'] == app_settings['FINAL_PAYMENT_CONST']:
                #set value in salesforce for the final payment to In Flight indicating transfer was initiated but not completeed
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Final_Pmt_Status__c': 'In Flight'})
            #render the html document that says thank you
            return render_template('newEnd.html', big_message = "Thank You", reason ="Your payment is now pending")
    # this statement will execute if the customer initiated a payment with a credit card and the payment was successful through stripe
    elif session['transfer_status'] == 'stripe_paid_true':
        #check to make sure their is an account object in the session variables
        if session['passAccount']:
            #payment made was for down payment this statement is exexuted
            if session['passAccount']['duePayment'] == app_settings['DOWN_PAYMENT_CONST']:
                #update salesforce down payment to In flight
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Down_Pmt_Status__c': 'In Flight'})
            #payment made was for permit payment this statement will exwcute
            if session['passAccount']['duePayment'] == app_settings['PERMIT_PAYMENT_CONST']:
                ##update permit payment status is salesforce to In flight
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Permit_Pmt_Status__c': 'In Flight'})
            #payment was for final payment this statement will execute
            if session['passAccount']['duePayment'] == app_settings['FINAL_PAYMENT_CONST']:
                ##update final payment status in salesforrce to in flight
                sf.project__c.update(session['passAccount']['ID'], {'Cash_Final_Pmt_Status__c': 'In Flight'})
            #render thank you html documents
            return render_template('newEnd.html', big_message = "Thank You")
            #TRANSFER STATUS WASNT
    #this will execute when the payment failed somewhere in the processing of the payment either through dwolla or stripe
    #no value will be changed in salesforce and customer will be prompted with a page that indicates there was an error
    elif session['transfer_status'] != 'pending' and session['transfer_status'] != 'unverified_manual_needed':
        return render_template('newEnd.html',big_message = "Error", reason = session['transfer_status'])

@application.route('/failed')
def failed():
    return render_template('failed.html')

#CAN BE ACCESSED EITHER FROM A LINK OR FROM THE startPage
#FIRST WILL CLEAR THE SESSION FOR DATA INTEGRITY
#WILL THEN GET THE CONTACT NAME FROM SALESFORCE BY USING THE PROJECT ID PROVIDED
#takes in one parameter whihc is the project id
@application.route('/linkwithid/<id>', methods = ['GET', "POST"])
def passObjID(id):
    #create global variables for both the plaid and dwolla clients so they can be accessed in other methods
    global client, dwolla_client
    #instantiate a connection to both the plaid and dwolla API's
    client = plaid.Client(client_id = app_settings['PLAID_CLIENT_ID'], secret=app_settings['PLAID_SECRET_SAND'], public_key= app_settings['PLAID_PUBLIC_KEY'], environment=app_settings['PLAID_ENV'], api_version='2019-05-29')
    dwolla_client = dwollav2.Client( key = app_settings['DWOLLA_KEY'], secret = app_settings['DWOLLA_SECRET'], environment = 'sandbox')
    global app_token
    app_token = dwolla_client.Auth.client()
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    session.clear()
    #instantitate the form
    form = verificationForm()
    # set a session variable to store the project ID
    session['proj_ID'] = id
    #query salesforce for the ID of the Account that is associated with the project
    contact_query = sf.query("select contact_first_name__c, contact_last_name__c, Name, ID, (select name, email, MailingAddress from contacts) from account where ID IN (select Account__c from project__c where project__c.Id  = '"+id+"')")
    # this statement will execute if there is no account associated with that project
    if contact_query['totalSize'] == 0:
        #they will be redirected to a page with an error message saying that the email does exist this
        #really should never occur the only way this would occur is if someone deleted either the project
        # or cantact in salesforce after the email was sent to them which would result in a dead link
        #but instead it would now redirect them to a page where they can enter their email to find their payment portal
        return(redirect(url_for('InvalidName')))
    #set a local variable to hold the account ID that was returned by the salesforce query
    accountID = contact_query['records'][0]['Id']
    # set a local variable to hold email that was sent back from salesforce
    email = contact_query['records'][0]['Contacts']['records'][0]['Email']
    #set a session variable for that same email that was sent back by salesforce
    session['email'] = email
    #set a local variable for the accout name that was returned by salesforce
    A_NAME = contact_query['records'][0]['Name']
    #set a session variable for the same account name that was returned by salesforce
    session['name'] = A_NAME
    #set a local variable for the customers first name that was returned by salesforce
    first_name = contact_query['records'][0]['Contact_First_Name__c']
    #set a local variable for the customerss last name that was returned by salesforce
    last_name = contact_query['records'][0]['Contact_Last_Name__c']
    #if for some reason the account in salesforce didnt have a last name
    if last_name == None:
        lastname = "lastname"
    #call the runqueries method that takes in a the account name, customer first name, customer last name, and the project ID and will return an ACCOUNT object
    passAccount = runQueriesID(A_NAME, first_name, last_name, id)
    #set a session variable for the data inside the ACCOUNT object that was just instantiated above by converting all the data inside the object to a json
    session['passAccount'] = passAccount.toJSON()
    #setting error codes to default settings
    session['Validation_Error'] = 'No Error'
    session['transfer_status'] = "BLANK"
    #query dwolla for a customer with the email because we would like to see if the customer is already VERIFIED
    # because if they were already verified we dont need to ask for their confidential information again in order to make a large transfer
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
        #get the value for the charge and set as a local variable
        send_payment = passAccount.getnextpayment()
        #set a session variable for the next payment
        session['send_payment'] = send_payment
        #get additional data from sf to show on page
        name_address = sf.query("select name, MailingAddress, email from contact where email LIKE '%" +email+ "%'")
        #set a local variable for the city
        a_city = name_address['records'][0]['MailingAddress']['city']
        #set a local variable for the state
        a_state = name_address['records'][0]['MailingAddress']['state']
        #set a local variable for the street address
        a_street = name_address['records'][0]['MailingAddress']['street']
        #set a local variable for the zip code
        a_zip = name_address['records'][0]['MailingAddress']['postalCode']
        #create a json to hold all of the address information so that it can be passed to the front end to be rendered much easier
        location = {
        'city' : a_city,
        'state' : a_state,
        'street' : a_street,
        'zip' : a_zip
        }
        #we are going to check if the payment that needs to be made next is the downpayment and if so we want to waive the credit card convienience fee so we will set a
        # local variable to be sent to the front end to tell whether we need to charge the credit card convienience fee or not
        if passAccount.duePayment == 'Down Payment':
            #using either a one or a zero because was having issues in front end logic determining equality of strings
            charge_fee = 0
        else:
            charge_fee = 1
        return render_template('ach-credit.html',charge_fee = charge_fee, unverified_limit =app_settings['DWOLLA_UNVERIFIED_LIMIT'], accountobj = passAccount, payment = send_payment, email = email, location = location, pre_verified = pre_verified)
    else:
         return redirect(url_for('newStart'))

#stripe credit card charge implementation
@application.route('/charge', methods = ['GET', 'POST'])
def credit_handler():
    #get the stripe token
    token = request.form['stripeToken']
    #create a charge with the data from the form
    charge = stripe.Charge.create(
        #amount stripe will charge the credit card
        amount=request.form['amount'],
        #currency of the amount
        currency='usd',
        #description of the charge
        description=request.form['description'],
        #token from stripe
        source=token,
        #metadata added so we can retrieve customer information from webhook events and send email upon failure or completion if we so pleae
        metadata = {'email': request.form['email'],
                    #paytype is the payment type for example down payment, permit payment, or final payment
                    'payType':request.form['payType'],
                    #project ID in salesforce
                    'proj_id' : request.form['proj_ID']}
    )
    #this statement will only execute if stripe returns a status of paid whcih means the transaction was successful
    if charge['paid'] == True:
        #get the project id from the metadata of the stripe charge
        proj_ID = charge['metadata']['proj_id']
        #change the payment status in salesforce for that particular payment for instance down payment that is held in the response['paytype'] metadata
        # now we are changing it to in flight and recieved from a webhook event but may just want to change it directly to recieved here as I believe this means
        #charge was successful
        change_payment_status_in_sf(request.form['payType'], proj_ID, "In Flight")
        #set a session variable to stripe_paid_true this is reference in the thanks() method and is used in the logic so it knows
        # to display the thank you page instead of the error page because the payment was successful if the program made it to this line
        session['transfer_status'] = 'stripe_paid_true'
        #redirect the customer to the thanks page to tell them that the payment is pending
    return redirect(url_for('thanks'))

#this form takes in the data from the form called ACHFORM in the ach-credit html File
# the data will be used to be sent to dwolla in order to attempt to make a verified customer
@application.route('/handle_validation_form', methods = ["POST"])
def handle_validation_form():
    #get the last 4 of the social and store in local variable
    SSN = request.form['s']
    #get the date of birth and staore in a local variable
    DOB = request.form['d']
    # call the method that will create a request body json with all the relevant data for this custoemr
    # this method has two parameter which are the two values just taken from the form
    request_body = create_verified_request_body_from_SF(SSN, DOB)
    try:
        #attempt to create a verified customer in dwolla by making a post request to their customers API endpoint
        customer = app_token.post('customers', request_body)
        customer_url = customer.headers['location']
        session['create_customer_status'] = 'Passed'
    except Exception as e:
        pp.pprint(e)
        session['create_customer_status'] = 'Failed'
    return '', 200

#this method is called to run queries in salesforce on a given project and return an ACCOUNT object with all relevant DATA
# this method had 4 parameters
    #1: name = the name of the account in SALESFORCE
    #2: fname = the first name of the contact in SALESFORCE
    #3: lname = the last name of the contact in SALESFORCE
    #4: id = the project id from SALESFORCE
def runQueriesID(name, fname, lname, id):
    #instantiate a connection to SALESFORCE
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    # create an ACCOUNT object from the parameters
    thisAccount = ACCOUNT(name, fname, lname)
    #query salesforce for the payment information on this project
    query = sf.query("select Name, id, Cash_Down_pmt__c, Cash_Down_Pmt_Status__c, Permit_pmt__C, Cash_Permit_Pmt_Status__c, Cash_final_Pmt__c, Cash_final_pmt_status__c from Project__c where id = '" + id + "'")
    #set the rest of the varicables for the ACCOUNT object ###########################################
    thisAccount.ID = query['records'][0]['Id']
    thisAccount.dp = query['records'][0]['Cash_Down_Pmt__c']
    thisAccount.dpSTAT = setFrontEndStatus(query['records'][0]['Cash_Down_Pmt_Status__c'])
    thisAccount.pp = query['records'][0]['Permit_Pmt__c']
    thisAccount.ppSTAT = setFrontEndStatus(query['records'][0]['Cash_Permit_Pmt_Status__c'])
    thisAccount.fp = query['records'][0]['Cash_Final_Pmt__c']
    thisAccount.fpSTAT = setFrontEndStatus(query['records'][0]['Cash_Final_Pmt_Status__c'])
    ####################################################################################################
    #want to find which of the three possible payments needs to be paid next and set it as the next duepayment
    if thisAccount.dpSTAT == app_settings['DUE_STATUS'] or thisAccount.dpSTAT == app_settings['NOT_DUE_STATUS'] or thisAccount.dpSTAT == ' ':
        thisAccount.duePayment = app_settings['DOWN_PAYMENT_CONST']
        return thisAccount
    elif thisAccount.ppSTAT == app_settings['DUE_STATUS'] or thisAccount.ppSTAT == app_settings['NOT_DUE_STATUS'] or thisAccount.ppSTAT == ' ':
        thisAccount.duePayment = app_settings['PERMIT_PAYMENT_CONST']
        return thisAccount
    elif thisAccount.fpSTAT == app_settings['DUE_STATUS'] or thisAccount.fpSTAT == app_settings['NOT_DUE_STATUS'] or thisAccount.fpSTAT == ' ':
        thisAccount.duePayment = app_settings['FINAL_PAYMENT_CONST']
        return thisAccount
    else:
        thisAccount.duePayment = "NA"
    return thisAccount

#invalidEmail was given ask for email
@application.route('/InvalidName', methods = ['GET', 'POST'])
def InvalidName():
    #instantiate a connetion to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #instantiate the form
    thisform = nameForm()
    #this statement will run if the form validates after the submit button is pressed
    if thisform.validate_on_submit():
        #data taken from the input in the form
        email = thisform.name.data
        #query salesforce in order to get the project Id and some account information
        query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
        #if there is either no contact associated with that email or no project associated with the contact that holds that email this statement will run
        if query['totalSize'] == 0 or query['records'][0]['Projects__r'] == None:
            #this will redirect the user to the same form and an error message will be displayed saying the email was invalid and they will be prompted for email again
            return redirect(url_for('InvalidName'))
        #this statement will run only when there are more than 1 projects associated with the contact that holds that email
        elif query['records'][0]['Projects__r']['totalSize'] > 1:
            #set a session variable to hold the email address
            session['email'] = email
            #redirect to a page that lists all the projects under than contact so customer can choose
            return redirect(url_for('multipleRecords', email = email, query = query))
        #this statement will run if there is exactly one project associated with that email address
        elif query['records'][0]['Projects__r']['totalSize'] == 1:
            #set a session variable to hold that email
            session['email'] = email
            #you successfully have a project Id now so you can move on tp the payment portal for that ID
            return redirect(url_for('passObjID', id = query['records'][0]['Projects__r']['records'][0]['Id']))
    return render_template('Invalid.html', form = thisform)

#more than one project exists for the given contact customer must choose which project they would like to pay for
@application.route('/multipleRecords/<email>')
def multipleRecords(email):
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'] , domain = 'test')
    #query salesfore for the account and projects data associated with that contact
    query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +email+ "')")
    #instantiate a list to hold projects
    accountList = list()
    #for loop that will go through all of the projects and create dictionaries holding there ID's and names and append them to the above list so they may be sent to the front end to be displayed to the customer
    for i in range(query['records'][0]['Projects__r']['totalSize']):
        account_dict = {'Name':query['records'][0]['Projects__r']['records'][i]['Name'], 'ID': query['records'][0]['Projects__r']['records'][i]['Id']}
        accountList.append(account_dict)
    return render_template('multipleRecordsNew.html', accounts = accountList)

#create a json to be sent in the request to dwolla for a customer whose current charge is under 5k
# because of this the custoemr doesnt need to be veriffied at this time
def create_unverified_dwolla_request_body():
    #instantiate connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #get contact data from salesforce
    name_address = sf.query("select FirstName, LastName, name, email from contact where email LIKE '%" + session['email'] + "%'")
    # this will run if only one contact is returned
    # technically this should always run unless the email is invalid which would have been caught earlier
    # because no two people can share the same email so this would only have an error if there was
    # a data integrity problem in salesforce
    if name_address['totalSize'] == 1:
        # set variables to hold data queried from salesforce ##################
        first_name_from_sf = name_address['records'][0]['FirstName']
        last_name_from_sf = name_address['records'][0]['LastName']
        email_from_sf = name_address['records'][0]['Email']
        #####################################################################
        #create a request body that will be sent in a post request to dwolla this is in json format
        customer_create_request_body ={
        'firstName':first_name_from_sf,
        'lastName': last_name_from_sf,
        'email': email_from_sf,
        }
        return customer_create_request_body
    else:
        alert("Something Went Wrong")
        return redirect(url_for('newStart'))

#this method runs when we were not able to verify the customer based of the information we got from salesforce and from the validation form
# we dont want to provide the customer with an error message in order to ensure a better user flow because of this we tell them payment is pendign and
# we retrieve their bank account and routing numbers from plaid and put them in salesforce so we can run the transfer manually
def customer_not_verified_encode_upload_send(customer_create_request_body):
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    query = sf.query("select Name, ID, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '" +customer_create_request_body['email']+ "')")
    name = query['records'][0]['Name']
    proj_ID = query['records'][0]['Projects__r']['records'][0]['Id']
    # call the plaid api auth endpoint to retrieve the user bank account number and routing number
    auth_response = client.Auth.get(session['access_token'])
    #this for loop is used so that we can go through all bank accounts associated with the login the user entered and match it
    # with the accocunt they clicked in the GUI so we can get the correct account number
    for i in range(len(auth_response['numbers']['ach'])):
        #this statement will only run when the accountID matches the account in the plaid auth response
        if auth_response['numbers']['ach'][i]['account_id'] == session['ACCOUNT_ID']:
            #set local variable for bank account number
            account_num = auth_response['numbers']['ach'][i]['account']
            #set local variable for vank routing number
            routing_num = auth_response['numbers']['ach'][i]['routing']
            #put the bank accounts routing number into salesforce in the encrypted field created for the account number
            sf.project__c.update(proj_ID, {'Bank_Account_Number__c': account_num})
            #put the routing number into salesforce in the encrypted field created for the routing number
            sf.project__c.update(proj_ID, {'Routing_Number__c': routing_num})
            #this will send an email to the address in the first parameter including information about the customer who could not be verified, this works
            # as an alert that the payment must be done MANUALLY
            email_sender("nathan@certasun.com", "verification fail", name + " proj ID: " + str(proj_ID), 0)
    return

#creates the json to be sent to dwolla in order to create a verified customer with data taken from salesforce not plaid
#takes in 2 parameters
    #1: L4S = last 4 of social that was taken frrom the validation form
    #2: DOB = Date of Birth that was also taken from the validation form
@application.route('/create_verified_dwolla_customer_from_SF', methods = ['GET', 'POST'])
def create_verified_request_body_from_SF(L4S, DOB):
    #instantiate a connection to salesforce api
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #query salesforce for additional data needed on customer
    name_address = sf.query("select name, MailingAddress, email from contact where email LIKE '%" + session['email'] + "%'")
    #this statement should always run as no two people can have the same email address but as long as their are not two Contacts
    # in salesforce with the same email this will run
    if name_address['totalSize'] == 1:
        #setting local variables from the data that was pulled from salesforce ############
        full_name_from_sf = name_address['records'][0]['Name']
        full_name_list = full_name_from_sf.split()
        first_name_from_sf = full_name_list[0]
        last_name_from_sf = full_name_list[1]
        email_from_sf = name_address['records'][0]['Email']
        street = name_address['records'][0]['MailingAddress']['street']
        city = name_address['records'][0]['MailingAddress']['city']
        state = name_address['records'][0]['MailingAddress']['stateCode']
        zip = name_address['records'][0]['MailingAddress']['postalCode']
        ################################################################################
        #create a json that will act as the request body to be sent in the post request to dwollas customer endpoint
        customer_create_request_body ={
        'firstName':first_name_from_sf,
        'lastName': last_name_from_sf,
        'email': email_from_sf,
        'type':'personal',
        'address1': street,
        'city': city,
        'state': state,
        'postalCode': zip,
        'dateOfBirth': DOB,
        'ssn': L4S
        }
        return customer_create_request_body
    else:
        alert("Something Went Wrong")
        return redirect(url_for('newStart'))

#create and attach a funding source to the given customer
def create_customer_funding_source(customer_url, request_body):
    #get the giiven customers funding sources
    # this must be done because we cannot add an already existing funding source to a customer
    current_customers_funding_sources = app_token.get('%s/funding-sources' % customer_url)
    #check if the funding source you wish to create is actually one that already exists
    # loop through all of the funding sources retrieved from the above get request to dwollas funding-sources endpoint
    for i in range(len(current_customers_funding_sources.body['_embedded']['funding-sources'])):
        #this statement will run if the name of the funding source in dwolla matches the name that we pulled from the bank account chosen in the plaid GUI by the customer
        if current_customers_funding_sources.body['_embedded']['funding-sources'][i]['name'] == request_body['name']:
            #set the funding source url endpoint to that funding source that matched
            customer_funding_source_url = current_customers_funding_sources.body['_embedded']['funding-sources'][i]['_links']['self']['href']
            #return said funding source
            return customer_funding_source_url
    #funding source doesnt alreay exist
    try:
        #post request to dwolla funding source endpoint to add a fundign source to the custoemr
        customer_funding_source = app_token.post('%s/funding-sources' % customer_url, request_body)
        #set funding source endpoint to the endpoint that is returned so we may use it later in the transfer request
        customer_funding_source_url = customer_funding_source.headers['location']
    #there was an error in creating the funding source so we will set the transfer status to an Error message
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

#method to actually initiate the transfer between the customers funding source and the certasun funding source
# takes in 1 parameter which is a json that holds data needed to initiate transfer
def createTransfer(transfer_request_body):
    try:
        #get balance from plaid
        balance_response = client.Accounts.balance.get(session['access_token'])
    except plaid.errors.PlaidError as e:
        session['transfer_status'] = "Balance Check Fail"
        return session['transfer_status']
    #match up to the account chosen account by first looping through all the bank accounts of that customer returned by plaud
    for i in range(len(balance_response['accounts'])):
        #this will run when we find the bank account that matches the one chosen by the customer in the GUI
        if balance_response['accounts'][i]['account_id'] == session['ACCOUNT_ID']:
            balance_index = i
            break
    #make sure that the custoemrs available balance according to plaid is more than the charge amount
    ###########################Change back right now just setup for testing because balance in plaid is only 200 and we need to test large transactions
    if  app_settings['PLAID_BALANCE'] < session['passAccount']['chargeAmount']:#balance_response['accounts'][balance_index]['balances']['available'] < session['passAccount']['chargeAmount']:
    ###################################################################################################################
    #set a session variable to be checked later showing that not to initiate transfer because it will bounce
        session['transfer_status'] = 'Insufficient Funds'
        return session['transfer_status']
    #balance is higher than charge
    else:
        try:
            #post request to dwolla transfers endpoint to initiate transfer, then get the transfer statuc
            transfer = app_token.post('transfers', transfer_request_body)
            transfer_url = transfer.headers['location']
            getTransfer = app_token.get(transfer_url)
            transfer_status = getTransfer.body['status']
            session['transfer_status'] = transfer_status
        except Exception as ex:
            session['Validation_Error'] = ex.body['_embedded']['errors'][0]['message']
            session['transfer_status'] = 'Transfer could not be initiated'
            transfer_status = session['Validation_Error']
        return transfer_status

#method that actually makes the post request to dwolla to create a customer
def create_verified_dwolla_customer():
    #check if customer exists in dwolla, by sending a get request to dwollla custoemr endpoint with a search parameter of the customers email set earlier
    customer_response = app_token.get('customers', search = session['email'])
    #if charge is above our limit for even a verified customer we encrypt user data and store to be entered manually
    # because there is no point in even attempting the transaction it will fail
    if session['passAccount']['chargeAmount'] > app_settings['DWOLLA_VERIFIED_LIMIT']:
        #create the request body so we can send data to the manual function
        customer_request_body = create_unverified_dwolla_request_body()
        #send the request body to the manual function
        customer_not_verified_encode_upload_send(customer_request_body)
        #set two session variables that will be checked later in order to tell what happened here
        session['verification_status'] = 'unverified_manual_needed'
        session['create_customer_status'] = 'NA'
        return
    ##Charge under Dwolla veriffied limit so we will try to run it through dwolla
    else:
        #customer already exists in dowlla
        if customer_response.body['total'] > 0:
            #set the customers url to a local variable from the response from dwolla
            customer_url =  customer_response.body['_embedded']['customers'][0]['_links']['self']['href']
            #set session variable to be checked later in logic
            session['create_customer_status'] = 'Already In System'
            # this will only run if custoemr is verified
            if customer_response.body['_embedded']['customers'][0]['status'] == 'verified':
                #set session variable to be used in logic later
                session['verification_status'] = 'verified'
            #customer is unverified but already exists and must be updated to verified because charge amount is above unverified limit
        elif session['passAccount']['chargeAmount'] > app_settings['DWOLLA_UNVERIFIED_LIMIT'] and customer_response.body['_embedded']['customers'][0]['status'] == 'unverified':
                #create the json to be sent in the request
                customer_create_request_body = create_verified_request_body_from_SF()
                #make a post request to dwolla in an attempt to upgrade the customers status to verified
                update = app_token.post(customer_url, customer_create_request_body)
                #customer update failed encrypt data and store for manual entry
                if update.body['status'] == 'unverified':
                    customer_not_verified_encode_upload_send(customer_create_request_body)
                    #set session variable to be checked later
                    session['verification_status'] = 'unverified_manual_needed'
                    return
        #custoemr does not already exist
        else:
            #customer doesnt exist and charge is less than 5k so no need to verify
            if session['passAccount']['chargeAmount'] < app_settings['DWOLLA_UNVERIFIED_LIMIT']:
                    customer_create_request_body =create_unverified_dwolla_request_body()
            #customer doesnt exist and charge is more than 5k so customer must be verified
            else:
                    customer_create_request_body = create_verified_request_body_from_SF()
            try:
                #post request to dwolla to create the custoemr
                customer = app_token.post('customers', customer_create_request_body)
                customer_url = customer.headers['location']
                pp.pprint(customer.body)
                session['create_customer_status'] = 'Passed'
                if customer.body['_embedded']['customers'][0]['status'] == 'verified':
                    session['verification_status'] = 'verified'
                else:
                    session['verification_status'] = 'unverified_manual_needed'
            except Exception as e:
                session['create_customer_status'] = 'Failed'
                return
        #use customer url returned by request to get customer info
        get_customer = app_token.get(customer_url)
        #customer must be verified
        if session['passAccount']['chargeAmount'] >= app_settings['DWOLLA_UNVERIFIED_LIMIT']:
            #verification attempt failed data encrypted and stored for manual entry
            if get_customer.body['status'] == 'unverified' and 'update' not in locals():
                customer_not_verified_encode_upload_send(customer_create_request_body)
                session['verification_status'] = 'unverified_manual_needed'
            #customer verification was successful
            elif get_customer.body['status'] == 'verified':
                session['verification_status'] = 'verified'
        #customer doesnt need to be verified
        elif session['passAccount']['chargeAmount'] < app_settings['DWOLLA_UNVERIFIED_LIMIT']:
            #customer isnt verified but its ok dwolla can still handle transaction because the charge is under 5k
            if get_customer.body['status'] == 'unverified':
                session['verification_status'] = 'unverified_manual_not_needed'
        return customer_url

#called by PLAID lINK
def pending_Dwolla():
    #get the custoemr url by either retrieving the customer or creating a new one
    customer_url = create_verified_dwolla_customer()
    #creation of customer failed because of an exception sent back by dwolla when making the post request
    if session['create_customer_status'] == 'Failed':
        #set local variable to return showing that there was an error
        transfer_status = 'Failed to create customer'
        #set same error message as a session variable to access from other methods
        session['transfer_status'] = transfer_status
        #return error message to front end
        return transfer_status
    #verification failed so transaction must be handled manually
    elif session['verification_status'] == 'unverified_manual_needed':
        #set the session variable for the error message so in thanks method logic can figure out where to direct customer
        session['transfer_status'] = session['verification_status']
        #return that message to the front end
        return session['transfer_status']
    #if the program made it this far then the customer was created successfully and verified if Needed
    #get the plaid token that has been previously stored in a session variable
    plaid_token = session['access_token']
    #get the plaid account id that was also stored previously in a session variable
    plaid_account_id = session['ACCOUNT_ID']
    #attempt to exchange your plaid token with dwolla for a dwolla token
    # and catch the exception if something goes wrong
    try:
        dwolla_response = client.Processor.dwollaBankAccountTokenCreate(plaid_token, plaid_account_id)
    except Exception as e:
        # raise an alert on the front end that something went wrong
        alert(e)
        # set the transfer status to an error code this will redirect you on the front end to a page that gives error message to customer
        session['transfer_status'] == "Error Connecting to Bank Account"
        return session['transfer_status']
    #if program made it this far then you successfully exchanged your plaid token with dwolla
    # set a local variable to the dwolla token
    processor_token = dwolla_response['processor_token']
    #gets account# and routing from plaid in order to find the name of the bank account to set in dwolla
    ################### need to change dont want more than 1 auth call because we are charged for it
    auth_response = client.Auth.get(session['access_token'])
    ###########################
    #loop through all the account that the customer has at that bank
    for i in range(len(auth_response['accounts'])):
        #this will run when account in auth response matches account chosen by customer in GUI
        if auth_response['accounts'][i]['account_id'] == session['ACCOUNT_ID']:
            index = i
            break
    #create a request body to be sent to the dwolla funding source endpont this is a json
    funding_source_request_body = {
      'plaidToken' : processor_token
      ,'name' : auth_response['accounts'][index]['name']
    }
    #create the funding source
    customer_funding_source_url = create_customer_funding_source(customer_url, funding_source_request_body)
    #Error resulted from an exception from dwolla after post request from funding source
    # return this error message to front end so it redirects to correct page to tell customer message
    if customer_funding_source_url == 'Error linking to Bank Account':
        return customer_funding_source_url
    #ccreated funding source successfully
    else:
        #get Certasun funding source from dwolla
        account_funding_source_url = getMasterAccountFundingSourceURL()
        #format the charge amount into the correct format for the dwolla request body
        Dwolla_Charge = str('{0:.2f}'.format(session['passAccount']['chargeAmount']))
        #create the request body to be sent to dwollas transfer endpoint this is json
        transfer_request_body = {
                    '_links': {
                        'source': {
                        #holds the endpoint for the customers bank account where funds will be taken from
                            'href': customer_funding_source_url
                        },
                        'destination': {
                        #holds endpoint of Certasun bank account where funds will be transfereed to
                            'href' : account_funding_source_url
                        }
                    },
                    #holds the amount to be transfered from the customers bank accound to the certasun bank account
                    #and the currency which will always be in USD
                    'amount':{
                        'currency' : 'USD',
                        'value' : Dwolla_Charge
                    },
                    #added metadata so we are able to pull more information from webhooks
                    'metadata': {
                    #payment_type = which payment is it for ex. Down Payment
                    'payment_type' : session['passAccount']['duePayment'],
                    #holds proj_ID from salesforce
                    'proj_ID': session['passAccount']['ID']
                    }
            }

        #initiate transfer and return the status
        transfer_status = createTransfer(transfer_request_body)
        return transfer_status

#method called by PLAID LINK
@application.route('/get_access_token_Dwolla', methods=['GET','POST'])
def get_access_token_Dwolla():
    #public token and accountID are returned by the plaid link

  public_token = request.form['public_token']
  ACCOUNT_ID = request.form['account_id']
  try:
      #public token given by plaid link is exchanged for an access token via the plaid API this
    # access token will eventually be exchanged with dwoll in order to create a funding source
      exchange_response = client.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    session['transfer_status'] = 'Verification Problem'
    return jsonify(format_error(e))
    #get the access token from the Plaid API response
  access_token = exchange_response['access_token']
  #set a session variable for the access token to be accessed by other methods
  session['access_token'] = access_token
  #set a session variable for the account ID to be accessed by other methods
  session['ACCOUNT_ID'] = ACCOUNT_ID
  #PLaid was successful now going on to dwolla
  transfer_status = pending_Dwolla()
  return "", 200 #render_template('testCSS.html', accountobj = toOBJ(session['passAccount']))

#This method is called by the front end to see if there were any errors in the payment process
# if there were the customer will be redirected to the error screen with an error message
# otherwise they will be pushed to the thank you payment pending screen
@application.route('/sessVars')
def getSessVars():
    if session['Validation_Error'] != 'No Error':
        return session['Validation_Error']
    else:
        return 'No Error'

#takes an email and returns the corresponding project ID queried from salesforce
def get_proj_from_sf(email):
    #instantiate salesforce connection
    sf = Salesforce(sf_user +".plaidtest", sf_pass, sf_token, domain = 'test')
    #query salesforce databse for proj_ID
    query = sf.query("select Name, (select id, Name from projects__r) from account where ID IN (select AccountId from contact where contact.email  = '"+email+"')")
    #set a local variable for the project ID quiered from salesforce to be returned by this method
    proj_ID = query['records'][0]['Projects__r']['records'][0]['Id']
    return proj_ID

#takes in a project ID and a payment type and status and changes the payment status for that payment type for that project to the input
def change_payment_status_in_sf(payment_type, proj_ID, change_to):
    #instantiate a connection to salesforce
    sf = Salesforce(app_settings['SF-USER'] +".plaidtest", app_settings['SF-PASS'], app_settings['SF-TOKEN'], domain = 'test')
    #this statement will run if the payment status that must be changed which is the parament: payment_type
    # is the down payment
    if payment_type == app_settings['DOWN_PAYMENT_CONST']:
        #change the value for the down payment status equal to the parameter: change_to
        sf.project__c.update(proj_ID, {'Cash_Down_Pmt_Status__c': change_to})
    #this statement will only run if the payment type taken in as a parameter is equal to PERMIT PAYMENT
    elif payment_type == app_settings['PERMIT_PAYMENT_CONST']:
        #change the value of the permit payment status to the parameter change_to
        sf.project__c.update(proj_ID, {'Cash_Permit_Pmt_Status__c': change_to})
    #this statement will only run if the parameter payment_tpye: is equal to FINAL PAYMENT
    elif payment_type == app_settings['FINAL_PAYMENT_CONST']:
        #change the value of the permit final payment status equal to the parameter change_to
        sf.project__c.update(proj_ID, {'Cash_Final_Pmt_Status__c': change_to})
    else:
        #if the payment type parameter was not equal to any of the available options then ERROR will be returned
        return "ERROR"
    #otherwise PASS will be returned in order to indicate a successful sf update
    return "PASS"

#creates an email from info given and sends
#parameters:
    #mail_to: email address to send the email to
    #sub: subject of the email
    #text: plaintext part of the email
    #html: html alternative email content
def email_sender(mail_to, sub, text, html):
    #instantiate an EmailMessage object
    msg = EmailMessage()
    ##Set data for email message
    msg['From'] = gmailaddress
    msg['To'] = mail_to
    msg['Subject'] = sub
    #set the plaintext of the email
    msg.set_content(text)
    #if there is no html content for the email this method will be called with a zero in the place
    #where the html content goes in the method call, if this is true then an html alternative will not be set for the
    #email messages
    #otherwise you will take the data passed into the message inn the html spot and add an alternative content to the email
    if html != 0:
        msg.add_alternative(html, subtype = 'html')
    #start up the smtp server
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    #start tls on the server which is encrypted email
    mailServer.starttls()
    #login to the email account to send the message from
    mailServer.login(gmailaddress, gmailpassword)
    #send the message
    mailServer.send_message(msg)
    #shutdown the mailserver
    mailServer.quit()
    return




################PLAID METHODS####################
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
