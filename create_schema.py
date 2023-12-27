from cassandra.cluster import Cluster

def create_schema():
    try:
        cluster = Cluster(['localhost'])
        session = cluster.connect()

        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS mykeyspace
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)

        session.set_keyspace('mykeyspace')

        session.execute("""
            CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY,
            name TEXT,
            price DECIMAL,
            category TEXT,
            image_url TEXT
            ) 
        """)

        print("Schema creation successful. Connected to Cassandra.")

    except Exception as e:
        print(f"Error connecting to Cassandra: {e}")

    finally:
        cluster.shutdown()
        print("Connection closed.")

if __name__ == "__main__":
    create_schema()
