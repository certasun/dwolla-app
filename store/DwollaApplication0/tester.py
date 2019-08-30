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
import time
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.interaction import KEY
from pynput.keyboard import Key, Controller
import subprocess
pp = pprint.PrettyPrinter(indent=2)
webdriverpath = os.path.join('\\Users', 'NathanWayne', 'Desktop', 'TestCSVPY', 'chromedriver.exe')
browser = webdriver.Chrome(executable_path = webdriverpath)
wait = WebDriverWait(browser, 3)
browser.get('http://eft-env.7eqxt8c8qq.us-east-2.elasticbeanstalk.com/')
email_field = browser.find_element_by_xpath('//*[@id="name"]')
email_field.send_keys('me1@me.me')
submit = browser.find_element_by_xpath('//*[@id="submit"]')
submit.click()
proj_spot_1 = browser.find_element_by_xpath('//*[@id="page-top"]/header/div/div/table/tbody/tr[1]/td/a')
proj_spot_1.click()
pay_ach_button = browser.find_element_by_xpath('//*[@id="linkButton"]')
pay_ach_button.click()
time.sleep(5)
browser.switch_to_window("link/2.0.285")
agree_button = browser.find_element_by_xpath('//*[@id="plaid-link-container"]/div/div[1]/div/div/div[2]/div[2]/div/button')
agree_button.click()
