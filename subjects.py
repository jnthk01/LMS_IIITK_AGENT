import os
import time
import sqlite3
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def subjects(driver,sql_path,db_path):
    wait = WebDriverWait(driver,10)
    
    show_all_button = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="paging-control-limit-container-2"]/div/button')))
    show_all_button_expanded = True if show_all_button.get_attribute("aria-expanded") == "true" else False

    if not show_all_button_expanded:
        show_all_button.click()

    drop_down_menu_show = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='dropdown-menu show']")))
    drop_down_menu_show_a_tags = drop_down_menu_show.find_elements(By.TAG_NAME, "a")

    drop_down_menu_show_a_tags[-1].click()
                

    time.sleep(5)
    subject_card_main = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-region='paged-content-page']//div[@role='list']")))
    time.sleep(2)
    subjects_data = []
    for i,sub_card_main in enumerate(subject_card_main):
        index = i+1
        add_format = f'//*[@id="page-container-2"]/div[{index}]/div/div'
        subject_cards = sub_card_main.find_elements(By.XPATH,add_format)
        time.sleep(2)
        for card in subject_cards:
            sub_type = card.find_element(By.XPATH, ".//span[contains(@class, 'categoryname')]").text
            if "BATCH" not in sub_type:
                continue
            
            subject_link = card.find_elements(By.XPATH,".//a")[0].get_attribute("href")
            subject_name = card.find_element(By.XPATH, ".//span[@class='multiline']").text
            subjects_data.append([subject_name,subject_link])
    convert_subjects_to_sql(subjects_data,sql_path,db_path)

    return subjects_data


def convert_subjects_to_sql(subjects_data, sql_file_path,db_path):
    with open(sql_file_path, 'w') as f:
        f.write("CREATE TABLE subjects_table (subject_names TEXT, subject_links TEXT);\n\n")
        
        for subject in subjects_data:
            subject_name = subject[0]
            subject_link = subject[1]
            f.write(f"INSERT INTO subjects_table (subject_names, subject_links) VALUES ('{subject_name}', '{subject_link}');\n")

    convert_to_db(sql_file_path,db_path)


def convert_to_db(sql_file_path,database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    with open(sql_file_path, "r") as f:
        sql_script = f.read()
        cursor.executescript(sql_script)
    
    conn.commit()
    conn.close()

    if os.path.exists(sql_file_path):
        os.remove(sql_file_path)