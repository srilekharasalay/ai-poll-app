import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

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

# Initialize or get the Google Sheet
@st.cache_data(ttl=5)  # Cache for 5 seconds
def get_sheet_data():
    client = get_gsheet_client()

    # Try to open existing sheet or create new one
    try:
        sheet = client.open("AI Tools Poll Results").sheet1
    except gspread.SpreadsheetNotFound:
        sheet = client.create("AI Tools Poll Results").sheet1
        # Initialize headers
        sheet.append_row(["Name", "Selected Option", "Comments"])

    # Get all records
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# App UI
st.title("🚀 AI Tools Poll with Live Results")

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
    if not name or not selected_option:
        st.warning("Please fill in your name and select an option.")
    else:
        try:
            # Get sheet and append new data
            client = get_gsheet_client()
            sheet = client.open("AI Tools Poll Results").sheet1
            sheet.append_row([name, selected_option, comments])
            st.success("Thank you! Your response has been recorded!")
            # Clear the cache to refresh the data
            get_sheet_data.clear()
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
