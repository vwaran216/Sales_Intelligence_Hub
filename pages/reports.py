import streamlit as st
import pandas as pd
from datetime import date
from database import get_connection


# =========================================================
# PAGE
# =========================================================

st.title("📑 Sales Reports & Analytics")


# =========================================================
# LOGIN CHECK
# =========================================================

if not st.session_state.get("logged_in", False):
    st.warning("Please login first from the main page.")
    st.stop()

user = st.session_state.get("user")

if user is None:
    st.warning("User session not found. Please logout and login again.")
    st.stop()


is_super_admin = user["role"] == "Super Admin"


# =========================================================
# BRANCH ADMIN FILTERS
# =========================================================

if not is_super_admin:

    st.subheader("🔍 Filter Sales Data")

    # -----------------------------------------------------
    # LOAD FILTER OPTIONS
    # -----------------------------------------------------

    connection = None
    cursor = None

    products = []
    customers = []

    try:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Product list
        cursor.execute("""
            SELECT DISTINCT product_name
            FROM customer_sales
            WHERE branch_id = %s
              AND product_name IS NOT NULL
              AND product_name <> ''
            ORDER BY product_name
        """, (user["branch_id"],))

        product_rows = cursor.fetchall()

        products = [
            row["product_name"]
            for row in product_rows
        ]

        # Customer list
        cursor.execute("""
            SELECT DISTINCT name
            FROM customer_sales
            WHERE branch_id = %s
              AND name IS NOT NULL
              AND name <> ''
            ORDER BY name
        """, (user["branch_id"],))

        customer_rows = cursor.fetchall()

        customers = [
            row["name"]
            for row in customer_rows
        ]

    except Exception as e:

        st.error(f"Error loading filter options: {e}")

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    # -----------------------------------------------------
    # FILTER UI
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        product_filter = st.selectbox(
            "🏷️ Product Name",
            ["All"] + products,
            key="product_filter"
        )

    with col2:

        customer_filter = st.selectbox(
            "👤 Customer Name",
            ["All"] + customers,
            key="customer_filter"
        )

    with col3:

        status_filter = st.selectbox(
            "📌 Status",
            ["All", "Open", "Close"],
            key="status_filter"
        )


    col4, col5 = st.columns(2)

    with col4:

        start_date = st.date_input(
            "📅 Start Date",
            value=date(2020, 1, 1),
            min_value=date(2020, 1, 1),
            max_value=date.today(),
            key="start_date"
        )

    with col5:

        end_date = st.date_input(
            "📅 End Date",
            value=date.today(),
            min_value=date(2020, 1, 1),
            max_value=date.today(),
            key="end_date"
        )


    # -----------------------------------------------------
    # BUTTONS
    # -----------------------------------------------------

    col6, col7 = st.columns(2)

    with col6:

        apply_filters = st.button(
            "🔍 Apply Filters",
            type="primary",
            use_container_width=True
        )

    with col7:

        reset_filters = st.button(
            "🔄 Reset Filters",
            use_container_width=True
        )


    # -----------------------------------------------------
    # RESET
    # -----------------------------------------------------

    if reset_filters:

        st.session_state["product_filter"] = "All"
        st.session_state["customer_filter"] = "All"
        st.session_state["status_filter"] = "All"
        st.session_state["start_date"] = date(2020, 1, 1)
        st.session_state["end_date"] = date.today()

        st.rerun()


else:

    # Super Admin does not need these Branch Admin filters
    product_filter = "All"
    customer_filter = "All"
    status_filter = "All"
    start_date = date(2020, 1, 1)
    end_date = date.today()


# =========================================================
# BUILD FILTER CONDITIONS
# =========================================================

conditions = []
parameters = []


# ---------------------------------------------------------
# BRANCH SECURITY
# ---------------------------------------------------------

if not is_super_admin:

    conditions.append("cs.branch_id = %s")
    parameters.append(user["branch_id"])


# ---------------------------------------------------------
# DATE FILTER
# ---------------------------------------------------------

conditions.append("DATE(cs.sale_date) >= %s")
parameters.append(start_date)

conditions.append("DATE(cs.sale_date) <= %s")
parameters.append(end_date)


# ---------------------------------------------------------
# PRODUCT FILTER
# ---------------------------------------------------------

if not is_super_admin:

    if product_filter != "All":

        conditions.append("cs.product_name = %s")
        parameters.append(product_filter)


# ---------------------------------------------------------
# CUSTOMER FILTER
# ---------------------------------------------------------

if not is_super_admin:

    if customer_filter != "All":

        conditions.append("cs.name = %s")
        parameters.append(customer_filter)


# ---------------------------------------------------------
# STATUS FILTER
# ---------------------------------------------------------

if not is_super_admin:

    if status_filter != "All":

        conditions.append("cs.status = %s")
        parameters.append(status_filter)


where_clause = ""

if conditions:
    where_clause = "WHERE " + " AND ".join(conditions)


# =========================================================
# COMPLETE SALES REPORT
# =========================================================

st.subheader("📊 Complete Sales Report")

connection = None
cursor = None

sales_data = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = f"""
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
        {where_clause}
        ORDER BY cs.sale_id DESC
    """

    cursor.execute(query, tuple(parameters))

    sales_data = cursor.fetchall()

except Exception as e:

    st.error(f"Error loading sales report: {e}")

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


# =========================================================
# DISPLAY SALES DATA
# =========================================================

if sales_data:

    df = pd.DataFrame(sales_data)

    # Convert numeric columns
    for column in [
        "gross_sales",
        "received_amount",
        "pending_amount"
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


   # -----------------------------------------------------
# FINANCIAL SUMMARY
# -----------------------------------------------------

st.subheader("💰 Financial Summary")

col1, col2, col3, col4 = st.columns(4)

total_gross = df["gross_sales"].sum()
total_received = df["received_amount"].sum()
total_pending = df["pending_amount"].sum()

if total_gross > 0:
    pending_collection_percentage = (
        total_pending / total_gross
    ) * 100
else:
    pending_collection_percentage = 0


with col1:

    st.metric(
        "Total Gross",
        f"₹{total_gross:,.2f}"
    )


with col2:

    st.metric(
        "Total Received",
        f"₹{total_received:,.2f}"
    )


with col3:

    st.metric(
        "Total Pending",
        f"₹{total_pending:,.2f}"
    )


with col4:

    st.metric(
        "Pending Collection %",
        f"{pending_collection_percentage:.2f}%"
    )

# =========================================================
# PAYMENT METHOD REPORT
# =========================================================

st.subheader("💳 Payment Method Collection")

connection = None
cursor = None

payment_data = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    payment_conditions = []
    payment_parameters = []

    # Branch restriction
    if not is_super_admin:

        payment_conditions.append(
            "cs.branch_id = %s"
        )

        payment_parameters.append(
            user["branch_id"]
        )


    # Date restriction
    payment_conditions.append(
        "DATE(cs.sale_date) >= %s"
    )

    payment_parameters.append(
        start_date
    )

    payment_conditions.append(
        "DATE(cs.sale_date) <= %s"
    )

    payment_parameters.append(
        end_date
    )


    # Product
    if not is_super_admin and product_filter != "All":

        payment_conditions.append(
            "cs.product_name = %s"
        )

        payment_parameters.append(
            product_filter
        )


    # Customer
    if not is_super_admin and customer_filter != "All":

        payment_conditions.append(
            "cs.name = %s"
        )

        payment_parameters.append(
            customer_filter
        )


    # Status
    if not is_super_admin and status_filter != "All":

        payment_conditions.append(
            "cs.status = %s"
        )

        payment_parameters.append(
            status_filter
        )


    payment_where = ""

    if payment_conditions:

        payment_where = (
            "WHERE " +
            " AND ".join(payment_conditions)
        )


    query = f"""
        SELECT
            ps.payment_method,
            SUM(ps.amount_paid) AS total_collected
        FROM payment_splits ps
        JOIN customer_sales cs
            ON ps.sale_id = cs.sale_id
        {payment_where}
        GROUP BY ps.payment_method
        ORDER BY total_collected DESC
    """

    cursor.execute(
        query,
        tuple(payment_parameters)
    )

    payment_data = cursor.fetchall()

except Exception as e:

    st.error(
        f"Error loading payment report: {e}"
    )

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


if payment_data:

    payment_df = pd.DataFrame(
        payment_data
    )

    payment_df["total_collected"] = (
        payment_df["total_collected"]
        .astype(float)
    )

    st.dataframe(
        payment_df,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        payment_df.set_index(
            "payment_method"
        )["total_collected"]
    )

else:

    st.info(
        "No payment data available."
    )


# =========================================================
# TOP CUSTOMERS REPORT
# =========================================================

st.subheader("🏆 Top 3 Customers")

connection = None
cursor = None

top_customers = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = f"""
        SELECT
            cs.name,
            COUNT(*) AS number_of_sales,
            SUM(cs.gross_sales) AS total_sales
        FROM customer_sales cs
        {where_clause}
        GROUP BY cs.name
        ORDER BY total_sales DESC
        LIMIT 3
    """

    cursor.execute(
        query,
        tuple(parameters)
    )

    top_customers = cursor.fetchall()

except Exception as e:

    st.error(
        f"Error loading top customers: {e}"
    )

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


if top_customers:

    top_df = pd.DataFrame(
        top_customers
    )

    top_df["total_sales"] = (
        top_df["total_sales"]
        .astype(float)
    )

    st.dataframe(
        top_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No customer sales data available."
    )


# =========================================================
# MONTHLY SALES ANALYSIS
# =========================================================

st.subheader("📅 Monthly Sales Analysis")

connection = None
cursor = None

monthly_data = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = f"""
        SELECT
            DATE_FORMAT(cs.sale_date, '%Y-%m') AS month,
            SUM(cs.gross_sales) AS total_sales,
            SUM(cs.received_amount) AS total_received,
            SUM(cs.pending_amount) AS total_pending
        FROM customer_sales cs
        {where_clause}
        GROUP BY DATE_FORMAT(cs.sale_date, '%Y-%m')
        ORDER BY month
    """

    cursor.execute(
        query,
        tuple(parameters)
    )

    monthly_data = cursor.fetchall()

except Exception as e:

    st.error(
        f"Error loading monthly analysis: {e}"
    )

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


if monthly_data:

    monthly_df = pd.DataFrame(
        monthly_data
    )

    for column in [
        "total_sales",
        "total_received",
        "total_pending"
    ]:

        monthly_df[column] = (
            monthly_df[column]
            .astype(float)
        )

    st.dataframe(
        monthly_df,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        monthly_df.set_index(
            "month"
        )["total_sales"]
    )

else:

    st.info(
        "No monthly sales data available."
    )


# =========================================================
# PENDING PAYMENT ANALYSIS
# =========================================================

st.subheader("⏳ Pending Payment Analysis")

connection = None
cursor = None

pending_analysis = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    pending_conditions = list(conditions)
    pending_parameters = list(parameters)

    pending_conditions.append(
        "cs.pending_amount > 0"
    )

    pending_where = (
        "WHERE " +
        " AND ".join(pending_conditions)
    )

    query = f"""
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
        {pending_where}
        ORDER BY cs.pending_amount DESC
    """

    cursor.execute(
        query,
        tuple(pending_parameters)
    )

    pending_analysis = cursor.fetchall()

except Exception as e:

    st.error(
        f"Error loading pending analysis: {e}"
    )

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


if pending_analysis:

    pending_df = pd.DataFrame(
        pending_analysis
    )

    for column in [
        "gross_sales",
        "received_amount",
        "pending_amount"
    ]:

        pending_df[column] = (
            pending_df[column]
            .astype(float)
        )

    st.dataframe(
        pending_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "🎉 No pending payments!"
    )


# =========================================================
# PRODUCT PERFORMANCE
# =========================================================

st.subheader("📦 Product Performance")

connection = None
cursor = None

product_data = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = f"""
        SELECT
            cs.product_name,
            COUNT(*) AS number_of_sales,
            SUM(cs.gross_sales) AS total_sales,
            SUM(cs.received_amount) AS total_received,
            SUM(cs.pending_amount) AS total_pending
        FROM customer_sales cs
        {where_clause}
        GROUP BY cs.product_name
        ORDER BY total_sales DESC
    """

    cursor.execute(
        query,
        tuple(parameters)
    )

    product_data = cursor.fetchall()

except Exception as e:

    st.error(
        f"Error loading product performance: {e}"
    )

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


if product_data:

    product_df = pd.DataFrame(
        product_data
    )

    for column in [
        "total_sales",
        "total_received",
        "total_pending"
    ]:

        product_df[column] = (
            product_df[column]
            .astype(float)
        )

    st.dataframe(
        product_df,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        product_df.set_index(
            "product_name"
        )["total_sales"]
    )

else:

    st.info(
        "No product sales data available."
    )


# =========================================================
# BRANCH REVENUE COMPARISON
# =========================================================

st.subheader("🏢 Branch Revenue Comparison")

connection = None
cursor = None

branch_revenue = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if is_super_admin:

        cursor.execute("""
            SELECT
                b.branch_name,
                COUNT(cs.sale_id) AS number_of_sales,
                COALESCE(
                    SUM(cs.gross_sales), 0
                ) AS total_sales,
                COALESCE(
                    SUM(cs.received_amount), 0
                ) AS total_received,
                COALESCE(
                    SUM(cs.pending_amount), 0
                ) AS total_pending
            FROM branches b
            LEFT JOIN customer_sales cs
                ON b.branch_id = cs.branch_id
            GROUP BY
                b.branch_id,
                b.branch_name
            ORDER BY total_sales DESC
        """)

    else:

        branch_conditions = [
            "b.branch_id = %s",
            "cs.sale_date >= %s",
            "cs.sale_date <= %s"
        ]

        branch_parameters = [
            user["branch_id"],
            start_date,
            end_date
        ]

        if product_filter != "All":

            branch_conditions.append(
                "cs.product_name = %s"
            )

            branch_parameters.append(
                product_filter
            )

        if customer_filter != "All":

            branch_conditions.append(
                "cs.name = %s"
            )

            branch_parameters.append(
                customer_filter
            )

        if status_filter != "All":

            branch_conditions.append(
                "cs.status = %s"
            )

            branch_parameters.append(
                status_filter
            )

        branch_where = (
            " AND ".join(branch_conditions)
        )

        query = f"""
            SELECT
                b.branch_name,
                COUNT(cs.sale_id) AS number_of_sales,
                COALESCE(
                    SUM(cs.gross_sales), 0
                ) AS total_sales,
                COALESCE(
                    SUM(cs.received_amount), 0
                ) AS total_received,
                COALESCE(
                    SUM(cs.pending_amount), 0
                ) AS total_pending
            FROM branches b
            LEFT JOIN customer_sales cs
                ON b.branch_id = cs.branch_id
            WHERE {branch_where}
            GROUP BY
                b.branch_id,
                b.branch_name
        """

        cursor.execute(
            query,
            tuple(branch_parameters)
        )

    branch_revenue = cursor.fetchall()

except Exception as e:

    st.error(
        f"Error loading branch revenue: {e}"
    )

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


if branch_revenue:

    branch_df = pd.DataFrame(
        branch_revenue
    )

    for column in [
        "total_sales",
        "total_received",
        "total_pending"
    ]:

        branch_df[column] = (
            branch_df[column]
            .astype(float)
        )

    st.dataframe(
        branch_df,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        branch_df.set_index(
            "branch_name"
        )["total_sales"]
    )

else:

    st.info(
        "No branch revenue data available."
    )


# =========================================================
# SALES STATUS SUMMARY
# =========================================================

st.subheader("📌 Sales Status Summary")

connection = None
cursor = None

status_data = []

try:

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = f"""
        SELECT
            cs.status,
            COUNT(*) AS number_of_sales,
            SUM(cs.gross_sales) AS total_sales
        FROM customer_sales cs
        {where_clause}
        GROUP BY cs.status
        ORDER BY cs.status
    """

    cursor.execute(
        query,
        tuple(parameters)
    )

    status_data = cursor.fetchall()

except Exception as e:

    st.error(
        f"Error loading status summary: {e}"
    )

finally:

    if cursor:
        cursor.close()

    if connection:
        connection.close()


if status_data:

    status_df = pd.DataFrame(
        status_data
    )

    status_df["total_sales"] = (
        status_df["total_sales"]
        .astype(float)
    )

    st.dataframe(
        status_df,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        status_df.set_index(
            "status"
        )["total_sales"]
    )

else:

    st.info(
        "No sales status data available."
    )