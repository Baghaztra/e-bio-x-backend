from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.config.database import db

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

def get_courses():
    courses = Course.query.all()

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
def get_my_courses():
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
def enroll(course_id):
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

