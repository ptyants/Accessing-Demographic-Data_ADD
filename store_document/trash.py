# # Define a custom JSONEncoder to handle serialization of SQLAlchemy models
# class CustomJSONEncoder(JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj.__class__, DeclarativeMeta):
#             # If obj is a SQLAlchemy model, convert it to a dictionary
#             return {column.key: getattr(obj, column.key) for column in obj.__table__.columns}
#         elif isinstance(obj, date):
#             # If obj is a date, convert it to a string
#             return obj.isoformat()
#         return super().default(obj)

# app.json_encoder = CustomJSONEncoder


# @app.route('/api/sgin_citizen', methods=["POST"])
# def sgin_citizen():
    # if request.method == "POST":
    #     data = request.json
    #     if not data or 'name' not in data or 'houseHold_id' not in data or 'person_info' not in data:
    #         abort(400, description="Thiếu các trường bắt buộc")

    #     # Extract person_info data from the request
    #     person_info_data = data['person_info']

    #     # Create a new Person_info instance
    #     new_person_info = Person_info(**person_info_data)
    #     db.session.add(new_person_info)
    #     db.session.flush()  # Make sure the person_info id is available for the next step

    #     # Create a new Citizen_info instance
    #     new_citizen = Citizen_info(name=data['name'], houseHold_id=data['houseHold_id'], person_info_id=new_person_info.id)
    #     db.session.add(new_citizen)
    #     db.session.commit()

        # return jsonify({'message': 'Đã đăng kí thông tin của công dân thành công!'}), 201



@app.route('/login')
def login():

    auth = request.authorization

    if auth and auth.password == "123":
        token = jwt.encode({
            'user': auth.username,
            'experation': str(datetime.datetime.utcnow() + datetime.timedelta(minutes=60))
        }, app.config['SECRET_KEY']
        )

        return jsonify({'token' : token})


    return make_response('Could not verify!', 401, 
        {'www-Authenticate' : 'Basic realm = "Login Required"'})




def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = request.args.get('token')
        token = request.cookies.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 403
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.decoded_token = payload  # Lưu thông tin của token cho mục đích gỡ lỗi
            print(payload['user'])
        except jwt.ExpiredSignatureError:
            print("Token Expired Error: Signature has expired")
            return jsonify({'Alert!': 'Token has expired'}), 403
        except jwt.InvalidTokenError as e:
            print("Token Decode Error:", e)
            return jsonify({'Alert!': 'Invalid Token'}), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/pro')
@token_required
def protected():
    if 'decoded_token' in request:
        # lấy dữ liệu trong token
        user_from_token = request.decoded_token.get("user", "Unknown User")
        return jsonify({'message': f'This is only available for people with valid tokens. User: {user_from_token}'})
    else:
        # Chuyển hướng đến trang /login nếu không có token hợp lệ
        return redirect(url_for('login'))


# Add your OAuth provider configuration here
# Cấu hình OAuth cho Google
# oauth = OAuth(app)
# google = oauth.remote_app(
#     'google',
#     consumer_key='YOUR_CLIENT_ID',
#     consumer_secret='YOUR_CLIENT_SECRET',
#     request_token_params={},
#     base_url=None,
#     request_token_url=None,
#     access_token_method='POST',
#     access_token_url='https://oauth2.googleapis.com/token',
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
# )


# @app.route('/login/<provider_name>')
# def login_oauth(provider_name):
#     return oauth_provider.authorize(callback=url_for('oauth_authorized', provider_name=provider_name, _external=True))

# @app.route('/login/<provider_name>/callback')
# def oauth_authorized(provider_name):
#     response = oauth_provider.authorized_response()

#     if response is None or response.get('access_token') is None:
#         flash('Authentication failed.')
#         return redirect(url_for('login'))

#     session['provider_name_token'] = (provider_name, response['access_token'])

#     # You can store additional user information in session or database as needed

#     return redirect(url_for('citien_view'))

# @oauth_provider.tokengetter
# def get_oauth_token():
#     return session.get('provider_name_token')



@app.route('/graph')
def graph():
    person_info = Person_info.query.all()
    citizen_info = Citizen_info.query.all()

    person_info_count = len(person_info)
    citizen_info_count = len(citizen_info)
    # Tạo biểu đồ tròn
    labels = ['Person Info', 'Citizen Info']
    values = [person_info_count, citizen_info_count]




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