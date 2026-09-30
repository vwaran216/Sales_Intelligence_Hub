import streamlit as st
import pandas as pd
from database import get_connection


st.title("📑 Sales Reports & Analytics")


# ---------------- LOGIN CHECK ----------------

if not st.session_state.get("logged_in", False):
    st.warning("Please login first from the main page.")
    st.stop()

user = st.session_state.get("user")

if user is None:
    st.warning("User session not found. Please logout and login again.")
    st.stop()


# ---------------- COMPLETE SALES REPORT ----------------

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            cs.sale_id,
            cs.sale_date,
            b.branch_name,
            cs.name,
            cs.mobile_number,
            cs.product_name,
            cs.gross_sales,
            cs.received_amount,
            cs.pending_amount,
            cs.status
        FROM customer_sales cs
        JOIN branches b
            ON cs.branch_id = b.branch_id
        ORDER BY cs.sale_id DESC
    """)

else:

    cursor.execute("""
        SELECT
            cs.sale_id,
            cs.sale_date,
            b.branch_name,
            cs.name,
            cs.mobile_number,
            cs.product_name,
            cs.gross_sales,
            cs.received_amount,
            cs.pending_amount,
            cs.status
        FROM customer_sales cs
        JOIN branches b
            ON cs.branch_id = b.branch_id
        WHERE cs.branch_id = %s
        ORDER BY cs.sale_id DESC
    """, (user["branch_id"],))

sales_data = cursor.fetchall()
st.dataframe(sales_data)

cursor.close()
connection.close()


if sales_data:

    df = pd.DataFrame(sales_data)

    st.subheader("📊 Complete Sales Report")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader("💰 Financial Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Gross",
            f"₹{df['gross_sales'].sum():,.2f}"
        )

    with col2:
        st.metric(
            "Total Received",
            f"₹{df['received_amount'].sum():,.2f}"
        )

    with col3:
        st.metric(
            "Total Pending",
            f"₹{df['pending_amount'].sum():,.2f}"
        )

else:

    st.info("No sales data available.")


# ---------------- PAYMENT METHOD REPORT ----------------

st.subheader("💳 Payment Method Collection")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            payment_method,
            SUM(amount_paid) AS total_collected
        FROM payment_splits
        GROUP BY payment_method
        ORDER BY total_collected DESC
    """)

else:

    cursor.execute("""
        SELECT
            ps.payment_method,
            SUM(ps.amount_paid) AS total_collected
        FROM payment_splits ps
        JOIN customer_sales cs
            ON ps.sale_id = cs.sale_id
        WHERE cs.branch_id = %s
        GROUP BY ps.payment_method
        ORDER BY total_collected DESC
    """, (user["branch_id"],))

payment_data = cursor.fetchall()

cursor.close()
connection.close()


if payment_data:

    payment_df = pd.DataFrame(payment_data)

    payment_df["total_collected"] = payment_df["total_collected"].astype(float)

    st.dataframe(
        payment_df,
        use_container_width=True
    )

    st.bar_chart(
        payment_df.set_index("payment_method")["total_collected"]
    )

else:

    st.info("No payment data available.")


# ---------------- TOP CUSTOMERS REPORT ----------------

st.subheader("🏆 Top 3 Customers")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            name,
            COUNT(*) AS number_of_sales,
            SUM(gross_sales) AS total_sales
        FROM customer_sales
        GROUP BY name
        ORDER BY total_sales DESC
        LIMIT 3
    """)

else:

    cursor.execute("""
        SELECT
            name,
            COUNT(*) AS number_of_sales,
            SUM(gross_sales) AS total_sales
        FROM customer_sales
        WHERE branch_id = %s
        GROUP BY name
        ORDER BY total_sales DESC
        LIMIT 3
    """, (user["branch_id"],))

top_customers = cursor.fetchall()

cursor.close()
connection.close()


if top_customers:

    top_df = pd.DataFrame(top_customers)

    top_df["total_sales"] = top_df["total_sales"].astype(float)

    st.dataframe(
        top_df,
        use_container_width=True
    )

else:

    st.info("No customer sales data available.")


# ---------------- MONTHLY SALES ANALYSIS ----------------

st.subheader("📅 Monthly Sales Analysis")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            DATE_FORMAT(sale_date, '%Y-%m') AS month,
            SUM(gross_sales) AS total_sales,
            SUM(received_amount) AS total_received,
            SUM(pending_amount) AS total_pending
        FROM customer_sales
        GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
        ORDER BY month
    """)

else:

    cursor.execute("""
        SELECT
            DATE_FORMAT(sale_date, '%Y-%m') AS month,
            SUM(gross_sales) AS total_sales,
            SUM(received_amount) AS total_received,
            SUM(pending_amount) AS total_pending
        FROM customer_sales
        WHERE branch_id = %s
        GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
        ORDER BY month
    """, (user["branch_id"],))

monthly_data = cursor.fetchall()

cursor.close()
connection.close()


if monthly_data:

    monthly_df = pd.DataFrame(monthly_data)

    monthly_df["total_sales"] = monthly_df["total_sales"].astype(float)
    monthly_df["total_received"] = monthly_df["total_received"].astype(float)
    monthly_df["total_pending"] = monthly_df["total_pending"].astype(float)

    st.dataframe(
        monthly_df,
        use_container_width=True
    )

    st.bar_chart(
        monthly_df.set_index("month")["total_sales"]
    )

else:

    st.info("No monthly sales data available.")


# ---------------- PENDING PAYMENT ANALYSIS ----------------

st.subheader("⏳ Pending Payment Analysis")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            cs.sale_id,
            b.branch_name,
            cs.name,
            cs.product_name,
            cs.gross_sales,
            cs.received_amount,
            cs.pending_amount,
            cs.status
        FROM customer_sales cs
        JOIN branches b
            ON cs.branch_id = b.branch_id
        WHERE cs.pending_amount > 0
        ORDER BY cs.pending_amount DESC
    """)

else:

    cursor.execute("""
        SELECT
            cs.sale_id,
            b.branch_name,
            cs.name,
            cs.product_name,
            cs.gross_sales,
            cs.received_amount,
            cs.pending_amount,
            cs.status
        FROM customer_sales cs
        JOIN branches b
            ON cs.branch_id = b.branch_id
        WHERE cs.branch_id = %s
          AND cs.pending_amount > 0
        ORDER BY cs.pending_amount DESC
    """, (user["branch_id"],))

pending_analysis = cursor.fetchall()

cursor.close()
connection.close()


if pending_analysis:

    pending_df = pd.DataFrame(pending_analysis)

    for column in ["gross_sales", "received_amount", "pending_amount"]:
        pending_df[column] = pending_df[column].astype(float)

    st.dataframe(
        pending_df,
        use_container_width=True
    )

else:

    st.success("🎉 No pending payments!")


# ---------------- PRODUCT PERFORMANCE ----------------

st.subheader("📦 Product Performance")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            product_name,
            COUNT(*) AS number_of_sales,
            SUM(gross_sales) AS total_sales,
            SUM(received_amount) AS total_received,
            SUM(pending_amount) AS total_pending
        FROM customer_sales
        GROUP BY product_name
        ORDER BY total_sales DESC
    """)

else:

    cursor.execute("""
        SELECT
            product_name,
            COUNT(*) AS number_of_sales,
            SUM(gross_sales) AS total_sales,
            SUM(received_amount) AS total_received,
            SUM(pending_amount) AS total_pending
        FROM customer_sales
        WHERE branch_id = %s
        GROUP BY product_name
        ORDER BY total_sales DESC
    """, (user["branch_id"],))

product_data = cursor.fetchall()

cursor.close()
connection.close()


if product_data:

    product_df = pd.DataFrame(product_data)

    for column in ["total_sales", "total_received", "total_pending"]:
        product_df[column] = product_df[column].astype(float)

    st.dataframe(
        product_df,
        use_container_width=True
    )

    st.bar_chart(
        product_df.set_index("product_name")["total_sales"]
    )

else:

    st.info("No product sales data available.")


# ---------------- BRANCH REVENUE COMPARISON ----------------

st.subheader("🏢 Branch Revenue Comparison")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            b.branch_name,
            COUNT(cs.sale_id) AS number_of_sales,
            COALESCE(SUM(cs.gross_sales), 0) AS total_sales,
            COALESCE(SUM(cs.received_amount), 0) AS total_received,
            COALESCE(SUM(cs.pending_amount), 0) AS total_pending
        FROM branches b
        LEFT JOIN customer_sales cs
            ON b.branch_id = cs.branch_id
        GROUP BY b.branch_id, b.branch_name
        ORDER BY total_sales DESC
    """)

else:

    cursor.execute("""
        SELECT
            b.branch_name,
            COUNT(cs.sale_id) AS number_of_sales,
            COALESCE(SUM(cs.gross_sales), 0) AS total_sales,
            COALESCE(SUM(cs.received_amount), 0) AS total_received,
            COALESCE(SUM(cs.pending_amount), 0) AS total_pending
        FROM branches b
        LEFT JOIN customer_sales cs
            ON b.branch_id = cs.branch_id
        WHERE b.branch_id = %s
        GROUP BY b.branch_id, b.branch_name
    """, (user["branch_id"],))

branch_revenue = cursor.fetchall()

cursor.close()
connection.close()


if branch_revenue:

    branch_df = pd.DataFrame(branch_revenue)

    for column in ["total_sales", "total_received", "total_pending"]:
        branch_df[column] = branch_df[column].astype(float)

    st.dataframe(
        branch_df,
        use_container_width=True
    )

    st.bar_chart(
        branch_df.set_index("branch_name")["total_sales"]
    )

else:

    st.info("No branch revenue data available.")


# ---------------- SALES STATUS SUMMARY ----------------

st.subheader("📌 Sales Status Summary")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS number_of_sales,
            SUM(gross_sales) AS total_sales
        FROM customer_sales
        GROUP BY status
        ORDER BY status
    """)

else:

    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS number_of_sales,
            SUM(gross_sales) AS total_sales
        FROM customer_sales
        WHERE branch_id = %s
        GROUP BY status
        ORDER BY status
    """, (user["branch_id"],))

# FIX: fetch status data for BOTH Super Admin and other users
status_data = cursor.fetchall()

cursor.close()
connection.close()


if status_data:

    status_df = pd.DataFrame(status_data)

    status_df["total_sales"] = status_df["total_sales"].astype(float)

    st.dataframe(
        status_df,
        use_container_width=True
    )

    st.bar_chart(
        status_df.set_index("status")["total_sales"]
    )

else:

    st.info("No sales status data available.")