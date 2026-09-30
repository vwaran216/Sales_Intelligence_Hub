import streamlit as st
from database import get_connection


st.title("📚 SQL Query FAQ")
st.write("Frequently used SQL queries for Sales Intelligence Hub.")


queries = {

    "🔹 Basic Queries": {

        "1. Retrieve all records from customer_sales":
            "SELECT * FROM customer_sales;",

        "2. Retrieve all records from branches":
            "SELECT * FROM branches;",

        "3. Retrieve all records from payment_splits":
            "SELECT * FROM payment_splits;",

        "4. Display all sales with status = 'Open'":
            "SELECT * FROM customer_sales WHERE status = 'Open';",

        "5. Retrieve all sales belonging to the Chennai branch":
            """
            SELECT cs.*
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            WHERE b.branch_name = 'Chennai';
            """
    },

    "🔹 Aggregation Queries": {

        "1. Calculate total gross sales across all branches":
            """
            SELECT SUM(gross_sales) AS total_gross_sales
            FROM customer_sales;
            """,

        "2. Calculate total received amount":
            """
            SELECT SUM(received_amount) AS total_received_amount
            FROM customer_sales;
            """,

        "3. Calculate total pending amount":
            """
            SELECT SUM(pending_amount) AS total_pending_amount
            FROM customer_sales;
            """,

        "4. Count total number of sales per branch":
            """
            SELECT b.branch_name,
                   COUNT(cs.sale_id) AS total_sales
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            GROUP BY b.branch_id, b.branch_name;
            """,

        "5. Find average gross sales amount":
            """
            SELECT AVG(gross_sales) AS average_gross_sales
            FROM customer_sales;
            """
    },

    "🔹 Join-Based Queries": {

        "1. Retrieve sales details along with branch name":
            """
            SELECT cs.*, b.branch_name
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id;
            """,

        "2. Retrieve sales details along with total payment received":
            """
            SELECT
                cs.sale_id,
                cs.name,
                cs.gross_sales,
                COALESCE(SUM(ps.amount_paid), 0) AS total_payment_received
            FROM customer_sales cs
            LEFT JOIN payment_splits ps
                ON cs.sale_id = ps.sale_id
            GROUP BY
                cs.sale_id,
                cs.name,
                cs.gross_sales;
            """,

        "3. Show branch-wise total gross sales":
            """
            SELECT
                b.branch_name,
                SUM(cs.gross_sales) AS total_gross_sales
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            GROUP BY b.branch_id, b.branch_name;
            """,

        "4. Display sales along with payment method used":
            """
            SELECT
                cs.sale_id,
                cs.name,
                cs.product_name,
                ps.amount_paid,
                ps.payment_method
            FROM customer_sales cs
            JOIN payment_splits ps
                ON cs.sale_id = ps.sale_id;
            """,

        "5. Retrieve sales along with branch admin name":
            """
            SELECT
                cs.sale_id,
                cs.name,
                cs.product_name,
                cs.gross_sales,
                b.branch_name,
                u.username AS branch_admin
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            LEFT JOIN users u
                ON b.branch_id = u.branch_id
            WHERE u.role = 'Admin';
            """
    },

    "🔹 Financial Tracking Queries": {

        "1. Find sales where pending amount is greater than 5000":
            """
            SELECT *
            FROM customer_sales
            WHERE pending_amount > 5000;
            """,

        "2. Retrieve top 3 highest gross sales":
            """
            SELECT *
            FROM customer_sales
            ORDER BY gross_sales DESC
            LIMIT 3;
            """,

        "3. Find the branch with highest total gross sales":
            """
            SELECT
                b.branch_name,
                SUM(cs.gross_sales) AS total_gross_sales
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
            GROUP BY b.branch_id, b.branch_name
            ORDER BY total_gross_sales DESC
            LIMIT 1;
            """,

        "4. Retrieve monthly sales summary":
            """
            SELECT
                YEAR(sale_date) AS year,
                MONTH(sale_date) AS month,
                COUNT(sale_id) AS total_sales,
                SUM(gross_sales) AS total_gross_sales,
                SUM(received_amount) AS total_received,
                SUM(pending_amount) AS total_pending
            FROM customer_sales
            GROUP BY YEAR(sale_date), MONTH(sale_date)
            ORDER BY year, month;
            """,

        "5. Calculate payment method-wise total collection":
            """
            SELECT
                payment_method,
                SUM(amount_paid) AS total_collection
            FROM payment_splits
            GROUP BY payment_method
            ORDER BY total_collection DESC;
            """
    }
}


# Category selection
category = st.selectbox(
    "Select Query Category",
    list(queries.keys())
)


# Question selection
question = st.selectbox(
    "Select Question",
    list(queries[category].keys())
)


sql_query = queries[category][question]


# Run query
if st.button("▶️ Get Results"):

    connection = get_connection()

    if connection:

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(sql_query)

            results = cursor.fetchall()

            cursor.close()
            connection.close()

            st.success(f"Query executed successfully — {len(results)} records found.")

            if results:
                st.dataframe(
                    results,
                    use_container_width=True
                )
            else:
                st.info("No records found.")

        except Exception as e:

            if connection:
                connection.close()

            st.error(f"Query execution failed: {e}")

    else:
        st.error("Database connection failed.")