from cassandra.cluster import Cluster

def create_schema():
    try:
        # Connect to Cassandra
        cluster = Cluster(['localhost'])
        session = cluster.connect()

        # Create keyspace
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS mykeyspace
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)

        # Use keyspace
        session.set_keyspace('mykeyspace')

        # Create table with a counter column for product number
        session.execute("""
            CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY,
            name TEXT,
            price DECIMAL,
            category TEXT,
            
            ) 
        """)

        print("Schema creation successful. Connected to Cassandra.")

    except Exception as e:
        print(f"Error connecting to Cassandra: {e}")

    finally:
        # Close the connection
        cluster.shutdown()
        print("Connection closed.")

if __name__ == "__main__":
    create_schema()
