import streamlit as st
from database import get_connection


st.title("🛒 Sales Management")
st.write("Add a new customer sale")


# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please login first from the main page.")
    st.stop()


user = st.session_state.get("user")

if user is None:
    st.warning("User session not found. Please logout and login again.")
    st.stop()


# Admin branch
branch_id = user["branch_id"]

# Customer details
name = st.text_input("Customer Name")
mobile_number = st.text_input("Mobile Number")

product_name = st.selectbox(
    "Product",
    ["DS", "DA", "BA", "FSD"]
)

gross_sales = st.number_input(
    "Gross Sales",
    min_value=0.0,
    step=100.0
)


# Add Sale
if st.button("Add Sale"):

    if not name or not mobile_number:
        st.error("Please enter customer name and mobile number.")

    elif gross_sales <= 0:
        st.error("Gross sales must be greater than 0.")

    else:

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO customer_sales
            (branch_id, sale_date, name, mobile_number,
             product_name, gross_sales, status)
            VALUES (%s, CURDATE(), %s, %s, %s, %s, 'Open')
        """

        cursor.execute(
            query,
            (
                branch_id,
                name,
                mobile_number,
                product_name,
                gross_sales
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        st.success("Sale added successfully!")