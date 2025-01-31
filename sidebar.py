import os
import sqlite3
from selenium.webdriver.common.by import By

def get_today(driver):
    month_year = driver.find_elements(By.XPATH,"//span[@class='current']")[0]
    month_link = month_year.find_element(By.XPATH, ".//a")
    month,year = month_link.text.split()

    today_cell = driver.find_element(By.XPATH, "//td[contains(@class, 'today')]")
    today_date = today_cell.find_element(By.XPATH,".//a").text

    return today_date,month,year

def sidebar(driver,sql_path,db_path):

    toggle_button = driver.find_element(By.XPATH,"//i[@id='sidepreopen-control']")
    toggle_state = True if toggle_button.get_attribute("aria-expanded") == "true" else False

    if not toggle_state:
        toggle_button.click()

    # date,month,year = get_today(driver)
    # current_date = date+" "+month+" "+year

    upcoming_events = []
    # upcoming_events.append(current_date)

    events_toggle = driver.find_elements(By.XPATH,"(//div[@class='event'])")

    for event in events_toggle:
        event_link = event.find_element(By.XPATH,".//a[@data-action='view-event']")
        date_div = event.find_element(By.XPATH,".//div[@class='date']")
        date_cell = date_div.find_element(By.XPATH,".//a")
        if len(date_cell.text.split())==1:
            event_date_formatted = 'Tomorrow'
        else:
            the_day,the_num,the_month = date_cell.text.split()
            the_day = the_day[:-1]
            event_date_formatted = the_day+" "+the_num+" "+the_month
        upcoming_events.append([event_link.text,event_date_formatted])

    convert_contents_to_sql(upcoming_events,sql_path,db_path)

def convert_contents_to_sql(upcoming_events, sql_file_path,db_path):
    with open(sql_file_path, 'w') as f:
        f.write("CREATE TABLE subjects_table (upcoming_events TEXT, upcoming_events_date TEXT);\n\n")
        
        for content in upcoming_events:
            content_name = content[0]
            content_date = content[1]
            f.write(f"INSERT INTO subjects_table (upcoming_events, upcoming_events_date) VALUES ('{content_name}', '{content_date}');\n")

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