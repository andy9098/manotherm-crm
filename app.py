import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- CONFIGURATION ---
# We now use Streamlit's Secret Manager for the password
ADMIN_USER = st.secrets["general"]["username"]
ADMIN_PASS = st.secrets["general"]["password"]

# --- DATABASE CONNECTION ---
def get_db():
    # Connect to Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn

def get_leads():
    """Fetch data from Google Sheets"""
    conn = get_db()
    # Read the data, treating it as a DataFrame
    df = conn.read()
    return df

def add_lead(name, company, email, phone, status, notes):
    """Add a new row to Google Sheets"""
    conn = get_db()
    df = conn.read()
    
    # Create new row
    new_data = pd.DataFrame([{
        "name": name,
        "company": company,
        "email": email,
        "phone": phone,
        "status": status,
        "notes": notes,
        "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    
    # Combine old data with new data
    updated_df = pd.concat([df, new_data], ignore_index=True)
    
    # Update the Google Sheet
    conn.update(data=updated_df)

# --- LOGIN LOGIC ---
def login_screen():
    st.title("🔒 Manotherm CRM Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Incorrect Credentials")

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="Manotherm CRM", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login_screen()
        return

    # --- APP INTERFACE ---
    with st.sidebar:
        st.write("Logged in: Admin")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
        choice = st.selectbox("Menu", ["View Leads", "Add New Lead"])

    if choice == "Add New Lead":
        st.title("📝 Add New Lead")
        with st.form("entry"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name")
            company = c1.text_input("Company")
            email = c1.text_input("Email")
            phone = c2.text_input("Phone")
            status = c2.selectbox("Status", ["New", "Contacted", "Proposal", "Won", "Lost"])
            notes = st.text_area("Notes")
            if st.form_submit_button("Save"):
                add_lead(name, company, email, phone, status, notes)
                st.success("Lead Saved to Cloud!")

    elif choice == "View Leads":
        st.title("📊 Pipeline")
        try:
            df = get_leads()
            st.dataframe(df)
        except Exception as e:
            st.error("Could not connect to Google Sheet. Check Secrets.")

if __name__ == '__main__':
    main()