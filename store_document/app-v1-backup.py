from flask import Flask, flash, current_app, jsonify, render_template, request, abort, redirect, url_for, session, make_response
from json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta

from sqlalchemy import Integer, String, ForeignKey, Column, Date
from datetime import date
from sqlalchemy.orm import relationship, joinedload
import mysql.connector

from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps
from datetime import datetime, timedelta


from chema_function import LifeStatusSchema
# from flask_oauthlib.client import OAuth


# from bokeh.embed import components
# from bokeh.plotting import figure
# from bokeh.models import Range1d
import plotly.express as px
import plotly.io as pio
import numpy as np
import pandas as pd

# from sqlalchemy.engine import URL






app = Flask(__name__)

CORS(app)
# origins cho phép bất kì domain nào truy cập
cors = CORS(app, resources={
    r"/api/*": {'origins': "*"}
})




app.secret_key = "Key-chốnghacker-123."
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%40nts28PtMySQL@localhost/citizen_db"
# app.permanent_session_lifetime = datetime.timedelta(seconds=60)
app.config['TIMEZONE'] = 'UTC'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



class Citizen_info(db.Model): # khi đã là công dân
    id = Column(Integer, primary_key=True)
    houseHold_id = Column(Integer, ForeignKey('household.id'), nullable=True)
    person_info_id = Column(Integer, ForeignKey('person_info.id'))


class Person_info(db.Model): #tương đương với giấy khai sinh
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable = False)
    address = Column(String(100))
    father_name = Column(String(100))
    mother_name = Column(String(100))
    Ls_id = Column(Integer, ForeignKey('life_status.id'))
    Ms = Column(String(10), default='Single') # Ms: tình trang hôn nhân
    born_in = Column(String(100), nullable = False) # Nơi sinh
    date_birth = Column(Date) # ngày tháng năm sinh
    # Define relationships
    citizen_info = relationship('Citizen_info', backref='person_info', lazy=True)


class Life_status(db.Model):
    id = Column(Integer, primary_key=True)
    Ns = Column(String(100), nullable = False) # Ns: name Life status, tên loại tình trạng này
    describe = Column(String(100)) # Mô tả loại tình trạng này
    # Define relationship
    person_info = relationship('Person_info', backref='life_status', lazy=True)


class Household(db.Model):
    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    HH = Column(Integer, ForeignKey('citizen_info.id')) # HH là người đúng tên hộ gia đình
    # Define relationship with explicit foreign_keys
    citizens = relationship('Citizen_info', backref='household', lazy=True, foreign_keys=[HH])

class User(db.Model):
    id = Column(Integer, primary_key=True)



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = request.args.get('token')
        token = request.cookies.get('token')
        # referrer = session.get('target_path', '/')
        referrer = request.path
        print('hi')
        print(referrer)
        if not token:
            session['referrer'] = referrer
            return redirect(url_for('login'))  # Chuyển hướng đến trang /login nếu không có token
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.decoded_token = payload  # Lưu thông tin của token cho mục đích gỡ lỗi
            print(payload['user'])
        except jwt.ExpiredSignatureError:
            print("Token Expired Error: Signature has expired")
            return jsonify({'Alert!': 'Token has expired', 'Admin': 'Cút ra hacker Lord'}), 403
        except jwt.InvalidTokenError as e:
            print("Token Decode Error:", e)
            return jsonify({'Alert!': 'Invalid Token'}), 403
        return f(*args, **kwargs)
    return decorated



@app.route('/')
def home():
    return render_template('home_page.html')

@app.route('/unprotected')
def unprotected():
    return jsonify({'message': 'Anyone can view this!.'})


@app.route('/protect')
@token_required
def protected():
    # Đoạn mã khác giữ nguyên
    if request.decoded_token:
        user_from_token = request.decoded_token.get("user", "Unknown User")
        return jsonify({'message': f'This is only available for people with valid tokens. User: {user_from_token}'})
    else:
        # Đoạn mã này sẽ không được chạy nếu có token hợp lệ
        return jsonify({'Alert!': 'This should not be reachable without a valid token.'})




@app.route('/login', methods=['POST', 'GET'])
def login():
    referrer = session['referrer']

    if request.method == 'POST':
        auth = request.form
        if auth and auth.get('password') == "12":
            current_datetime = datetime.utcnow()
            expiration_time = current_datetime + timedelta(minutes=60)
            print("ok")
            token = jwt.encode({
                'user': auth.get('username'),
                'exp': expiration_time
            }, app.config['SECRET_KEY'], algorithm='HS256')

            # response_data = {'token': token, 'referrer': referrer}
            # response = make_response(jsonify(response_data))

            response = make_response(redirect(referrer))
            referrer = session.pop('referrer', '/')

            # Lưu token trong cookie của người dùng
            response.set_cookie('token', token, max_age=3600, httponly=True)

            #  # Kiểm tra và chuyển hướng người dùng về trang trước đó nếu có
            # if 'referrer' in request.cookies:
            #     return redirect(request.cookies.get('referrer'))

            # reset session

            return response
        else:
            return make_response('Could not verify!', 401, {'www-Authenticate': 'Basic realm="Login Required"'})
    
    return render_template('login.html')


# 'exp': exp_timestamp





# def get_life_status():
#     # Xử lý logic để lấy thông tin về trạng thái sống
#     # Ví dụ:
#     life_status_data = Life_status.query.all()
#     life_status_list = []

#     for life_status in life_status_data:
#         life_status_list.append({
#             'id': life_status.id,
#             'Ns': life_status.Ns,
#             'describe': life_status.describe,
#             # Thêm các trường khác nếu cần
#         })

#     return jsonify({'life_status': life_status_list}), 200


@app.route('/citien_view')
def citien_view():
    return "<h1>This's citizen view</h1>"



@app.route('/admin/edit_life_status', methods=["GET", "POST"])
@token_required
def edit_life_status():
    if 'message' in session:
        message = session.pop('message', None)
        flash(message)
    else:
        message = None
    if request.method == "GET":
        # Hiển thị trang HTML với danh sách trạng thái sống
        life_statuses = Life_status.query.all()
        return render_template("life_status.html", life_statuses=life_statuses)
    
    elif request.method == "POST":
        # Xử lý thêm trạng thái sống mới
        data = request.form
        if (not data or 'Ns' not in data or 'describe' not in data):
            abort(400, description="Thiếu các trường bắt buộc")

        new_life_status = Life_status(Ns=data['Ns'], describe=data['describe'])
        db.session.add(new_life_status)
        db.session.commit()
        session['message'] = 'Trạng thái sống đã được thêm'
        # Sau khi thêm, chuyển hướng lại trang HTML
        return redirect(url_for('edit_life_status'))

    return render_template("life_status.html")

@app.route('/admin/edit_life_status/<int:status_id>', methods=["GET"])
@token_required
def delete_life_status(status_id):
    life_status = Life_status.query.get_or_404(status_id)
    db.session.delete(life_status)
    db.session.commit()
    session['message'] = 'Trạng thái sống đã được xóa'
    return redirect(url_for('edit_life_status'))





@app.route('/admin/edit_person_info')
def edit_Person_info():
    life_statuses = Life_status.query.all()
    
    return render_template("Born_CERT.html", life_statuses=life_statuses)




@app.route('/admin/edit_citizens')
def edit_Citizens():
    if request.method == "GET":
        # Hiển thị trang HTML với danh sách trạng thái sống
        life_statuses = Life_status.query.all()
        return render_template("life_status.html", life_statuses=life_statuses)
    
    elif request.method == "POST":
        # Xử lý thêm trạng thái sống mới
        data = request.form
        if (not data or 'Ns' not in data or 'describe' not in data):
            abort(400, description="Thiếu các trường bắt buộc")

        new_life_status = Life_status(Ns=data['Ns'], describe=data['describe'])
        db.session.add(new_life_status)
        db.session.commit()
        session['message'] = 'Trạng thái sống đã được thêm'
        # Sau khi thêm, chuyển hướng lại trang HTML
        return redirect(url_for('edit_life_status'))
    return 0

def findPerson_info(id):
    person_info = Person_info.query.options(joinedload(Person_info.life_status)).filter_by(id=id).first()
    return person_info

@app.route('/admin/edit_citizens/<int:id>', methods=["GET"])
def check_Citizens_id(id):
    person_info = findPerson_info(id)
    if person_info:
        # Nếu tìm thấy người dựa trên id
        person_data = {
            "id": person_info.id,
            "name": person_info.name,
            "address": person_info.address,
            "father_name": person_info.father_name,
            "mother_name": person_info.mother_name,
            "Ls_id": person_info.Ls_id,
            "Ms": person_info.Ms,
            "born_in": person_info.born_in,
            "date_birth": person_info.date_birth.strftime('%Y-%m-%d') if person_info.date_birth else None,
            # Các trường dữ liệu khác nếu cần
        }
        # Thêm dữ liệu từ bảng Life_status
        if person_info.life_status:
            life_status_data = {
                "Ls_id": person_info.life_status.id,
                "Ns": person_info.life_status.Ns,
                "describe": person_info.life_status.describe,
            }
            person_data["life_status"] = life_status_data
        
        return jsonify(person_data)
    else:
        # Nếu không tìm thấy người dựa trên id
        return jsonify({"error": "Không tìm thấy người với id đã cho."}), 404
    

@app.route('/admin/search_Person_info', methods=["GET"])
def display_citizens_html():
    return render_template("Citizen.html", id=id)

@app.route('/sign_Citizen', methods=["GET", "POST"])
def sign_Citizen():
    if request.method == "POST":
        # Lấy dữ liệu từ form gửi lên
        person_id = request.form.get('person_id')

        # Kiểm tra xem person_info có tồn tại và có đủ thông tin cần thiết không
        person_info = findPerson_info(person_id)
        if person_info:
            required_fields = ['name', 'address', 'father_name', 'mother_name', 'born_in']
            for field in required_fields:
                if not getattr(person_info, field):
                    return jsonify({'error': f'Vui lòng nhập đầy đủ thông tin cho trường {field}.'}), 400

            # Nếu tất cả các trường đều được nhập đúng
            # Thực hiện tạo mới Citizen_info
            new_citizen = Citizen_info(person_info_id=person_id)
            db.session.add(new_citizen)
            db.session.commit()
            
            # Chuyển hướng hoặc hiển thị thông báo thành công
            return redirect('/success')  # Chuyển hướng đến trang thông báo thành công hoặc trang chính
        else:
            # Nếu không tìm thấy thông tin cá nhân
            return jsonify({"error": "Không tìm thấy người với id đã cho."}), 404

    # Nếu là GET request hoặc khi xử lý POST request xong
    return render_template("sign_Citizen.html")
    


@app.route('/admin/edit_houseHold')
def edit_houseHold():
    return 0




@app.route('/graph')
def graph():
    # Tạo dữ liệu mẫu
    x = [i for i in range(100)]
    y = [np.sin(i) for i in x]

    # Tạo đồ thị Plotly
    fig = px.line(x=x, y=y, title="Plotly Plot in Flask")

    # Chuyển đồ thị thành HTML
    graph_html = pio.to_html(fig, full_html=False)

    # Tạo dữ liệu mô phỏng cho dashboard
    np.random.seed(42)
    gender = np.random.choice([0, 1], size=1000, p=[0.48, 0.52])
    age = np.random.randint(18, 81, size=1000)
    data = {'Age': age, 'Gender': gender}
    dashboard_fig = px.histogram(data, x="Age", color="Gender", marginal="box", nbins=20, labels={'Age': 'Tuổi', 'Gender': 'Giới tính'})
    dashboard_fig.update_layout(title_text="Biểu đồ Tuổi và Giới tính")

    # Chuyển đồ thị dashboard thành HTML
    dashboard_html = pio.to_html(dashboard_fig, full_html=False)




    # Chuyển đến trang HTML chứa cả hai đồ thị
    return render_template('graph.html', graph_html=graph_html, dashboard_html=dashboard_html)

   
        
@app.route('/api/sgin_Born_CERT', methods=["GET", "POST"])
def sgin_Born_CERT():
    # if request.method == "GET":
    #     life_statuses = Life_status.query.all()
    #     life_status_schema = LifeStatusSchema(many=True)
    #     result = life_status_schema.dump(life_statuses)
    #     print(result)
    #     return jsonify({'life_status_data': result}), 200

    if request.method == "POST":
        data = request.json
        if (not data or 'name' not in data or 'address' not in data or 'father_name' not in data
            or 'mother_name' not in data or 'Ls_id' not in data or 'born_in' not in data or 'date_birth' not in data):
            print(data)
            abort(400, description="Thiếu các trường bắt buộc")

      
        newBorn_CERT = Person_info(
            name=data['name'],
            address=data['address'],
            father_name=data['father_name'],
            mother_name=data['mother_name'],
            Ls_id=data['Ls_id'],
            born_in=data['born_in'],
            date_birth = data['date_birth']
        )
        print("ok1")
        db.session.add(newBorn_CERT)
        print("ok2")
        db.session.commit()

        return jsonify({'message': 'Đã đăng kí thông tin của công dân thành công!'}), 201

@app.route('/api/get_life_status', methods=["GET"])
def get_life_status():
    if request.method == "GET":
        life_statuses = Life_status.query.all()
        life_status_schema = LifeStatusSchema(many=True)
        result = life_status_schema.dump(life_statuses)
        print(result)
        return jsonify({'life_status_data': result}), 200





@app.route('/api/test', methods=["GET", "POST"])
def test_api_connect():
    if request.method == "GET":
        return jsonify({'message': 'Connect successfully'}), 201
    elif request.method == "POST":
        # Handle POST request logic here
        pass
@app.route('/test', methods=["GET", "POST"])
def test_connect():
    if request.method == "GET":
        return jsonify({'message': 'Connect successfully'}), 201
    elif request.method == "POST":
        # Handle POST request logic here
        pass


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # from pyngrok import ngrok
    # public_url = ngrok.connect(80)
    from born_cert import born_cert
    app.register_blueprint(born_cert)
    app.run(debug=True)



