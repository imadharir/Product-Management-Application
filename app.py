from flask import Flask, render_template, request, redirect, url_for
from cassandra.cluster import Cluster


app = Flask(__name__)
 

cluster = Cluster(['localhost'])
session = cluster.connect('mykeyspace')


def get_all_products():
    result = session.execute("SELECT * FROM products")
    return result.all()


def get_product_by_id(product_id):
    result = session.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    return result.one()


def add_product(name, price, category):
    product_id = get_next_product_id()
    session.execute(
        """
        INSERT INTO products (product_id, name, price, category)
        VALUES (%s, %s, %s, %s)
        """,
        (product_id, name, price, category)
    )


def update_product_price(product_id, new_price):
    session.execute("UPDATE products SET price = %s WHERE product_id = %s", (new_price, product_id))


def delete_product(product_id):
    session.execute("DELETE FROM products WHERE product_id = %s", (product_id,))


def get_next_product_id():
    result = session.execute("SELECT MAX(product_id) FROM products")
    max_product_id = result.one().system_max_product_id
    return max_product_id + 1 if max_product_id is not None else 1


@app.route('/')
def index():
    products = get_all_products()
    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    return render_template('product_detail.html', product=product)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product_route():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']

        add_product(name, price, category)

        return redirect(url_for('index'))

    return render_template('add_product.html')


@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product_route(product_id):
    if request.method == 'POST':
        new_price = float(request.form['new_price'])
        update_product_price(product_id, new_price)
        return redirect(url_for('index'))

    product = get_product_by_id(product_id)
    return render_template('update_product.html', product=product)


@app.route('/delete_product/<int:product_id>')
def delete_product_route(product_id):
    delete_product(product_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
