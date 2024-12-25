import mysql.connector

conn = mysql.connector.connect(host="127.0.0.1", port=3306,
                               user="root", password="qwerty")
class SQLHelper:

    def __init__(self, dbname, table_name):
        self.dbname = dbname
        self.table_name = table_name
        self.conn = mysql.connector.connect(host="127.0.0.1", port=3306,
                               user="root", password="qwerty", database = self.dbname)

    def RunQuery(self, query, verbose=True):
        # Create a cursor
        cur = self.conn.cursor()

        # Execute the query
        cur.execute(query)

        # Commit the changes (assuming you are making changes to the database)
        self.conn.commit()

        if verbose:
            print("Query Executed")

    def ShowTables(self, dbname):

        # Create connecation
        cur = conn.cursor()

        # Use Database
        cur.execute(f"USE {dbname}")
        
        # Execute a query
        cur.execute("SHOW TABLES")
        
        # Fetch one result
        row = cur.fetchall()

        print([db for db in row])


    def ShowDatabase(self):
        cur = conn.cursor()
        
        # Execute a query
        cur.execute("SHOW DATABASES")
        
        # Fetch one result
        row = cur.fetchall()

        print([db for db in row])

    def __get_datetime__(self):
        # Get a cursor
        cur = conn.cursor()
        
        # Execute a query
        cur.execute("SELECT current_timestamp()")
        
        # Fetch one result
        row = cur.fetchone()
        
        print("Current date is: {0}".format(row[0]))
        
        # Close connection
        # conn.close()