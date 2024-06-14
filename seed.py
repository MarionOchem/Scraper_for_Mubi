import psycopg2

# Connect to the db
conn = psycopg2.connect(
    dbname="bleauinfo",
    user="postgres",
    password="hello",
    host="localhost",
    port="5432"
)

# Open a cursor to perform db operations 
cur = conn.cursor()

# Create tables if not exists
''' cur.execute(sql)'''

# Would i need a transaction ? 
# Execute the insertion 



cur.close()
conn.close()