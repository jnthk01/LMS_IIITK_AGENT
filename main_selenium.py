import os
from login import login
from sidebar import sidebar
from subjects import subjects
from individual_subject import individual_subject

# 1) Login into the LMS
driver = login()


# 2) Create the directory
folder_db = os.path.join(os.getcwd(),'data_dbs')
if not os.path.exists(folder_db):
    os.makedirs(folder_db)


# 3) OPTIONAL -> GET THE DEADLINES
upcoming_events_file_path = os.path.join(folder_db,'deadline_events.sql')
upcoming_events_file_path_db = os.path.join(folder_db,'deadline_events.db')
if not os.path.exists(upcoming_events_file_path_db):
    sidebar(driver=driver,sql_path=upcoming_events_file_path,db_path=upcoming_events_file_path_db)


# 4) OPTIONAL -> GET THE LIST OF ALL SUBJECTS
subjects_list_file_path = os.path.join(folder_db, 'subjects_list.sql')
subjects_list_file_path_db = os.path.join(folder_db, 'subjects_list.db')
if not os.path.exists(subjects_list_file_path_db):
    subjects(driver=driver,sql_path=subjects_list_file_path,db_path=subjects_list_file_path_db)


# 5) OPTIONAL -> GET THE ENTIRE FOLDERS OF A PARTICULAR SUBJECT
user_selected_subject = "ICS321 Data Warehousing and Data Mining"
user_link = "https://lms.iiitkottayam.ac.in/course/view.php?id=432"

individual_subjecs_file_path_to_excel = f'{user_selected_subject}_individual_subjects.xlsx'
individual_subjecs_file_path_to_sql = os.path.join(folder_db, f'{user_selected_subject}_individual_subjects.sql')
individual_subjecs_file_path_to_db = os.path.join(folder_db, f'{user_selected_subject}_individual_subjects.db')
if not os.path.exists(individual_subjecs_file_path_to_db):
    individual_subject(driver,user_link,individual_subjecs_file_path_to_excel,individual_subjecs_file_path_to_sql,individual_subjecs_file_path_to_db)


input("Enter to close:")

driver.quit()