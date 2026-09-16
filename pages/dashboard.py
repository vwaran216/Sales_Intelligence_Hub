import streamlit as st
import pandas as pd
from database import get_connection


st.title("📊 Sales Dashboard")


# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please login first from the main page.")
    st.stop()


user = st.session_state.get("user")

if user is None:
    st.warning("User session not found. Please logout and login again.")
    st.stop()


# Connect to MySQL
connection = get_connection()
cursor = connection.cursor(dictionary=True)


# Super Admin → all branches
if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            COALESCE(SUM(gross_sales), 0) AS total_gross,
            COALESCE(SUM(received_amount), 0) AS total_received,
            COALESCE(SUM(pending_amount), 0) AS total_pending,
            COUNT(*) AS total_sales
        FROM customer_sales
    """)

# Admin → assigned branch only
else:

    cursor.execute("""
        SELECT
            COALESCE(SUM(gross_sales), 0) AS total_gross,
            COALESCE(SUM(received_amount), 0) AS total_received,
            COALESCE(SUM(pending_amount), 0) AS total_pending,
            COUNT(*) AS total_sales
        FROM customer_sales
        WHERE branch_id = %s
    """, (user["branch_id"],))


kpi = cursor.fetchone()

cursor.close()
connection.close()


# Display KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Gross Sales",
        f"₹{kpi['total_gross']:,.2f}"
    )

with col2:
    st.metric(
        "💵 Total Received",
        f"₹{kpi['total_received']:,.2f}"
    )

with col3:
    st.metric(
        "⏳ Total Pending",
        f"₹{kpi['total_pending']:,.2f}"
    )

with col4:
    st.metric(
        "🧾 Total Sales",
        kpi["total_sales"]
    )

st.subheader("📈 Daily Sales Trend")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            sale_date,
            SUM(gross_sales) AS total_sales
        FROM customer_sales
        GROUP BY sale_date
        ORDER BY sale_date
    """)

else:

    cursor.execute("""
        SELECT
            sale_date,
            SUM(gross_sales) AS total_sales
        FROM customer_sales
        WHERE branch_id = %s
        GROUP BY sale_date
        ORDER BY sale_date
    """, (user["branch_id"],))

trend_data = cursor.fetchall()

cursor.close()
connection.close()

if trend_data:

    df = pd.DataFrame(trend_data)

    df["sale_date"] = pd.to_datetime(df["sale_date"])

    df = df.set_index("sale_date")

    st.line_chart(df["total_sales"])

else:

    st.info("No sales data available for the trend chart.")


st.subheader("🏢 Branch Performance")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

if user["role"] == "Super Admin":

    cursor.execute("""
        SELECT
            b.branch_name,
            COALESCE(SUM(cs.gross_sales), 0) AS total_sales
        FROM branches b
        LEFT JOIN customer_sales cs
            ON b.branch_id = cs.branch_id
        GROUP BY b.branch_id, b.branch_name
        ORDER BY total_sales DESC
    """)

    branch_data = cursor.fetchall()

else:

    cursor.execute("""
        SELECT
            b.branch_name,
            COALESCE(SUM(cs.gross_sales), 0) AS total_sales
        FROM branches b
        LEFT JOIN customer_sales cs
            ON b.branch_id = cs.branch_id
        WHERE b.branch_id = %s
        GROUP BY b.branch_id, b.branch_name
    """, (user["branch_id"],))

    branch_data = cursor.fetchall()

cursor.close()
connection.close()

if branch_data:

    branch_df = pd.DataFrame(branch_data)

    branch_df = branch_df.set_index("branch_name")

    st.bar_chart(branch_df["total_sales"])

else:

    st.info("No branch sales data available.")



st.subheader("⏳ Pending Payments")

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
            cs.pending_amount
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
            cs.pending_amount
        FROM customer_sales cs
        JOIN branches b
            ON cs.branch_id = b.branch_id
        WHERE cs.branch_id = %s
          AND cs.pending_amount > 0
        ORDER BY cs.pending_amount DESC
    """, (user["branch_id"],))

pending_data = cursor.fetchall()

cursor.close()
connection.close()

if pending_data:
    st.dataframe(pending_data, use_container_width=True)
else:
    st.success("🎉 No pending payments!")