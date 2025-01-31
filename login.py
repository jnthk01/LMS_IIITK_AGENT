import os
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def login():
    load_dotenv()

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service,options=chrome_options)
    driver.maximize_window()

    driver.get('https://lms.iiitkottayam.ac.in/login/')
    username = os.getenv('USER_NAME')
    password = os.getenv('PASS_WORD')

    username_field =  driver.find_element(By.XPATH,"//input[@id='username']")
    password_field = driver.find_element(By.XPATH,"//input[@id='password']")

    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = driver.find_element(By.XPATH,"//button[@id='loginbtn']")

    login_button.click()

    return driver