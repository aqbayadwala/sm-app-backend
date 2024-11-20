from app import sm_app, db
from flask import request, jsonify, make_response
from app.models import Moallim, Daur, Student
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
)


@sm_app.route("/")
def home():
    return "Hello"


@sm_app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        its = int(data.get("its"))
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        user = Moallim(its=its, name=name, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Successfully registered. Please login"})

    except Exception as e:
        print(f"Error during registration: {e}")

        return jsonify({"error": f"{e}"}), 500


# for creating a new daur entry
@sm_app.route("/createdaur", methods=["POST"])
@jwt_required()
def create_daur():
    data = request.json
    print("code came here")
    # after implementing auth, this has to be changed to fetch the moallim who is logged in
    moallim_its = get_jwt_identity()
    moallim = Moallim.query.filter_by(its=moallim_its).first()
    moallim = Moallim.query.first()
    if isinstance(data, dict):
        daur_name = data.get("daurName")
        new_daur = Daur(name=daur_name, moallim_id=moallim.its)
        db.session.add(new_daur)
        db.session.commit()

        daur_id = new_daur.id

        return jsonify({"daurId": daur_id}), 200


# Add students to daur
@sm_app.route("/addstudents", methods=["POST"])
@jwt_required()
def addstudents():
    data = request.json
    students = data[1]
    daur_id = data[0]["daurId"]

    Student.query.filter_by(daur_id=daur_id).delete()

    for student in students:
        student_its = student.get("its")
        student_name = student.get("name")
        student_grade = student.get("grade")

        new_student = Student(
            its=student_its,
            name=student_name,
            grade=student_grade,
            daur_id=daur_id,
        )
        db.session.add(new_student)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("code arrived here")
            return (
                jsonify({"error": "something failed"}),
                400,
            )

    return jsonify({"message": "success"}), 200


@sm_app.route("/getstudents/<int:id>")
def get_students(id):
    daur_id = id
    students = Student.query.filter_by(daur_id=id).all()

    students_data = [
        {
            "id": student.id,
            "name": student.name,
            "its": student.its,
            "grade": student.grade,
        }
        for student in students
    ]
    return jsonify({"message": "success", "students": students_data})


# to display daur cards
@sm_app.route("/fetchdaurs", methods=["GET"])
@jwt_required()
def fetch_daurs():
    daurs = Daur.query.all()
    daurs_list = [daur.to_dict() for daur in daurs]
    return jsonify(daurs_list), 200


# to delete daur
@sm_app.route("/deletedaur/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_daur(id):
    print(id)
    daur = Daur.query.filter_by(id=id).first()

    if daur is None:
        return jsonify({"message": "daur not found"})

    db.session.delete(daur)
    db.session.commit()

    return jsonify({"message": "success"}), 200


# auth check for protected routes
@sm_app.route("/auth-check", methods=["GET"])
@jwt_required()
def auth_check():
    return jsonify({"authenticated": True}), 200


# Authentication/Login route
@sm_app.route("/login", methods=["POST"])
def login():
    username = request.json.get("email")
    password = request.json.get("password")

    moallim = Moallim.query.filter_by(email=username).first()

    if moallim and moallim.check_password(password):
        access_token = create_access_token(identity=str(moallim.its))
        response = jsonify({"message": "Login Successful"})
        set_access_cookies(response, access_token)
        print("login complete")
        return response
    else:
        return jsonify({"message": "nothing"}), 401
