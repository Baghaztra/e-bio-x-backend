from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.course import Course
from src.models.enrollment import Enrollment
from src.config.database import db

@jwt_required()
def create_course():
    data = request.get_json()
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Course's name required"}), 400
    
    teacher_id = get_jwt_identity()
    if not teacher_id:
        return jsonify({"error": "Teacher not authenticated"}), 401
    
    new_course = Course(
        name=name,
        teacher_id=teacher_id
    )
    db.session.add(new_course)
    db.session.commit()

    return jsonify({
        "message": "Course created successfully",
        "data": {
            "id": new_course.id,
            "name": new_course.name,
            "created_at": new_course.created_at.isoformat()
        }
    }), 201

@jwt_required()
def get_courses():
    courses = Course.query.all()

    result = []
    for course in courses:
        result.append({
            "id": course.id,
            "name": course.name,
            "teacher": course.teacher.name,
            "created_at": course.created_at.isoformat(),
            "code": f"KLS{course.id:03d}", 
            "students": len(course.enrollments)
        })

    return jsonify(result), 200

@jwt_required()
def get_teacher_courses():
    teacher_id = get_jwt_identity()
    courses = Course.query.filter_by(teacher_id=teacher_id).all()

    result = []
    for course in courses:
        result.append({
            "id": course.id,
            "name": course.name,
            "created_at": course.created_at.isoformat(),
            "code": f"KLS{course.id:03d}",
            "students": len(course.enrollments)
        })

    return jsonify(result), 200

@jwt_required()
def get_student_courses():
    student_id = get_jwt_identity()

    enrollments = Enrollment.query.filter_by(student_id=student_id).all()

    result = []
    for enrollment in enrollments:
        course = enrollment.course
        result.append({
            "id": course.id,
            "name": course.name,
            "teacher": course.teacher.name,
            "created_at": course.created_at.isoformat(),
            "code": f"KLS{course.id:03d}",
            "students": len(course.enrollments)
        })

    return jsonify(result), 200

@jwt_required()
def enroll(course_id):
    if course_id.startswith("KLS") and course_id[3:].isdigit():
        course_id = int(course_id[3:])
    else:
        return jsonify({"error": "Invalid course code format"}), 400
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    student_id = get_jwt_identity()
    if not student_id:
        return jsonify({"error": "Student not authenticated"}), 401
    
    enroll = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if enroll:
        return jsonify({"error": f"You already enrolled in {course.name}"}), 400
    
    enroll = Enrollment(
        student_id=student_id,
        course_id=course_id
    )
    db.session.add(enroll)
    db.session.commit()

    return jsonify({
        "message": f"Enroll successfully to {course.name}",
    }), 200

@jwt_required()
def out(course_id):
    if course_id.startswith("KLS") and course_id[3:].isdigit():
        course_id = int(course_id[3:])

    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    student_id = get_jwt_identity()
    if not student_id:
        return jsonify({"error": "Student not authenticated"}), 401
    
    enroll = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if not enroll:
        return jsonify({"error": f"You are not enrolled in {course.name}"}), 400
    
    db.session.delete(enroll)
    db.session.commit()

    return jsonify({
        "message": f"Successfully out from {course.name}",
    }), 200

@jwt_required()
def kick(course_id, student_id):
    if course_id.startswith("KLS") and course_id[3:].isdigit():
        course_id = int(course_id[3:])
    course = Course.query.get(course_id)
    
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    if not student_id:
        return jsonify({"error": "Student not authenticated"}), 401
    
    enroll = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if not enroll:
        return jsonify({"error": f"You are not enrolled in {course.name}"}), 400
    
    db.session.delete(enroll)
    db.session.commit()

    return jsonify({
        "message": f"Successfully out from {course.name}",
    }), 200

@jwt_required()
def get_course_by_id(course_id):
    course = Course.query.get(course_id)
    if not course:
        jsonify({"error": "Course not found"}), 404

    students = []
    for enrollment in course.enrollments:
        students.append({
            "id": enrollment.student.id,
            "name": enrollment.student.name,
            "email": enrollment.student.email,
            "quizes": [{
                "title":submission.quiz.title,
                "score":submission.score,
                "cluster":submission.cluster,
                    }for submission in enrollment.student.quiz_results if submission.quiz.course_id == course.id]
        })
        
    return jsonify({
        "name": course.name,
        "created_at": course.created_at.isoformat(),
        "code": f"KLS{course.id:03d}",
        "teacher": course.teacher.name,
        "students_count": len(course.enrollments),
        "students": students
    }), 200

@jwt_required()
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        jsonify({"error": "Course not found"}), 404

    try:
        for enrollment in course.enrollments:
            db.session.delete(enrollment)
        
        db.session.delete(course)
    except:
        db.session.rollback()
        return jsonify({
            "message":f"Failed to delete {course.name}" 
        }), 
        
    db.session.commit()
        
    return jsonify({
        "message":"Course deleted successfully" 
    }), 200

