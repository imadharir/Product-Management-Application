from cassandra.cluster import Cluster

def connect_to_cassandra():
    # Connect to Cassandra
    cluster = Cluster(['localhost'])
    session = cluster.connect('mykeyspace')
    return cluster, session

def close_connection(cluster):
    # Close the connection
    cluster.shutdown()

def get_next_product_id(session):
    # Retrieve the current maximum product_id and increment by 1
    result = session.execute("SELECT MAX(product_id) FROM products")
    max_product_id = result.one().system_max_product_id
    return max_product_id + 1 if max_product_id is not None else 1

def add_product(name, price, category):
    cluster, session = connect_to_cassandra()

    # Get the next product_id
    product_id = get_next_product_id(session)

    session.execute(
        """
        INSERT INTO products (product_id, name, price, category)
        VALUES (%s, %s, %s, %s)
        """,
        (product_id, name, price, category)
    )

    print(f"Product added: {name}")
    close_connection(cluster)

def get_product(product_id):
    cluster, session = connect_to_cassandra()

    try:
        result = session.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        return result.one()

    except Exception as e:
        print(f"Error retrieving product details: {e}")
        return None

    finally:
        close_connection(cluster)


def update_product(product_id, new_price):
    cluster, session = connect_to_cassandra()
    session.execute("UPDATE products SET price = %s WHERE product_id = %s", (new_price, product_id))
    print(f"Product updated: {product_id}")
    close_connection(cluster)

def delete_product(product_id):
    cluster, session = connect_to_cassandra()
    session.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    print(f"Product deleted: {product_id}")
    close_connection(cluster)

def list_all_products():
    cluster, session = connect_to_cassandra()

    try:
        result = session.execute("SELECT * FROM products")
        products = result.all()
        return products

    except Exception as e:
        print(f"Error listing all products: {e}")
        return None

    finally:
        close_connection(cluster)

def search_products_by_category(category):
    cluster, session = connect_to_cassandra()

    try:
        result = session.execute("SELECT * FROM products WHERE category = %s ALLOW FILTERING", (category,))
        products = result.all()
        return products

    except Exception as e:
        print(f"Error searching products by category: {e}")
        return None

    finally:
        close_connection(cluster)

def count_products():
    cluster, session = connect_to_cassandra()

    try:
        result = session.execute("SELECT COUNT(*) FROM products")
        total_products = result.one().count
        return total_products

    except Exception as e:
        print(f"Error counting products: {e}")
        return None

    finally:
        close_connection(cluster)



def update_product_name(product_id, new_name):
    cluster, session = connect_to_cassandra()

    try:
        session.execute("UPDATE products SET name = %s WHERE product_id = %s", (new_name, product_id))
        print(f"Product name updated: {product_id}")

    except Exception as e:
        print(f"Error updating product name: {e}")

    finally:
        close_connection(cluster)

def search_products_by_price_range(min_price, max_price):
    cluster, session = connect_to_cassandra()

    try:
        result = session.execute("SELECT * FROM products WHERE price >= %s AND price <= %s ALLOW FILTERING", (min_price, max_price))
        products = result.all()
        return products

    except Exception as e:
        print(f"Error searching products by price range: {e}")
        return None

    finally:
        close_connection(cluster)



if __name__ == "__main__":
    # Example usage:

    # Add a product
    add_product("Laptop", 1200.0, "Electronics")
    add_product("Headphones", 100.0, "Electronics")
    add_product("Desk", 200.0, "Furniture")
    add_product("Blender", 60.0, "Appliances")
    add_product("Backpack", 40.0, "Fashion")
    add_product("Running Shoes", 80.0, "Sports and Outdoors")
    add_product("Coffee Maker", 50.0, "Appliances")
    add_product("Desk Chair", 150.0, "Furniture")
    add_product("Book: Introduction to Big Data", 29.99, "Books")
    add_product("Smartphone", 800.0, "Electronics")

    # Get product details
    added_product_id = 1  # Replace with the actual product_id generated in the add_product function
    get_product_result = get_product(added_product_id)

    if get_product_result:
        print(f"Product details: {get_product_result}")
    else:
        print("Failed to retrieve product details. Check your code and Cassandra setup.")

    # Update product price
    update_product(added_product_id, 1300.0)

    # Delete a product
    delete_product(added_product_id)

    # List all products
    all_products = list_all_products()
    if all_products:
        print("All Products:")
        for product in all_products:
            print(product)
    else:
        print("Failed to list all products. Check your code and Cassandra setup.")

    # Search products by category
    electronics_products = search_products_by_category("Electronics")
    if electronics_products:
        print("Electronics Products:")
        for product in electronics_products:
            print(product)
    else:
        print("No Electronics products found. Check your code and Cassandra setup.")

    # Count total products
    total_products_count = count_products()
    if total_products_count is not None:
        print(f"Total number of products: {total_products_count}")
    else:
        print("Failed to count products. Check your code and Cassandra setup.")

    # Update product name
    update_product_name(1, "Updated Laptop")

    # Search products by price range
    min_price = 50.0
    max_price = 100.0
    products_in_range = search_products_by_price_range(min_price, max_price)
    if products_in_range:
        print(f"Products within price range ${min_price} - ${max_price}:")
        for product in products_in_range:
            print(product)
    else:
        print("No products found within the specified price range. Check your code and Cassandra setup.")
