import streamlit as st
from auth import authenticate_user
from database import get_connection


st.set_page_config(
    page_title="Sales Intelligence Hub",
    page_icon="📊",
    layout="wide"
)


# Initialize session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    st.title("📊 Sales Intelligence Hub")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = authenticate_user(username, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.user = user

            st.success("Login successful!")
            st.rerun()

        else:
            st.error("Invalid username or password")


# ---------------- DASHBOARD ----------------

else:

    user = st.session_state.user

    st.title("📊 Sales Intelligence Hub")

    st.write(f"Welcome, {user['username']}")

    st.write(f"Role: {user['role']}")

    # Super Admin
    if user["role"] == "Super Admin":

        st.info("You have access to all branches.")

    # Admin
    elif user["role"] == "Admin":

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT branch_name FROM branches WHERE branch_id = %s",
            (user["branch_id"],)
        )

        branch = cursor.fetchone()

        cursor.close()
        connection.close()

        if branch:
            st.info(f"You are assigned to: {branch['branch_name']}")

    # Logout
    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user = None

        st.rerun()