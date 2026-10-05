import streamlit as st
from datetime import date
from database import get_connection


# ---------------------------------------------------------
# LOGIN CHECK
# ---------------------------------------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.stop()


# ---------------------------------------------------------
# SUPER ADMIN CHECK
# ---------------------------------------------------------
user = st.session_state.get("user")

if not user or user.get("role") != "Super Admin":
    st.error("Access denied. Only Super Admin can add customers and payments.")
    st.stop()


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Customer & Payment Management",
    page_icon="💰",
    layout="wide"
)

st.title("👤 Customer & Payment Management")
st.write("Add new customers and record payment splits.")


# =========================================================
# TABS
# =========================================================

customer_tab, payment_tab = st.tabs(
    ["🧾 Customer Entry", "💰 Payment Splits"]
)


# =========================================================
# CUSTOMER ENTRY TAB
# =========================================================

with customer_tab:

    st.header("🧾 Add New Customer")

    # -----------------------------------------------------
    # LOAD BRANCHES
    # -----------------------------------------------------
    branches = []

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT branch_id, branch_name
            FROM branches
            ORDER BY branch_name
        """)

        branches = cursor.fetchall()

    except Exception as e:
        st.error(f"Unable to load branches: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if branches:

        branch_options = {
            branch["branch_name"]: branch["branch_id"]
            for branch in branches
        }

        # -------------------------------------------------
        # CUSTOMER DETAILS
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:
            branch_name = st.selectbox(
                "Branch",
                list(branch_options.keys())
            )

            customer_name = st.text_input(
                "Customer Name"
            )

            mobile_number = st.text_input(
                "Mobile Number"
            )

            product_name = st.selectbox(
                "Product",
                ["DS", "DA", "BA", "FSD"]
            )

        with col2:

            sale_date = st.date_input(
                "Sale Date",
                value=date.today(),
                min_value=date(2020, 1, 1)
            )

            gross_sales = st.number_input(
                "Gross Sales",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

        st.divider()

        # -------------------------------------------------
        # ADD CUSTOMER
        # -------------------------------------------------

        if st.button(
            "➕ Add Customer",
            type="primary",
            use_container_width=True
        ):

            if not customer_name.strip():
                st.error("Please enter Customer Name.")

            elif not mobile_number.strip():
                st.error("Please enter Mobile Number.")

            elif gross_sales <= 0:
                st.error("Gross Sales must be greater than 0.")

            else:

                conn = None
                cursor = None

                try:

                    conn = get_connection()
                    cursor = conn.cursor()

                    branch_id = branch_options[branch_name]

                    cursor.execute("""
                        INSERT INTO customer_sales
                        (
                            branch_id,
                            sale_date,
                            name,
                            mobile_number,
                            product_name,
                            gross_sales,
                            received_amount,
                            pending_amount,
                            status
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                    """, (
                        branch_id,
                        sale_date,
                        customer_name.strip(),
                        mobile_number.strip(),
                        product_name,
                        gross_sales,
                        0,
                        gross_sales,
                        "Open"
                    ))

                    conn.commit()

                    sale_id = cursor.lastrowid

                    st.success(
                        f"Customer added successfully! Customer ID / Sale ID: {sale_id}"
                    )

                    st.info(
                        f"Now go to the **💰 Payment Splits** tab and enter "
                        f"Customer ID **{sale_id}** to record the initial payment."
                    )

                except Exception as e:

                    if conn:
                        conn.rollback()

                    st.error(f"Error adding customer: {e}")

                finally:

                    if cursor:
                        cursor.close()

                    if conn:
                        conn.close()

    else:

        st.warning(
            "No branches found. Please make sure the branches table contains data."
        )


# =========================================================
# PAYMENT SPLITS TAB
# =========================================================

with payment_tab:

    st.header("💰 Payment Splits")

    st.write(
        "Use this section to record the initial payment or any subsequent payment."
    )

    # -----------------------------------------------------
    # CUSTOMER / SALE ID
    # -----------------------------------------------------

    customer_id_input = st.text_input(
        "Customer ID / Sale ID",
        placeholder="Enter Customer ID",
        help="Enter the Sale ID generated when the customer was added."
    )

    customer = None
    customer_id = None

    # -----------------------------------------------------
    # FIND CUSTOMER
    # -----------------------------------------------------

    if customer_id_input.strip():

        try:

            customer_id = int(customer_id_input.strip())

            conn = None
            cursor = None

            try:

                conn = get_connection()
                cursor = conn.cursor(dictionary=True)

                cursor.execute("""
                    SELECT
                        cs.sale_id,
                        cs.branch_id,
                        cs.sale_date,
                        cs.name,
                        cs.mobile_number,
                        cs.product_name,
                        cs.gross_sales,
                        cs.received_amount,
                        cs.pending_amount,
                        cs.status,
                        b.branch_name
                    FROM customer_sales cs
                    LEFT JOIN branches b
                        ON cs.branch_id = b.branch_id
                    WHERE cs.sale_id = %s
                """, (customer_id,))

                customer = cursor.fetchone()

            finally:

                if cursor:
                    cursor.close()

                if conn:
                    conn.close()

            if customer:

                # -----------------------------------------
                # CUSTOMER DETAILS
                # -----------------------------------------

                st.success(
                    f"Customer found — {customer['name']}"
                )

                st.subheader("👤 Customer Details")

                detail_col1, detail_col2, detail_col3 = st.columns(3)

                with detail_col1:
                    st.write("**Customer ID**")
                    st.write(customer["sale_id"])

                    st.write("**Customer Name**")
                    st.write(customer["name"])

                    st.write("**Mobile Number**")
                    st.write(customer["mobile_number"])

                with detail_col2:
                    st.write("**Branch**")
                    st.write(customer["branch_name"])

                    st.write("**Product**")
                    st.write(customer["product_name"])

                    st.write("**Sale Date**")
                    st.write(customer["sale_date"])

                with detail_col3:
                    st.write("**Status**")
                    st.write(customer["status"])

                # -----------------------------------------
                # PAYMENT SUMMARY
                # -----------------------------------------

                st.subheader("💵 Payment Summary")

                gross_sales_value = float(
                    customer["gross_sales"] or 0
                )

                received_value = float(
                    customer["received_amount"] or 0
                )

                pending_value = float(
                    customer["pending_amount"] or 0
                )

                summary_col1, summary_col2, summary_col3 = st.columns(3)

                with summary_col1:
                    st.metric(
                        "Gross Sales",
                        f"₹{gross_sales_value:,.2f}"
                    )

                with summary_col2:
                    st.metric(
                        "Received Amount",
                        f"₹{received_value:,.2f}"
                    )

                with summary_col3:
                    st.metric(
                        "Pending Amount",
                        f"₹{pending_value:,.2f}"
                    )

            else:

                st.warning(
                    "Customer ID / Sale ID not found."
                )

        except ValueError:

            st.error(
                "Customer ID must be a valid number."
            )

        except Exception as e:

            st.error(
                f"Error while finding customer: {e}"
            )

    else:

        st.info(
            "Enter a Customer ID / Sale ID above to view the customer's payment details."
        )


    # =====================================================
    # PAYMENT FORM
    # =====================================================

    st.divider()

    st.subheader("💳 Add Payment")

    # -----------------------------------------------------
    # PAYMENT FIELDS ARE ALWAYS VISIBLE
    # -----------------------------------------------------

    payment_col1, payment_col2 = st.columns(2)

    with payment_col1:

        payment_date = st.date_input(
            "Payment Date",
            value=date.today(),
            min_value=date(2020, 1, 1),
            key="payment_date"
        )

        payment_method = st.selectbox(
            "Payment Method",
            [
                "Cash",
                "UPI",
                "Card",
                "Bank Transfer"
            ],
            key="payment_method"
        )

    with payment_col2:

        payment_amount = st.number_input(
            "Payment Amount",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="payment_amount"
        )

        # -------------------------------------------------
        # PENDING AMOUNT INFORMATION
        # -------------------------------------------------

        if customer:

            pending_value = float(
                customer["pending_amount"] or 0
            )

            if pending_value > 0:

                st.caption(
                    f"Current Pending Amount: ₹{pending_value:,.2f}"
                )

                if payment_amount > 0:

                    new_received = (
                        float(customer["received_amount"] or 0)
                        + payment_amount
                    )

                    new_pending = (
                        pending_value
                        - payment_amount
                    )

                    st.write(
                        f"New Received Amount: **₹{new_received:,.2f}**"
                    )

                    if new_pending >= 0:

                        st.write(
                            f"New Pending Amount: **₹{new_pending:,.2f}**"
                        )

                    else:

                        st.error(
                            "Payment amount exceeds the pending amount."
                        )

            else:

                st.success(
                    "This customer has no pending amount. Payment is already fully settled."
                )

    # -----------------------------------------------------
    # ADD PAYMENT BUTTON
    # -----------------------------------------------------

    add_payment = st.button(
        "💰 Add Payment",
        type="primary",
        use_container_width=True
    )

    if add_payment:

        # ---------------------------------------------
        # VALIDATE CUSTOMER ID
        # ---------------------------------------------

        if not customer_id_input.strip():

            st.error(
                "Please enter Customer ID / Sale ID."
            )

        elif customer is None:

            st.error(
                "Please enter a valid Customer ID / Sale ID."
            )

        elif payment_amount <= 0:

            st.error(
                "Payment Amount must be greater than 0."
            )

        else:

            pending_value = float(
                customer["pending_amount"] or 0
            )

            # -----------------------------------------
            # PAYMENT CANNOT EXCEED PENDING
            # -----------------------------------------

            if payment_amount > pending_value:

                st.error(
                    f"Payment amount cannot exceed the pending amount "
                    f"of ₹{pending_value:,.2f}."
                )

            elif pending_value <= 0:

                st.error(
                    "This customer has no pending amount."
                )

            else:

                conn = None
                cursor = None

                try:

                    conn = get_connection()
                    cursor = conn.cursor()

                    # ---------------------------------
                    # INSERT PAYMENT SPLIT
                    # ---------------------------------

                    cursor.execute("""
                        INSERT INTO payment_splits
                        (
                            sale_id,
                            payment_date,
                            amount_paid,
                            payment_method
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s
                        )
                    """, (
                        customer_id,
                        payment_date,
                        payment_amount,
                        payment_method
                    ))

                    conn.commit()

                    st.success(
                        f"Payment of ₹{payment_amount:,.2f} added successfully!"
                    )

                    st.info(
                        "Received Amount and Pending Amount have been updated automatically."
                    )

                    st.rerun()

                except Exception as e:

                    if conn:
                        conn.rollback()

                    st.error(
                        f"Error adding payment: {e}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if conn:
                        conn.close()