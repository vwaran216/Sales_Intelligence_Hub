from database import get_connection


def authenticate_user(username, password):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT user_id, username, password, branch_id, role, email
        FROM users
        WHERE username = %s
          AND password = %s
    """

    cursor.execute(query, (username, password))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user