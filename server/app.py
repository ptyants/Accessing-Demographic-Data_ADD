from flask import Flask, flash, current_app, jsonify, render_template, request, abort, redirect, url_for, session, make_response
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

from sqlalchemy import Integer, String, ForeignKey, Column, Date, func
from datetime import date
from sqlalchemy.orm import relationship, joinedload
import mysql.connector

from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps
from datetime import datetime, timedelta

# GG-auth 2.0
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from google.oauth2 import id_token

from pip._vendor import cachecontrol
import plotly.graph_objects as go

import requests
import os
from flask_sslify import SSLify


from chema_function import LifeStatusSchema


# from bokeh.embed import components
# from bokeh.plotting import figure
# from bokeh.models import Range1d
import plotly.express as px
import plotly.io as pio
import numpy as np
import pandas as pd

# from sqlalchemy.engine import URL






app = Flask(__name__)
sslify = SSLify(app)

CORS(app)
# origins cho phép bất kì domain nào truy cập
cors = CORS(app, resources={
    r"/api/*": {'origins': "*"}
})


app.secret_key = "Key-chốnghacker-123."
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%40nts28PtMySQL@localhost/citizen_db"
# app.permanent_session_lifetime = datetime.timedelta(seconds=60)
# app.config['TIMEZONE'] = 'UTC'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID = "1028993107715-nkl0etge0ks4i3r5mtjmkr6bnbclrg46.apps.googleusercontent.com"

# Lấy đường dẫn tới thư mục chứa tệp mã nguồn Python
current_dir = os.path.dirname(__file__)

# Đường dẫn tới tệp client_secret.json
client_secrets_file = os.path.join(current_dir, 'client_secret.json')

flow =Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    )



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
        token = request.cookies.get('token')
        referrer = request.path

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


def login_is_required(f):
    def warpper(*args, **kwargs):
        if 'google_id' not in session:
            return abort(401)
        else:
            return f()
    return warpper




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







@app.route('/login')
def login():
    authorize_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorize_url)



@app.route('/callback')
def callback():

    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")

    if id_info and id_info.get("name"):
        current_datetime = datetime.utcnow()
        expiration_time = current_datetime + timedelta(minutes=60)
        print("ok - Auth 2.0 has token")
        token = jwt.encode({
            'user': id_info.get("name"),
            'exp': expiration_time
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        referrer = session.get('referrer', '/')

        response = make_response(redirect(referrer))
        referrer = session.pop('referrer', '/')

        # Lưu token trong cookie của người dùng
        response.set_cookie('token', token, max_age=3600, httponly=True)

        return response
    else:
        return make_response('Could not verify!', 401, {'www-Authenticate': 'Basic realm="Login Required"'})

    # return redirect("/protectgg")


@app.route('/protectgg')
@token_required
def protectgg():
    print(session.get)
    return f"Hello {session.get('name', None)}! <br/> <a href='/logout'><button>Logout</button></a>"

# @app.route('/logout')
# def logout():
#     session.clear()
#     print(session.get)
#     return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('home')))
    response.set_cookie('token', '', expires=0)  # Xóa cookie bằng cách đặt thời gian hết hạn là 0
    return response


@app.route('/loginAsAdmin', methods=['POST', 'GET'])
def loginAsAdmin():
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

            response = make_response(redirect(referrer))
            referrer = session.pop('referrer', '/')

            # Lưu token trong cookie của người dùng
            response.set_cookie('token', token, max_age=3600, httponly=True)

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





@app.route('/admin/edit_person_info', methods=["GET", "POST"])
def edit_Person_info():
    life_statuses = Life_status.query.all()
    message=""
    if request.method == "POST":
        data = request.form
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

        message = "Dữ liệu đã được gửi thành công!"
    
    return render_template("Born_CERT.html", life_statuses=life_statuses, message=message)




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
            return redirect('/admin/search_Person_info')  # Chuyển hướng đến trang thông báo thành công hoặc trang chính
        else:
            # Nếu không tìm thấy thông tin cá nhân
            return jsonify({"error": "Không tìm thấy người với id đã cho."}), 404

    # Nếu là GET request hoặc khi xử lý POST request xong
    return render_template("sign_Citizen.html")
    


@app.route('/admin/edit_houseHold')
def edit_houseHold():
    return "<h1>This's Edit HouseHold</h1>"




@app.route('/graph', methods=["GET", "POST"])
def graph():
    selected_life_status_id = 1
    if request.method == "POST":
        print('ok')
        selected_life_status_id = request.form.get("Ls_id")

    person_info = Person_info.query.all()
    citizen_info = Citizen_info.query.all()
    life_statuses = Life_status.query.all()

    # Đếm số lượng tương quan giữa người dân và công dân
    person_info_count = len(person_info)
    citizen_info_count = len(citizen_info)

    

    # Tạo biểu đồ tròn
    labels = ['Person Info', 'Citizen Info']
    values = [person_info_count, citizen_info_count]

    fig1 = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig1.update_layout(title_text="Tương quan số lượng Person Info và Citizen Info")


    count_by_life_status_id = db.session.query(func.count(Person_info.id)).join(Life_status).filter(Life_status.id == Person_info.Ls_id).filter(Life_status.id == selected_life_status_id).scalar()

    # Tạo dữ liệu mẫu
    np.random.seed(42)
    x = np.random.normal(loc=0, scale=1, size=1000)

    # Tạo biểu đồ histogram
    fig2 = go.Figure(data=[go.Histogram(x=x, histnorm='probability')])

    # Cấu hình box plot
    fig2.update_layout(
        title='Phân phối của dữ liệu',
        xaxis_title='Giá trị',
        yaxis_title='Tần suất',
        bargap=0.05,
        xaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True
        ),
        yaxis=dict(
            showline=True,
            showgrid=True,
            showticklabels=True
        ),
    )

    # Tạo box
    fig2.update_traces(
        xbins=dict(
            start=-3,
            end=3,
            size=0.5
        ),
        marker=dict(color='blue'),
        selector=dict(type='histogram')
    )

    # Hiển thị tối đa 5 box
    fig2.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        showlegend=False,
        bargap=0.2,
        xaxis=dict(
            title='Giá trị',
            showline=True,
            showgrid=True,
            showticklabels=True
        ),
        yaxis=dict(
            title='Tần suất',
            showline=True,
            showgrid=True,
            showticklabels=True
        ),
        boxmode='group',
        boxgroupgap=0.1,
        boxgap=0.2
    )

    # Chuyển đổi biểu đồ thành HTML
    pie_html = fig1.to_html(full_html=False)
    histogram_html = fig2.to_html(full_html=False)

    return render_template('graph.html', pie_html=pie_html, histogram_html=histogram_html, life_statuses=life_statuses, person_info_count=person_info_count, count_by_life_status_id=count_by_life_status_id)





   
        
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



