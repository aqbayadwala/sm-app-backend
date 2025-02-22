# Import statements

# Import app object, db object, and jwt object instances
from app import sm_app, db, jwt

# Helper functions
from flask import request, jsonify, make_response
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    get_jwt,
)
from app.utils import (
    calculate_ayat_assignment,
    jsonify_dict_with_non_string_keys,
    transform_json,
)
import subprocess

# Import models
from app.models import (
    BlockListedTokens,
    Moallim,
    Daur,
    Student,
    SuratMetaData,
    AyatLengths,
)


# Testing route
@sm_app.route("/")
def home():
    return "Hello"


# Callback function to check if a JWT exists in the database BlockListedTokens
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(BlockListedTokens.id).filter_by(jti=jti).scalar()
    return token is not None


# WebHook - For automatic github pulls
@sm_app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    if payload.get("ref") == "refs/heads/main":
        repo_dir = "/home/ubuntu/backends/sm-app-backend/"
        subprocess.run(["git", "pull"], cwd=repo_dir, check=True)
    return "OK", 200


# Registers the user
# Flow of the function
# 1. Extracts json from the request and validates it.
# 2. Extracts its, name, email  and password from the json payload.
# 3. Instantiates a moallim object with its, name and email.
# 4. Sets the password to the user using the set_password method of the User model.
# 5. Adds the user object to the database session and commits it.
# 6. Returns success message upon successful registration.
# 7. If any error, returns 500 - internal server error.
@sm_app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        if data is None:
            return jsonify(error="Invalid JSON"), 400

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        user = Moallim(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Successfully registered. Please login"})

    except Exception as e:
        # print(f"Error during registration: {e}")  # log

        return jsonify({"error": f"{e}"}), 500


# for creating a new daur entry
@sm_app.route("/createdaur", methods=["POST"])
@jwt_required()
def create_daur():
    data = request.json
    # print("code came here")
    # after implementing auth, this has to be changed to fetch the moallim who is logged in
    moallim_email = get_jwt_identity()
    print("moallim_email: ", moallim_email)
    moallim = Moallim.query.filter_by(email=moallim_email).first()
    if isinstance(data, dict):
        daur_name = data.get("daurName")
        new_daur = Daur(name=daur_name, moallim_id=moallim.id)
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
    print("data: ", data)
    print("Students: ", students)
    daur_id = data[0]["daurId"]

    # fetch already added students
    current_students = Student.query.filter_by(daur_id=daur_id).all()
    print("current_students: ", current_students)
    # check which students came from server after edit
    current_ids = {student.id for student in current_students}
    print("current_ids: ", current_ids)
    # check which students are new
    new_ids = {student["id"] for student in students}
    print("New Ids: ", new_ids)
    # check which students got deleted
    ids_to_delete = current_ids - new_ids
    print("Ids to delete: ", ids_to_delete)

    # delete the students from db
    Student.query.filter_by(daur_id=daur_id).filter(
        Student.id.in_(ids_to_delete)
    ).delete(synchronize_session=False)
    print("I completed this ids to delete query")
    students_to_delete = (
        db.session.execute(
            db.select(Student)
            .filter_by(daur_id=daur_id)
            .filter(Student.id.in_(ids_to_delete))
        )
        .scalars()
        .all()
    )
    print("Students to delete: ", students_to_delete)
    for student in students_to_delete:
        db.session.delete(student)

    for student_data in students:
        student = Student.query.filter_by(
            id=student_data["id"], daur_id=daur_id
        ).first()

        if student:
            student.name = student_data["name"]
            student.grade = student_data["grade"]
        else:
            new_student = Student(
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
    moallim_email = get_jwt_identity()
    moallim = Moallim.query.filter_by(email=moallim_email).first()
    print("fetch daurs code")
    if moallim:
        daurs = moallim.daurs
        daurs_list = [daur.to_dict() for daur in daurs]
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
        print("failed auth check")
        return jsonify({"message": str(e)}), 401


# Authentication/Login route
@sm_app.route("/login", methods=["POST"])
def login():
    username = request.json.get("email")
    password = request.json.get("password")

    moallim = Moallim.query.filter_by(email=username).first()

    if moallim and moallim.check_password(password):
        access_token = create_access_token(identity=moallim.email)
        # print("login complete")
        return jsonify({"access_token": access_token})
    else:
        print("failed login")
        return jsonify({"message": "failed login"}), 401


@sm_app.route("/logout1", methods=["POST"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    db.session.add(BlockListedTokens(jti=jti))
    db.session.commit()
    return jsonify(msg="JWT revoked"), 200


@sm_app.route("/getsuratayat", methods=["GET"])
@jwt_required()
def get_surat_ayat():
    surat_ayat_data = db.session.execute(
        db.select(
            SuratMetaData.surat_num, SuratMetaData.surat_name, SuratMetaData.ayat_count
        )
    ).all()

    quran_metadata = [
        {"surat_num": surat_num, "surat": surat, "ayat": ayat}
        for surat_num, surat, ayat in surat_ayat_data
    ]

    # print(quran_metadata)
    return jsonify(quran_metadata)


# Daur assignment logic -------------------------------------------------------------------------------------------------------


@sm_app.route("/calculatedaur", methods=["POST"])
@jwt_required()
def calculate_daur():
    # pass
    try:
        payload = request.json
        moallim_email = get_jwt_identity()
        daur_id = payload.get("daur_id")
        # print("Moallim: ", moallim_email)
        # print(type(moallim_email))
        # print("calculate started")
        result = calculate_ayat_assignment(payload)
        # print("calculate ended")
        json_to_send_to_client = transform_json(result, moallim_email, daur_id)
        print(f"{moallim_email}  calculated a daur")
        return json_to_send_to_client, 200
        # return "Success", 200
    except Exception as e:
        print("Error:", str(e))
        # traceback.print_exc()  # Logs full stack trace
        return "error", 500


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
