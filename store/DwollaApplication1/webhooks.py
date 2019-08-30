
#webhook event from dwolla that customer verification was successful
#email can be sent to the customer with a link to make that initial down payment
def webhook_customer_verified(customer, request):
    sf = Salesforce(sf_user +".plaidtest", sf_pass, sf_token, domain = 'test')
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


#webhook from dwolla that transfer was successful will update payment status in sf to recieved
#and then send an email
def webhook_bank_transfer_completed(customer, request, transfer):
    proj_ID = transfer.body['metadata']['proj_ID']
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
