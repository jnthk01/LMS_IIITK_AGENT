import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def individual_subject(driver,link,individual_subjecs_file_path_to_excel):
    driver.execute_script(f"window.open('{link}');")

    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])

    wait = WebDriverWait(driver, 10)

    sections_list_ul = wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='topics']")))
    time.sleep(2)

    li_elements = sections_list_ul.find_elements(By.XPATH, "./li")
    time.sleep(2)

    type_list = {
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/folder/1703654757/icon":"Module",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/core/1703654757/f/pdf-24":"PDF",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/assign/1703654757/icon":"Assignment",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/forum/1703654757/icon":"Announcements",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/attendance/1703654757/icon":"Attendance",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/core/1703654757/f/powerpoint-24":"Powerpoint",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/vpl/1703654757/icon":"VPL",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/core/1703654757/f/text-24":"TEXT",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/core/1703654757/f/png":"PNG",
        "https://lms.iiitkottayam.ac.in/theme/image.php/moove/core/1703654757/f/document-24":"DOCUMENT"
    }

    subjects_knowledge_base = {}
    for li in li_elements:
        div_content = li.find_element(By.XPATH,'.//div[@class="content"]')
        try:
            div_access = div_content.find_element(By.XPATH,'.//h3')
        except Exception as e:
            continue
        div_access_name = div_access.get_attribute('class') # sectionname accesshide    sectionname
        if "accesshide" in div_access_name:
            section_name = "General"
        else:
            section_name = div_access.find_element(By.XPATH,".//a").text
        
        if "topic" in section_name.lower():
            continue

        content_type_imgs = div_content.find_elements(By.XPATH,".//img")
        content_type_names = div_content.find_elements(By.XPATH,".//span[@class='instancename']")
        content_links = div_content.find_elements(By.XPATH,".//a[@class='aalink']")

        if section_name not in subjects_knowledge_base:
            subjects_knowledge_base[section_name] = []

        for type_imgs,content_type_name,content_link in zip(content_type_imgs,content_type_names,content_links):
            con_type = type_list[type_imgs.get_attribute("src")] if type_imgs.get_attribute("src") in type_list else "SPECIAL"
            con_name = content_type_name.text
            con_name = con_name.split("\n")[0] if "\n" in con_name else con_name
            con_link = content_link.get_attribute("href")
            content_entry = {
                "content_type": con_type,
                "content_name": con_name,
                "content_link": con_link,
            }
            if "Module" in con_type:
                module_content = individual_subject_modules(driver,con_link,type_list)
                content_entry['module_content'] = module_content
            else:
                content_entry['module_content'] = []
            subjects_knowledge_base[section_name].append(content_entry)
    
    driver.close()
    individual_subject_to_excel(subjects_knowledge_base,individual_subjecs_file_path_to_excel)

def individual_subject_modules(driver, content_link,type_list):
    driver.execute_script(f"window.open('{content_link}');")
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])

    wait = WebDriverWait(driver, 10)

    div_contents_main = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ygtvc1"]')))
    time.sleep(2)
    div_contents = div_contents_main.find_elements(By.XPATH,".//div[@class='ygtvitem']")
    individual_contents = []
    for item in div_contents:
        a_link_tag = item.find_element(By.XPATH,'.//a')
        a_link = a_link_tag.get_attribute('href')
        img_type = type_list.get(a_link_tag.find_element(By.XPATH, './/img').get_attribute('src'), "Document")
        mod_file_name = a_link_tag.find_element(By.XPATH,'.//span[@class="fp-filename"]').text
        content_entry = {
            "module_content_type": img_type,
            "module_content_name": mod_file_name,
            "module_content_link": a_link,
        }
        individual_contents.append(content_entry)

    driver.close() 
    driver.switch_to.window(window_handles[-2])
    return individual_contents


def individual_subject_to_excel(subjects_knowledge_base,save_path):
    rows = []
    for section, contents in subjects_knowledge_base.items():
        for content in contents:
            if "module_content" in content and content["module_content"]:
                for module in content["module_content"]:
                    rows.append([
                        section,
                        content["content_type"],
                        content["content_name"],
                        content["content_link"],
                        module["module_content_type"],
                        module["module_content_name"],
                        module["module_content_link"]
                    ])
            else:
                rows.append([
                    section,
                    content["content_type"],
                    content["content_name"],
                    content["content_link"],
                    None,
                    None,
                    None
                ])

    df = pd.DataFrame(rows, columns=[
        "Section",
        "Content_Type",
        "Content_Name",
        "Content_Link",
        "Module_Content_Type",
        "Module_Content_Name",
        "Module_Content_Link"
    ])

    df.to_excel(save_path, index=False, engine='openpyxl')
    # convert_to_sql(save_path,individual_subjecs_file_path_to_sql,individual_subjecs_file_path_to_db)

    # if os.path.exists(save_path):
    #     os.remove(save_path)

# def convert_to_sql(save_path,individual_subjecs_file_path_to_sql,individual_subjecs_file_path_to_db):
#     df = pd.read_excel(save_path, engine='openpyxl')

#     with open(individual_subjecs_file_path_to_sql, 'w') as f:
#         columns = ', '.join(df.columns)
#         f.write(f"CREATE TABLE subjects_table ({columns});\n\n")
        
#         for _, row in df.iterrows():
#             values = ', '.join([f"NULL" if val is None else f"'{str(val)}'" for val in row.values])
#             f.write(f"INSERT INTO subjects_table ({columns}) VALUES ({values});\n")
    
#     convert_to_db(individual_subjecs_file_path_to_sql,individual_subjecs_file_path_to_db)


# def convert_to_db(sql_file_path,database_path):
#     conn = sqlite3.connect(database_path)
#     cursor = conn.cursor()

#     with open(sql_file_path, "r") as f:
#         sql_script = f.read()
#         cursor.executescript(sql_script)
    
#     conn.commit()
#     conn.close()

#     if os.path.exists(sql_file_path):
#         os.remove(sql_file_path)