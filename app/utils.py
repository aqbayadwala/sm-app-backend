from sqlalchemy import func
from app.models import AyatLengths, SuratMetaData, Student, Moallim, Daur
from app import db
import json


# get ayat length sum if surat are same
def get_same_surat_ayat_length_sum(surat_num, from_ayat, to_ayat):
    total_length = (
        db.session.query(func.sum(AyatLengths.ayat_length))
        .filter(
            AyatLengths.surat_num == surat_num,  # Filter by specific surah
            AyatLengths.ayat_number >= from_ayat,  # Filter by `from_ayat`
            AyatLengths.ayat_number <= to_ayat,  # Filter by `to_ayat`
        )
        .scalar()  # Get the scalar result of the sum
    )
    return total_length


def get_total_lines(from_surat_num, from_ayat, to_surat_num, to_ayat):
    """
    Calculate the total lines of ayaat between two points in the Quran,
    spanning across multiple surahs if necessary.

    Parameters:
        from_surat_num (int): The surah number where the range starts.
        from_ayat (int): The ayah number where the range starts.
        to_surat_num (int): The surah number where the range ends.
        to_ayat (int): The ayah number where the range ends.

    Returns:
        int: The total number of ayah lines between the specified range.
    """
    total_length = 0

    # Case 1: If the range is within the same surah
    if from_surat_num == to_surat_num:
        # Sum all ayat lengths within the same surah from `from_ayat` to `to_ayat`
        total_length = (
            db.session.query(func.sum(AyatLengths.ayat_length))
            .filter(
                AyatLengths.surat_num == from_surat_num,
                AyatLengths.ayat_number >= from_ayat,
                AyatLengths.ayat_number <= to_ayat,
            )
            .scalar()  # Fetch the scalar value of the sum
        )

    else:
        # Case 2: If the range spans across multiple surahs

        # Step 1: Calculate the length of ayat from `from_ayat` to the end of the starting surah
        total_length += (
            db.session.query(func.sum(AyatLengths.ayat_length))
            .filter(
                AyatLengths.surat_num == from_surat_num,
                AyatLengths.ayat_number >= from_ayat,
            )
            .scalar()
            or 0  # Handle cases where the query returns None
        )

        # Step 2: Calculate the length of ayat in all intermediate surahs
        # Fetch distinct surah numbers between `from_surat_num` and `to_surat_num`
        intermediate_surahs = (
            db.session.query(AyatLengths.surat_num)
            .distinct()
            .filter(
                AyatLengths.surat_num
                > from_surat_num,  # Surahs after the starting surah
                AyatLengths.surat_num < to_surat_num,  # Surahs before the ending surah
            )
            .all()
        )
        for surah in intermediate_surahs:
            # Sum up the length of all ayat in each intermediate surah
            total_length += (
                db.session.query(func.sum(AyatLengths.ayat_length))
                .filter(AyatLengths.surat_num == surah[0])
                .scalar()
                or 0
            )

        # Step 3: Calculate the length of ayat from the beginning of the ending surah to `to_ayat`
        total_length += (
            db.session.query(func.sum(AyatLengths.ayat_length))
            .filter(
                AyatLengths.surat_num == to_surat_num,
                AyatLengths.ayat_number <= to_ayat,
            )
            .scalar()
            or 0
        )

    # Return the total lines of ayaat within the specified range
    return total_length


def get_surat_nums(from_surat_name, to_surat_name):
    """
    Retrieve a list of surah numbers between two given surah names (inclusive).

    Parameters:
        from_surat_name (str): The name of the starting surah.
        to_surat_name (str): The name of the ending surah.

    Returns:
        list: A list of surah numbers in the specified range.

    Raises:
        ValueError: If either surah name is not found in the database.
    """
    # Fetch the starting and ending surah records
    from_surah = SuratMetaData.query.filter_by(surat_name=from_surat_name).first()
    to_surah = SuratMetaData.query.filter_by(surat_name=to_surat_name).first()

    if not from_surah:
        raise ValueError(f"Surat '{from_surat_name}' not found!")
    if not to_surah:
        raise ValueError(f"Surat '{to_surat_name}' not found!, error occured here")

    # Ensure the range is valid (from_surat_num <= to_surat_num)
    if from_surah.surat_num > to_surah.surat_num:
        raise ValueError(
            "The starting surah comes after the ending surah in the Quran!"
        )

    # Query all surah numbers in the range (inclusive)
    surat_nums = (
        SuratMetaData.query.filter(
            SuratMetaData.surat_num >= from_surah.surat_num,
            SuratMetaData.surat_num <= to_surah.surat_num,
        )
        .order_by(SuratMetaData.surat_num)  # Ensure the order is ascending
        .with_entities(SuratMetaData.surat_num)  # Retrieve only surah numbers
        .all()
    )

    # Extract and return the list of surah numbers
    # surat_nums is like [(1,), (2,), (3,)]
    # surat_num[0] extracts the value and makes this like [1,2,3,4]
    return [surat_num[0] for surat_num in surat_nums]


def get_surat_num(surat_name):
    surah = SuratMetaData.query.filter_by(surat_name=surat_name).first()
    if not surah:
        raise ValueError(f"Surat '{surat_name}' not found!")
    return surah.surat_num


def get_student_grades(student_ids):
    students = (
        db.session.query(Student.id, Student.grade)
        .filter(Student.id.in_(student_ids))
        .all()
    )
    student_grades = {
        student.id: student.grade for student in students
    }  # this works because student in sqlalchemy object and not raw tuples
    return student_grades


def calculate_ayat_assignment(payload):
    student_ids = payload.get("studentIds")

    from_surat_name = payload.get("tilawat_from").get("fromSurat")
    from_ayat = int(payload.get("tilawat_from").get("fromAyat"))
    to_surat_name = payload.get("tilawat_to").get("toSurat")
    to_ayat = int(payload.get("tilawat_to").get("toAyat"))

    from_surat_num = get_surat_num(from_surat_name)
    to_surat_num = get_surat_num(to_surat_name)

    surat_nums = get_surat_nums(from_surat_name, to_surat_name)
    total_lines = get_total_lines(from_surat_num, from_ayat, to_surat_num, to_ayat)

    grades = get_student_grades(student_ids)

    is_students_workload = payload.get("is_students_workload")
    # print(is_students_workload)

    workload = {student_id: 0 for student_id in grades.keys()}

    has_a_grades = any(grade == "A" for grade in grades.values())
    has_b_grades = any(grade == "B" for grade in grades.values())
    has_c_grades = any(grade == "C" for grade in grades.values())
    has_d_grades = any(grade == "D" for grade in grades.values())

    sadr_percentage = 0
    grade_a_percentage = 0
    grade_b_percentage = 0
    grade_c_percentage = 0
    grade_d_percentage = 0

    if is_students_workload:
        if has_a_grades:
            sadr_percentage = 0.2
            grade_a_percentage = 0.6
            grade_b_percentage = 0.15
            grade_c_percentage = 0.05
        elif has_b_grades:
            sadr_percentage = 0.7
            grade_b_percentage = 0.20
            grade_c_percentage = 0.1
        elif has_c_grades:
            sadr_percentage = 0.9
            grade_c_percentage = 0.1
        else:
            sadr_percentage = 0.95
            grade_d_percentage = 0.05

        sadr_lines = int(total_lines * sadr_percentage)
        grade_a_lines = int(total_lines * grade_a_percentage)
        grade_b_lines = int(total_lines * grade_b_percentage)
        grade_c_lines = int(total_lines * grade_c_percentage)
        grade_d_lines = total_lines - (
            sadr_lines + grade_a_lines + grade_b_lines + grade_c_lines
        )

        grade_percentages = {
            "Sadr": sadr_percentage,
            "A": grade_a_percentage,
            "B": grade_b_percentage,
            "C": grade_c_percentage,
            "D": grade_d_percentage,
        }

        grade_lines = {
            "Sadr": sadr_lines,
            "A": grade_a_lines,
            "B": grade_b_lines,
            "C": grade_c_lines,
            "D": grade_d_lines,
        }
        # print("Total lines: ", total_lines)
        # print("Grades: ", grades)
        # print("grade_percentages: ", grade_percentages)
        # print("grade_lines: ", grade_lines)
        workload = assign_lines(total_lines, grades, grade_lines)
        # print("workload printed inside calculate_ayat_assignment: ", workload)
        ayat_metadata = generate_ayat_metadata(
            from_surat_num, from_ayat, to_surat_num, to_ayat
        )
        # print(ayat_metadata)
        ayat_ranges = assign_ayat_ranges(workload, ayat_metadata)
        print("Ayat ranges: ", ayat_ranges)
        return ayat_ranges

    else:
        # logic
        # if has_a_grades:
        sadr_percentage = 0.5
        grade_a_percentage = 0.2
        grade_b_percentage = 0.15
        grade_c_percentage = 0.10

        sadr_lines = int(total_lines * sadr_percentage)
        grade_a_lines = int(total_lines * grade_a_percentage)
        grade_b_lines = int(total_lines * grade_b_percentage)
        grade_c_lines = int(total_lines * grade_c_percentage)
        grade_d_lines = total_lines - (
            sadr_lines + grade_a_lines + grade_b_lines + grade_c_lines
        )

        grade_percentages = {
            "Sadr": sadr_percentage,
            "A": grade_a_percentage,
            "B": grade_b_percentage,
            "C": grade_c_percentage,
            "D": grade_d_percentage,
        }

        grade_lines = {
            "Sadr": sadr_lines,
            "A": grade_a_lines,
            "B": grade_b_lines,
            "C": grade_c_lines,
            "D": grade_d_lines,
        }
        # print("Total lines: ", total_lines)
        # print("Grades: ", grades)
        # print("grade_percentages: ", grade_percentages)
        # print("grade_lines: ", grade_lines)
        workload = assign_lines(total_lines, grades, grade_lines)
        # print("workload printed inside calculate_ayat_assignment: ", workload)
        ayat_metadata = generate_ayat_metadata(
            from_surat_num, from_ayat, to_surat_num, to_ayat
        )
        # print(ayat_metadata)
        ayat_ranges = assign_ayat_ranges(workload, ayat_metadata)
        # print("Ayat ranges: ", ayat_ranges)

        return ayat_ranges


def assign_lines(total_lines, student_grades, grade_lines):
    # Initialize workload dictionary
    workload = {student: 0 for student in student_grades.keys()}
    workload["Sadr"] = 0  # Initialize Sadr's workload

    for grade, grade_line_allocation in grade_lines.items():
        # Filter students belonging to the current grade
        students = [student for student, g in student_grades.items() if g == grade]

        # If there are no students for this grade, assign the lines to Sadr
        if not students:
            workload["Sadr"] += grade_line_allocation
            continue

        # Special condition for Grade D: each student gets exactly 1 line
        if grade == "D":
            for student in students:
                workload[student] += 1
                grade_line_allocation -= 1

            # Assign any leftover lines for Grade D to Sadr
            workload["Sadr"] += grade_line_allocation
            continue

        # Distribute lines equally among students for other grades
        lines_per_student = grade_line_allocation // len(students)
        remaining_lines = grade_line_allocation % len(students)

        for student in students:
            workload[student] += lines_per_student

        # Distribute any leftover lines in a round-robin manner
        for i in range(remaining_lines):
            student_id = students[i % len(students)]
            workload[student_id] += 1

    # Assign any remaining lines (if total lines exceed allocated grade lines) to Sadr
    allocated_lines = sum(workload.values())
    if allocated_lines < total_lines:
        workload["Sadr"] += total_lines - allocated_lines

    return workload


def jsonify_dict_with_non_string_keys(data):
    """
    Convert a dictionary to a JSON string, ensuring all keys are strings.

    Args:
        data (dict): The input dictionary.

    Returns:
        str: The JSON string representation of the dictionary.
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary.")

    # Convert all keys to strings
    json_ready_data = {str(key): value for key, value in data.items()}

    # Convert the dictionary to a JSON string
    return json.dumps(json_ready_data)


def assign_ayat_ranges(workload, ayat_metadata):
    """
    Assign ayat ranges to students and Sadr based on workloads.

    Args:
        workload (dict): Dictionary with keys as student IDs (or "Sadr") and values as the number of lines assigned.
        ayat_metadata (list): List of tuples containing (surah_num, ayat_number, ayat_length).

    Returns:
        dict: A dictionary with keys as student IDs (or "Sadr") and values as lists of ayat ranges assigned to them.
    """
    assignments = {student: [] for student in workload.keys()}

    # Track the current position in ayat_metadata
    current_index = 0

    # Ensure Sadr is assigned first
    students = ["Sadr"] + [student for student in workload if student != "Sadr"]

    for student in students:
        lines = workload[student]
        total_lines_assigned = 0
        start_tuple = None

        while current_index < len(ayat_metadata) and total_lines_assigned < lines:
            surat_num, ayat_number, ayat_length = ayat_metadata[current_index]

            # Start the range if not already started
            if start_tuple is None:
                start_tuple = (surat_num, ayat_number)

            # Check if adding this ayat would exceed the assigned workload
            if total_lines_assigned + ayat_length > lines:
                break

            # Add ayat length to the total lines assigned
            total_lines_assigned += ayat_length
            current_index += 1

        # Assign the range to the student
        if start_tuple is not None and total_lines_assigned > 0:
            # Ensure end_tuple points to the last assigned ayat for this student
            end_tuple = (
                ayat_metadata[current_index - 1][0],
                ayat_metadata[current_index - 1][1],
            )
            assignments[student].append((start_tuple, end_tuple))

    # Handle remaining ayat (if any)
    while current_index < len(ayat_metadata):
        surat_num, ayat_number, ayat_length = ayat_metadata[current_index]

        # Check if the current ayat is 1 line
        if ayat_length == 1:
            for student in workload:
                if workload[student] == 1:  # D-grade student condition
                    assignments[student].append(
                        ((surat_num, ayat_number), (surat_num, ayat_number))
                    )
                    current_index += 1
                    break
        else:
            # Assign all remaining ayat to Sadr
            start_tuple = (surat_num, ayat_number)
            end_tuple = start_tuple

            while current_index < len(ayat_metadata):
                surat_num, ayat_number, _ = ayat_metadata[current_index]
                end_tuple = (surat_num, ayat_number)
                current_index += 1

            assignments["Sadr"].append((start_tuple, end_tuple))
            break

    return assignments


def generate_ayat_metadata(from_surat_num, from_ayat, to_surat_num, to_ayat):
    # Query all records from the AyatLengths table
    ayat_data = db.session.query(
        AyatLengths.surat_num, AyatLengths.ayat_number, AyatLengths.ayat_length
    ).all()

    ayat_metadata = []

    # Loop through the data to generate metadata in the specified range
    for surat_num, ayat_number, ayat_length in ayat_data:
        if (
            surat_num > from_surat_num
            or (surat_num == from_surat_num and ayat_number >= from_ayat)
        ) and (
            surat_num < to_surat_num
            or (surat_num == to_surat_num and ayat_number <= to_ayat)
        ):
            ayat_metadata.append((surat_num, ayat_number, ayat_length))

    return ayat_metadata


# TODO: Now check the is_students_workload and assign accordingly, dont follow 150 lines rule


def transform_json(server_json, moallim_email, daur_id):
    # Fetch the Moallim and their associated students
    moallim = Moallim.query.filter_by(email=moallim_email).first()

    # Fetch all students and Surat metadata in one go to minimize queries
    daur_ids = [daur.id for daur in Daur.query.filter_by(moallim_id=moallim.id).all()]
    students = {
        student.id: student.name
        for student in Student.query.filter_by(daur_id=daur_id).all()
    }
    surats = {surat.surat_num: surat.surat_name for surat in SuratMetaData.query.all()}

    # Result structure to be returned
    result = {}

    for key, assignments in server_json.items():
        # Handle "Sadr" separately or map it to a specific identifier (e.g., "Sadr" -> "Sadr" directly)
        if key == "Sadr":
            student_name = "Sadr"
        else:
            # Convert student ID to student name
            student_name = students.get(int(key), None)
            if not student_name:
                continue  # Skip if the student ID is not found

        result[student_name] = []

        # Process the assignments for the student/Sadr
        for assignment in assignments:
            start = assignment[0]
            end = assignment[1]

            # Map Surat numbers to Surat names
            start_surat = surats.get(start[0], None)
            end_surat = surats.get(end[0], None)

            if start_surat and end_surat:
                result[student_name].append(
                    {
                        "startSuratNum": start[0],
                        "startSuratName": start_surat,
                        "startAyat": str(start[1]),
                        "endSuratNum": end[0],
                        "endSuratName": end_surat,
                        "endAyat": str(end[1]),
                    }
                )

    return result
