import streamlit as st
from auth import authenticate_user
from database import get_connection
from datetime import date


st.set_page_config(
    page_title="Sales Intelligence Hub",
    page_icon="📊",
    layout="wide"
)
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 24px;
}
[data-testid="stMetricLabel"] {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION INITIALIZATION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# =========================================================
# LOGIN PAGE
# =========================================================

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


# =========================================================
# DASHBOARD
# =========================================================

else:

    user = st.session_state.user

    st.title("📊 Sales Intelligence Hub")

    st.write(f"Welcome, **{user['username']}**")
    st.write(f"Role: **{user['role']}**")

    # =====================================================
    # SUPER ADMIN DASHBOARD
    # =====================================================

    if user["role"] == "Super Admin":

        st.info("You have access to all branches.")

        st.subheader("🔎 Customer Sales Filters")

        connection = get_connection()

        if connection is None:
            st.error("MySQL Connection not available.")
        else:

            cursor = connection.cursor(dictionary=True)

            # -------------------------------------------------
            # GET BRANCHES
            # -------------------------------------------------

            cursor.execute("""
                SELECT DISTINCT branch_name
                FROM branches
                WHERE branch_name IS NOT NULL
                ORDER BY branch_name
            """)

            branch_rows = cursor.fetchall()

            branch_options = ["All Branches"] + [
                row["branch_name"] for row in branch_rows
            ]

            # -------------------------------------------------
            # GET PRODUCTS
            # -------------------------------------------------

            cursor.execute("""
                SELECT DISTINCT product_name
                FROM customer_sales
                WHERE product_name IS NOT NULL
                  AND product_name <> ''
                ORDER BY product_name
            """)

            product_rows = cursor.fetchall()

            product_options = ["All Products"] + [
                row["product_name"] for row in product_rows
            ]

            # -------------------------------------------------
            # FILTER UI
            # -------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:
                selected_branch = st.selectbox(
                    "Branch Name",
                    branch_options
                )

            with col2:
                selected_product = st.selectbox(
                    "Product Name",
                    product_options
                )

            col3, col4 = st.columns(2)

            with col3:
                start_date = st.date_input(
                    "Start Date",
                    value=date(2020, 1, 1),
                    min_value=date(2020, 1, 1),
                )

            with col4:
                end_date = st.date_input(
                    "End Date",
                    value=date.today()
                )

            st.write("")

            apply_filter = st.button(
                "🔍 Apply Filters",
                type="primary"
            )

            # -------------------------------------------------
            # FILTER VALIDATION
            # -------------------------------------------------

            if start_date > end_date:

                st.error("Start Date cannot be after End Date.")

            else:

                # -------------------------------------------------
                # BUILD QUERY
                # -------------------------------------------------

                query = """
                    SELECT
                        cs.sale_id,
                        cs.branch_id,
                        b.branch_name,
                        cs.sale_date,
                        cs.name,
                        cs.product_name,
                        cs.gross_sales,
                        cs.received_amount,
                        cs.pending_amount,
                        cs.status
                    FROM customer_sales cs
                    LEFT JOIN branches b
                        ON cs.branch_id = b.branch_id
                    WHERE 1 = 1
                """

                params = []

                # Branch filter
                if selected_branch != "All Branches":

                    query += """
                        AND b.branch_name = %s
                    """

                    params.append(selected_branch)

                # Product filter
                if selected_product != "All Products":

                    query += """
                        AND cs.product_name = %s
                    """

                    params.append(selected_product)

                # Date filter
                query += """
                    AND DATE(cs.sale_date) >= %s
                    AND DATE(cs.sale_date) <= %s
                """

                params.append(start_date)
                params.append(end_date)

                query += """
                    ORDER BY cs.sale_date DESC, cs.sale_id DESC
                """

                # -------------------------------------------------
                # EXECUTE FILTERED QUERY
                # -------------------------------------------------

                cursor.execute(query, tuple(params))

                sales_data = cursor.fetchall()

                # -------------------------------------------------
                # CLOSE CONNECTION
                # -------------------------------------------------

                cursor.close()
                connection.close()

                # -------------------------------------------------
                # RESULTS
                # -------------------------------------------------

                st.subheader("📋 Customer Sales Report")

                if sales_data:

                    # Convert to dataframe
                    import pandas as pd

                    df = pd.DataFrame(sales_data)

                    # -------------------------------------------------
                    # SUMMARY METRICS
                    # -------------------------------------------------

                    total_sales = len(df)

                    gross_sales = df["gross_sales"].sum()

                    received_amount = df["received_amount"].sum()

                    pending_amount = df["pending_amount"].sum()
                    if gross_sales > 0:
                        pending_collection_percentage = (pending_amount / gross_sales) * 100
                    else:
                        pending_collection_percentage = 0

                    col1, col2, col3, col4, col5 = st.columns(5)

                    with col1:
                        st.metric(
                            "Total Sales",
                            total_sales
                        )

                    with col2:
                        st.metric(
                            "Gross Sales",
                            f"₹{gross_sales:,.2f}"
                        )

                    with col3:
                        st.metric(
                            "Received",
                            f"₹{received_amount:,.2f}"
                        )

                    with col4:
                        st.metric(
                            "Pending",
                            f"₹{pending_amount:,.2f}"
                        )

                    with col5:
                        st.metric(
                            "Pending Collection %",
                            f"{pending_collection_percentage:.2f}%"
                        )

                    st.write("")

                    # -------------------------------------------------
                    # DISPLAY SALES
                    # -------------------------------------------------

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.warning(
                        "No customer sales found for the selected filters."
                    )


    # =====================================================
    # =====================================================

    elif user["role"] == "Admin":

        connection = get_connection()

        if connection is None:

            st.error("MySQL Connection not available.")

        else:

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT branch_name
                FROM branches
                WHERE branch_id = %s
                """,
                (user["branch_id"],)
            )

            branch = cursor.fetchone()

            cursor.close()
            connection.close()

            if branch:

                st.info(
                    f"You are assigned to: **{branch['branch_name']}**"
                )

            else:

                st.warning(
                    "Branch information not found."
                )


    # =====================================================
    # LOGOUT
    # =====================================================

    st.write("")

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user = None

        st.rerun()