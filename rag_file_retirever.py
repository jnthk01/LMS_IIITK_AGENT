import os
from selenium import webdriver
from urllib.parse import urlparse, unquote
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def rag_file_retriever(user_type, user_prompt, file_name):

    def get_filename_from_url(url):
       parsed_url = urlparse(url)
       path = parsed_url.path 
       filename = path.split("/")[-1]
       filename = unquote(filename)
       return filename.split("?")[0]
     
    download_dir = os.getcwd()

    if os.path.exists(file_name):
        return file_name

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False, 
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True 
    })

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    download_url = user_prompt

    if "forcedownload" in download_url or "ppt" in user_type.lower():
        driver.get(download_url)

        username = os.getenv('USER_NAME')
        password = os.getenv('PASS_WORD')
        username_field = driver.find_element(By.XPATH, "//input[@id='username']")
        password_field = driver.find_element(By.XPATH, "//input[@id='password']")
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button = driver.find_element(By.XPATH, "//button[@id='loginbtn']")
        login_button.click()
        download_file_name = get_filename_from_url(download_url)
        print("download file name: ",download_file_name)
        while not os.path.exists(os.path.join(download_dir, download_file_name)):
            continue

        downloaded_file = os.path.join(download_dir, download_file_name)
        if downloaded_file != os.path.join(download_dir, file_name):
            os.rename(downloaded_file, os.path.join(download_dir, file_name))

        driver.quit()

    else:
        driver.get(download_url)

        while driver.current_url == download_url:
            continue

        pdf_url = driver.current_url
        downloaded_file = get_filename_from_url(pdf_url)
        print("download file name: ",download_file_name)

        while not os.path.exists(os.path.join(download_dir, downloaded_file)):
            continue

        if downloaded_file != file_name:
            os.rename(os.path.join(download_dir, downloaded_file), os.path.join(download_dir, file_name))

        driver.quit()

    return file_name