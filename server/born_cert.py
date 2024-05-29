from flask import current_app, Blueprint, jsonify, request, abort
from flask.helpers import flash
from app import db, Person_info, Life_status




born_cert = Blueprint("born_cert", __name__)


@born_cert.route('/api/test/sgin_Born_CERT', methods=["GET", "POST"])
def sgin_Born_CERT():
    if request.method == "GET":
        with current_app.app_context():
            life_statuses = current_app.extensions['sqlalchemy'].db.session.query(Life_status).all()
        return jsonify({'life_status_data': life_statuses}), 200

    if request.method == "POST":
        data = request.json
        if (not data or 'name' not in data or 'address' not in data or 'father_name' not in data
            or 'mother_name' not in data or 'Ls_id' not in data or 'born_in' not in data):
            abort(400, description="Thiếu các trường bắt buộc")

        with current_app.app_context():
            newBorn_CERT = current_app.extensions['sqlalchemy'].db.session.add(Person_info(
                name=data['name'],
                address=data['address'],
                father_name=data['father_name'],
                mother_name=data['mother_name'],
                Ls_id=data['Ls_id'],
                born_in=data['born_in']
            ))
            current_app.extensions['sqlalchemy'].db.session.commit()

        return jsonify({'message': 'Đã đăng kí thông tin của công dân thành công!'}), 201








@born_cert.route('/api/test/born_cert', methods=["GET", "POST"])
def test_connect():
    if request.method == "GET":
        return jsonify({'message': 'Connect successfully'}), 201
    elif request.method == "POST":
        # Handle POST request logic here
        pass

