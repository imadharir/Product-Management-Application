from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from cassandra.cluster import Cluster
from PIL import Image

app = Flask(__name__)
Bootstrap(app)

def connect_to_cassandra():
    cluster = Cluster(['localhost'])
    session = cluster.connect('mykeyspace')
    return cluster, session

def close_connection(cluster):
    cluster.shutdown()

def get_next_product_id(session):
    result = session.execute("SELECT MAX(product_id) FROM products")
    max_product_id = result.one().system_max_product_id
    return max_product_id + 1 if max_product_id is not None else 1

def add_product(name, price, category, image):
    cluster, session = connect_to_cassandra()

    product_id = get_next_product_id(session)

    # Save image to a directory
    original_image_path = f"static/images/{product_id}_{secure_filename(image.filename)}"
    image.save(original_image_path)

    # Open the original image and convert it to RGB mode
    with Image.open(original_image_path) as img:
        img = img.convert("RGB")

        # Resize the image to a uniform size (e.g., 300x300 pixels)
        img.thumbnail((300, 300))

        # Save the resized image to a new path
        resized_image_path = f"static/images/{product_id}_resized.jpg"
        img.save(resized_image_path)

    session.execute(
        """
        INSERT INTO products (product_id, name, price, category, image_url)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (product_id, name, price, category, f"images/{product_id}_resized.jpg")
    )

    print(f"Product added: {name}")
    close_connection(cluster)

def get_all_products():
    cluster, session = connect_to_cassandra()
    result = session.execute("SELECT * FROM products")
    products = result.all()
    close_connection(cluster)
    return products

def get_product_by_id(session, product_id):
    try:
        result = session.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        return result.one()

    except Exception as e:
        print(f"Error retrieving product details: {e}")
        return None

def update_product_price(session, product_id, new_price):
    try:
        session.execute("UPDATE products SET price = %s WHERE product_id = %s", (new_price, product_id))
        print(f"Product price updated: {product_id}")

    except Exception as e:
        print(f"Error updating product price: {e}")

def delete_product(session, product_id):
    try:
        session.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        print(f"Product deleted: {product_id}")

    except Exception as e:
        print(f"Error deleting product: {e}")

@app.route('/')
def index():
    products = get_all_products()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cluster, session = connect_to_cassandra()

    product = get_product_by_id(session, product_id)

    close_connection(cluster)

    if product:
        return render_template('product_detail.html', product=product)
    else:
        return render_template('error.html', message="Product not found")

@app.route('/add_product', methods=['GET', 'POST'])
def add_product_route():
    if request.method == 'POST':
        # Check if 'name' key exists in request.form
        if 'name' in request.form:
            name = request.form['name']
            price = float(request.form['price'])
            category = request.form['category']
            image = request.files['image']

            add_product(name, price, category, image)

            return redirect(url_for('index'))

    return render_template('add_product.html')

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product_route(product_id):
    cluster, session = connect_to_cassandra()

    if request.method == 'POST':
        new_price = float(request.form['new_price'])
        update_product_price(session, product_id, new_price)
        close_connection(cluster)
        return redirect(url_for('index'))

    product = get_product_by_id(session, product_id)

    close_connection(cluster)

    if product:
        return render_template('update_product.html', product=product)
    else:
        return render_template('error.html', message="Product not found")

@app.route('/delete_product/<int:product_id>')
def delete_product_route(product_id):
    cluster, session = connect_to_cassandra()

    delete_product(session, product_id)

    close_connection(cluster)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
