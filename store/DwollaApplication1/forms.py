from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField
from DwollaApplication0 import app_settings
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
        if self.duePayment == app_settings['DOWN_PAYMENT_CONST']:
            self.chargeAmount = self.dp
            return self.dp
        if self.duePayment == app_settings['PERMIT_PAYMENT_CONST']:
            self.chargeAmount = self.pp
            return self.pp
        if self.duePayment == app_settings['FINAL_PAYMENT_CONST']:
            self.chargeAmount = self.fp
            return self.fp
        return 0

    def toJSON(self):
        return self.__dict__

    def getDuePayment(self):
        if self.dpSTAT == app_settings['DUE_STATUS'] or self.dpSTAT == app_settings['NOT_DUE_STATUS']:
            self.duePayment = app_settings['DOWN_PAYMENT_CONST']
            return app_settings['DOWN_PAYMENT_CONST']
        elif self.ppSTAT == app_settings['DUE_STATUS'] or self.ppSTAT == app_settings['NOT_DUE_STATUS']:
            self.duePayment = app_settings['PERMIT_PAYMENT_CONST']
            return app_settings['PERMIT_PAYMENT_CONST']
        elif self.fpSTAT == app_settings['DUE_STATUS'] or self.fpSTAT == app_settings['NOT_DUE_STATUS']:
            self.duePayment = app_settings['FINAL_PAYMENT_CONST']
            return app_settings['FINAL_PAYMENT_CONST']
        else:
            self.duePayment = "N/A"
        return "N/A"

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
# takes in the status code for payments from SF and returns a more consumer friendly string to display on the front end
def setFrontEndStatus(stat):
    if stat == app_settings['DUE_STATUS']:
        return app_settings['DUE_STATUS']
    elif stat == app_settings['NOT_DUE_STATUS']:
        return ' '
    elif stat == app_settings['IN_FLIGHT_STATUS']:
        return "Pending"
    elif stat == app_settings['RECEIVED_STATUS']:
        return 'Paid'
    elif stat == app_settings['N/A_STATUS']:
        return app_settings['N/A_STATUS']
    else:
        return " "
