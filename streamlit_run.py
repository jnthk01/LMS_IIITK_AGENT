import os
import pickle
import pandas as pd
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
import streamlit as st
from login import login
from sidebar import sidebar
from subjects import subjects
from individual_subject import individual_subject

def main_page():
    st.title("LMS Chatbot")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        lms_user_id = st.text_input("Enter your LMS User ID:", type="default")
        lms_password = st.text_input("Enter your LMS Password:", type="password")
        gemini_api_key = st.text_input("Enter your GEMINI API Key:", type="password")

        if st.button("Login"):
            if lms_user_id and lms_password and gemini_api_key:
                os.environ["USER_NAME"] = lms_user_id
                os.environ["PASS_WORD"] = lms_password
                os.environ["GEMINI_API_KEY"] = gemini_api_key

                st.session_state["authenticated"] = True
                st.success("Login successful! You can now use the chatbot.")
            else:
                st.warning("Please provide all the required inputs to proceed.")

    if st.session_state["authenticated"]:
        st.write("Welcome to the LMS Chatbot!")
        
        def setup_driver():
            return login()

        @st.cache_resource
        def setup_llm():
            return ChatGoogleGenerativeAI(
                api_key=os.environ["GEMINI_API_KEY"],
                model="gemini-1.5-flash",
                temperature=0,
                max_tokens=10000,
                timeout=None,
            )

        @st.cache_resource
        def setup_folder():
            folder_db = os.path.join(os.getcwd(), 'data_dbs')
            if not os.path.exists(folder_db):
                os.makedirs(folder_db)
            return folder_db

        @st.cache_resource
        def load_subjects_data(folder_db, _driver):
            subjects_list_file_path = os.path.join(folder_db, 'subjects_list.sql')
            subjects_list_file_path_db = os.path.join(folder_db, 'subjects_list.db')
            if not os.path.exists(subjects_list_file_path_db):
                subjects_data = subjects(driver=_driver, sql_path=subjects_list_file_path, db_path=subjects_list_file_path_db)
                with open('subjects_list.pkl', 'wb') as f:
                    pickle.dump(subjects_data, f)
            else:
                with open("subjects_list.pkl", "rb") as f:
                    subjects_data = pickle.load(f)
            return subjects_data

        folder_db = setup_folder()
        driver = setup_driver()
        llm = setup_llm()
        subjects_data = load_subjects_data(folder_db, driver)

        question = st.text_input("Ask your LMS-related question:", placeholder="e.g., What are the contents of the subject with 'data warehousing'?")

        if question:
            flag = False
            with st.spinner("Processing your query..."):
                prompt = (
                    "You just need to output the numbers 1, 2, or 3. I repeat, only output the numbers 1, 2, or 3. "
                    "In the following given user question, do the following:\n\n"
                    "1. Output '1' if the person is asking about upcoming events or anything related to time.\n"
                    "2. Output '2' if the person is asking for a list of subjects (plural), specifically the name and hyperlink of the subject (nothing about the contents of the subject, only the name and hyperlink). One such example of question is -> Give me the name of subject that has probability in its name\n"
                    "3. Output '3' if the person is asking about the contents inside a particular subject (e.g., modules, files, labs, etc.), referring to a specific subject's details.\n\n"
                    f"Question: {question}"
                )
                output_initial_splitter = llm.invoke(prompt).content

                if output_initial_splitter == '1':
                    upcoming_events_file_path = os.path.join(folder_db, 'deadline_events.sql')
                    upcoming_events_file_path_db = os.path.join(folder_db, 'deadline_events.db')
                    if not os.path.exists(upcoming_events_file_path_db):
                        sidebar(driver=driver, sql_path=upcoming_events_file_path, db_path=upcoming_events_file_path_db)

                    dp_events = "data_dbs/deadline_events.db"
                    db_events = SQLDatabase.from_uri(f"sqlite:///{dp_events}")
                    sql_agent_events = create_sql_agent(llm=llm, db=db_events)
                    prompt = (
                        f"You are a SQL retriever where the table here contains the list of certain events that will take place along with their date. "
                        f"Please answer the question in a clear and well-formatted **string output**. "
                        f"Avoid using markdown syntax. Your response should be concise, structured, and easy to print directly. "
                        f"Question: {question}"
                    )
                    answer = sql_agent_events.invoke(prompt)['output']

                elif output_initial_splitter == '2':
                    dp_sublist = "data_dbs/subjects_list.db"
                    db_sublist = SQLDatabase.from_uri(f"sqlite:///{dp_sublist}")
                    sql_agent_sublist = create_sql_agent(llm=llm, db=db_sublist)
                    prompt = (
                        f"You are a SQL retriever. The table provided contains a list of subjects along with their respective hyperlinks. "
                        f"Your task is to answer the question using this table. Important Instructions: "
                        f"Always include the respective hyperlinks in your answers. Your output must be in a clear and structured **string format** "
                        f"that is easy to understand and print directly. Avoid markdown syntax. "
                        f"Ensure your answer fully addresses the query and includes all requested information. "
                        f"ALSO IF THE USER REQUESTS TO GET ABOUT ALL THE SUBJECTS THEN IT MUST OUTPUT ALL THE CONTENT OF DATABASE ALONG WITH RESPECTIVE HYPERLINK"
                        f"I REPEAT IF THE USER REQUESTS TO GET ABOUT ALL THE SUBJECTS THEN IT MUST OUTPUT ALL THE CONTENT OF DATABASE ALONG WITH RESPECTIVE HYPERLINK"
                        f"Question: {question}"
                    )
                    answer = sql_agent_sublist.invoke(prompt)['output']

                elif output_initial_splitter == '3':
                    flag = True
                    dp_sublist = "data_dbs/subjects_list.db"
                    db_sublist = SQLDatabase.from_uri(f"sqlite:///{dp_sublist}")
                    sql_agent_sublist = create_sql_agent(llm=llm, db=db_sublist)

                    subject_name = sql_agent_sublist.invoke(
                        f"Retrieve the exact name of the subject mentioned in the question. Output the name as a plain string. "
                        f"Question: {question}"
                    )['output']

                    user_selected_subject = subject_name
                    user_link = ""
                    for a, b in subjects_data:
                        if a == user_selected_subject:
                            user_link = b
                            break

                    print(user_selected_subject,user_link)
                    individual_subjecs_file_path_to_excel = os.path.join(folder_db, f'{user_selected_subject}_individual_subjects.xlsx')
                    if not os.path.exists(individual_subjecs_file_path_to_excel):
                        individual_subject(driver, user_link, individual_subjecs_file_path_to_excel)

                    df = pd.read_excel(individual_subjecs_file_path_to_excel)
                    st.dataframe(df, height=500)

                else:
                    answer = "Sorry, I couldn't classify your question."

            if not flag:
                st.text_area("Answer:", answer, height=400)

if __name__ == "__main__":
    main_page()