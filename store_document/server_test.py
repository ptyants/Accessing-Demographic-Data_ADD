import mysql.connector
from sqlalchemy import Integer, String, ForeignKey, Column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS
from flask import Flask, Blueprint, current_app, jsonify, render_template, request, abort
from sqlalchemy.engine import URL
import os





app = Flask(__name__)

app.secret_key = "Key-chốnghacker-TB02BIuIt3w7DiJKmQu2oHGwZdJOrtdjuXvbTqVa4dg0DdlJSDf2aOvmd1DX2qA."
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%40nts28PtMySQL@localhost/our_user"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Category(db.Model):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    product = relationship('Product', backref="category", lazy=True)

class Product(db.Model):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)



@app.route('/test', methods=['POST'])
def test():
    if request.method == 'POST':
        try:
            data = request.json['name']
            return f"<h1>{data}</h1>"
        except KeyError  as e:
            return f"<h1>{e}</h1>"
    return f"<h1>không có</h1>"

@app.route('/create_product', methods=["POST"])
def create_product():
    # bổ sung thêm trường hợp sai phương thức truyền như yêu cầu body mà lại truyền parameter
    # và trường hợp chưa có dữ liệu quan hệ trong database
    if request.method == 'POST':
        data = request.json  # Sử dụng request.json cho dữ liệu JSON
        print(data['category_id'])  # In ra giá trị category_id từ Postman
        if not data or 'name' not in data or 'description' not in data or 'category_id' not in data:
            abort(400, description="Thiếu các trường bắt buộc")
            
        new_product = Product(name=data['name'], description=data['description'], category_id=data['category_id'])
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Tạo sản phẩm thành công'}), 201


@app.route('/products', methods=["GET"])
def get_all_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_list.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category_id': product.category_id
        })
    return jsonify({'products': product_list})

@app.route('/products/<int:product_id>', methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'category_id': product.category.name
        })
    else:
        return jsonify({'message': 'Product not found'}), 404
    
@app.route('/update/<int:product_id>', methods=["PUT"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if product:
        data = request.form
        product.name = data['name']
        product.description = data['description']
        product.category_id = data['category_id']
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'})
    else:
        return jsonify({'message': 'Product not found'}), 404
    
@app.route('/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    else:
        return jsonify({'message': 'Product not found'}), 404






@app.route('/create', methods=["POST"])
def create():
    return render_template("index.html")

@app.route('/create_category', methods=["POST"])
def create_category():
    if request.method == 'POST':
        data = request.json  # Sử dụng request.json cho dữ liệu JSON
        if not data or 'name' not in data:
            abort(400, description="Thiếu trường bắt buộc 'name' khi tạo category")
            
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': 'Tạo category thành công'}), 201

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    CORS(app)
    app.run(debug=True)



