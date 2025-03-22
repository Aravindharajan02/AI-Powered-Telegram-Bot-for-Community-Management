import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import pandas as pd

# Initialize Firebase
if not firebase_admin._apps:
    CRED_PATH = os.path.abspath(r"config\serviceAccountKey.json")
    cred = credentials.Certificate(CRED_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Users", "Events", "Chat Logs", "Leaderboard"])

# Dashboard
if page == "Dashboard":
    st.title("📊 AI-Powered Bot Dashboard")

    users_count = len(list(db.collection('users').stream()))
    events_count = len(list(db.collection('events').stream()))
    messages_count = len(list(db.collection('messages').stream()))

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", users_count)
    col2.metric("Total Events", events_count)
    col3.metric("Total Messages", messages_count)

# User Management
elif page == "Users":
    st.title("👥 User Management")
    search_query = st.text_input("Search User (Username or ID)")

    if search_query:
        user_ref = db.collection("users").where("username", "==", search_query).stream()
        user_list = [doc.to_dict() for doc in user_ref]
        if user_list:
            st.write(pd.DataFrame(user_list))
        else:
            st.warning("No matching user found.")

# Event Management
elif page == "Events":
    st.title("🎉 Manage Events")
    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date")
    event_time = st.time_input("Event Time")
    event_description = st.text_area("Event Description")

    if st.button("Add Event"):
        db.collection("events").add({
            "name": event_name,
            "date": datetime.datetime.combine(event_date, event_time),
            "description": event_description
        })
        st.success("Event added successfully!")

    st.write("### Upcoming Events")
    events = db.collection("events").order_by("date").stream()
    for event in events:
        event_data = event.to_dict()
        st.write(f"📅 {event_data['name']} - {event_data['date']}")
        st.write(event_data.get("description", "No description available"))
        st.write("---")
