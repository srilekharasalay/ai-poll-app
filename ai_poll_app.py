import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Google Sheets setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load credentials and create Google Sheets client using Streamlit secrets
@st.cache_resource
def get_gsheet_client():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(credentials)

# Initialize or get the Google Sheet with header check
@st.cache_data(ttl=5)
def get_sheet_data():
    client = get_gsheet_client()
    sheet = client.open("AI Tools Poll Results").sheet1

    # Validate headers
    existing_headers = sheet.row_values(1)
    expected_headers = ["Name", "Selected Option", "Comments", "Timestamp"]

    if existing_headers != expected_headers:
        sheet.clear()
        sheet.append_row(expected_headers)

    # Get all records
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Function to append new response
def append_response(name, selected_option, comments):
    client = get_gsheet_client()
    sheet = client.open("AI Tools Poll Results").sheet1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, selected_option, comments, timestamp])
    get_sheet_data.clear()

# Streamlit UI
st.title("🚀 AI Tools Poll")

st.write("We are gathering your feedback on the best AI tools to improve efficiency, speed, and accuracy. Please vote and share your suggestions!")

# User input fields
name = st.text_input("Your Name:")
options = [
    "Cursor AI",
    "GitHub Copilot",
    "Replit",
    "Claude",
    "Other (Please specify in comments)"
]
selected_option = st.radio("Which AI Tool Do You Recommend?", options)
comments = st.text_area("Additional Suggestions (Optional)")

# Submit response
if st.button("Submit"):
    if not name.strip() or not selected_option.strip():
        st.warning("Please fill in your name and select an option.")
    else:
        poll_data = get_sheet_data()

        # Check for duplicate names (case insensitive)
        if name.strip().lower() in [n.lower() for n in poll_data['Name'].tolist()]:
            st.error("You have already submitted your response. Duplicate entries are not allowed.")
        else:
            try:
                append_response(name.strip(), selected_option.strip(), comments.strip())
                st.success("Thank you! Your response has been recorded!")
            except Exception as e:
                st.error(f"Error saving your response: {str(e)}")

# Show current poll results
try:
    poll_data = get_sheet_data()
    if not poll_data.empty:
        st.subheader("📊 Current Poll Results Table")
        st.dataframe(poll_data)

        # Prepare chart data
        vote_counts = poll_data['Selected Option'].value_counts()
        st.subheader("📈 Live Poll Chart")
        st.bar_chart(vote_counts)
except Exception as e:
    st.error(f"Error loading poll results: {str(e)}")

st.info("Results update automatically every 5 seconds. No need to refresh the page!")
