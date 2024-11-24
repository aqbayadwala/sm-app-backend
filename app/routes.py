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
        # print(f"Error during registration: {e}")

        return jsonify({"error": f"{e}"}), 500


# for creating a new daur entry
@sm_app.route("/createdaur", methods=["POST"])
@jwt_required()
def create_daur():
    data = request.json
    # print("code came here")
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


"""# Add students to daur
@sm_app.route("/addstudents", methods=["POST"])
@jwt_required()
def addstudents():
    data = request.json
    students = data[1]
    daur_id = data[0]["daurId"]

    Student.query.filter_by(daur_id=daur_id).delete()
    db.session.commit()

    new_students = []
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

        new_students.append(new_student)

    db.session.add_all(new_students)

    try:
        print("code before commit")
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("code arrived here")
        return (
            jsonify({"error": "something failed"}),
            400,
        )

    return jsonify({"message": "success"}), 200
"""


# Add students to daur
@sm_app.route("/addstudents", methods=["POST"])
@jwt_required()
def addstudents():
    data = request.json
    students = data[1]
    daur_id = data[0]["daurId"]

    current_students = Student.query.filter_by(daur_id=daur_id).all()

    current_its = {student.its for student in current_students}
    new_its = {student["its"] for student in students}

    its_to_delete = current_its - new_its

    Student.query.filter_by(daur_id=daur_id).filter(
        Student.its.in_(its_to_delete)
    ).delete(synchronize_session=False)

    for student_data in students:
        student = Student.query.filter_by(
            its=student_data["its"], daur_id=daur_id
        ).first()

        if student:
            student.name = student_data["name"]
            student.grade = student_data["grade"]
        else:
            new_student = Student(
                its=student_data["its"],
                name=student_data["name"],
                grade=student_data["grade"],
                daur_id=daur_id,
            )

            db.session.merge(new_student)

    try:
        # print("code before commit")
        db.session.commit()
        # print("code after commit")
    except IntegrityError as e:
        db.session.rollback()
        # print(f"Error: {str(e)}")  # Log the error for debugging
        return (
            jsonify({"error": "something failed"}),
            400,
        )

    return jsonify({"message": "success"}), 200


# When clicking edit daur on client
@sm_app.route("/getstudents/<int:id>")
def get_students(id):
    students = Student.query.filter_by(daur_id=id).all()

    students_data = [
        {
            "id": student.id,
            "name": student.name,
            "its": student.its,
            "grade": student.grade,
            "daur_id": id,
        }
        for student in students
    ]
    return jsonify({"message": "success", "students": students_data})


# to display daur cards
@sm_app.route("/fetchdaurs", methods=["GET"])
@jwt_required()
def fetch_daurs():
    moallim_its = get_jwt_identity()

    daurs = Daur.query.filter_by(moallim_id=moallim_its).all()
    daurs_list = [daur.to_dict() for daur in daurs]
    print(daurs_list)
    return jsonify(daurs_list), 200


# to edit daur name
@sm_app.route("/updatedaurname/<int:id>", methods=["POST"])
def updatedaurname(id):
    try:
        data = request.json
        new_name = data.get("daurName")

        daur = Daur.query.get(id)
        if not daur:
            return jsonify({"message": "Daur not found"}), 404

        daur.name = new_name
        db.session.commit()

        return jsonify({"message": "Daur name updated successfully"})

    except Exception as e:
        return jsonify({f"error": str(e)}), 500


# to delete daur
@sm_app.route("/deletedaur/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_daur(id):
    # print(id)
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
    try:
        return jsonify({"authenticated": True}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 401


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
        # print("login complete")
        return response
    else:
        return jsonify({"message": "nothing"}), 401
