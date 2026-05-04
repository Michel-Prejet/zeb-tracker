import psycopg

def connection():
    """
    :return: a connection to the database for the application.
    """
    return psycopg.connect(
        dbname="zeb-tracker",
        user="postgres",
        password="55757089",
        host="localhost",
        port=5432
    )