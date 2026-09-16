import streamlit as st
from database import get_connection


st.title("💰 Payment Management")
st.write("Record a payment for a customer sale")


# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please login first from the main page.")
    st.stop()


user = st.session_state.get("user")

if user is None:
    st.warning("User session not found. Please logout and login again.")
    st.stop()


# Get sales based on user role
connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT sale_id, name, gross_sales, received_amount,
               pending_amount
        FROM customer_sales
        WHERE pending_amount > 0
        ORDER BY sale_id DESC
    """)

else:

    cursor.execute("""
        SELECT sale_id, name, gross_sales, received_amount,
               pending_amount
        FROM customer_sales
        WHERE branch_id = %s
          AND pending_amount > 0
        ORDER BY sale_id DESC
    """, (user["branch_id"],))


sales = cursor.fetchall()

cursor.close()
connection.close()


if not sales:

    st.info("No pending sales available for payment.")

else:

    # Create sale selection
    sale_options = {}

    for sale in sales:
        label = (
            f"Sale #{sale['sale_id']} - "
            f"{sale['name']} - "
            f"Pending: ₹{sale['pending_amount']:.2f}"
        )

        sale_options[label] = sale["sale_id"]


    selected_sale = st.selectbox(
        "Select Sale",
        list(sale_options.keys())
    )

    sale_id = sale_options[selected_sale]

    selected_sale_data = next(
        sale for sale in sales
        if sale["sale_id"] == sale_id
    )


    st.write(
        f"*Gross Sales:* ₹{selected_sale_data['gross_sales']:.2f}"
    )

    st.write(
        f"*Already Received:* ₹{selected_sale_data['received_amount']:.2f}"
    )

    st.write(
        f"*Pending:* ₹{selected_sale_data['pending_amount']:.2f}"
    )


    payment_amount = st.number_input(
        "Payment Amount",
        min_value=0.0,
        max_value=float(selected_sale_data["pending_amount"]),
        step=100.0
    )


    payment_method = st.selectbox(
        "Payment Method",
        ["Cash", "UPI", "Card", "Bank Transfer"]
    )


    if st.button("Record Payment"):

        if payment_amount <= 0:

            st.error("Payment amount must be greater than 0.")

        else:

            connection = get_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO payment_splits
                (sale_id, payment_date, amount_paid, payment_method)
                VALUES (%s, CURDATE(), %s, %s)
            """

            cursor.execute(
                query,
                (
                    sale_id,
                    payment_amount,
                    payment_method
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            st.success("Payment recorded successfully!")
            st.rerun()