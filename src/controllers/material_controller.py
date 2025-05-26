from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from googleapiclient.http import MediaIoBaseUpload
from src.models.material import Material
from src.config.database import db
from src.config.drive import drive_service
from datetime import datetime
import os
import re

@jwt_required()
def upload_material():
    title = request.form.get('title')
    content = request.form.get('content')
    try:
        course_id = int(request.form.get('course_id'))
    except (TypeError, ValueError):
        return jsonify({'error': 'course_id harus berupa angka'}), 400

    file = request.files.get('file')

    if not all([title, course_id, file]):
        return jsonify({'error': 'Title, course_id, and file are required'}), 400

    file_metadata = {
        'name': file.filename,
        'parents': [os.getenv("GOOGLE_DRIVE_FOLDER_ID")]
    }

    media = MediaIoBaseUpload(file.stream, mimetype=file.mimetype, resumable=False)

    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    new_material = Material(
        title=title,
        content=content,
        course_id=course_id,
        file_url=uploaded['webViewLink'],
        uploaded_at=datetime.utcnow()
    )
    db.session.add(new_material)
    db.session.commit()

    return jsonify({
        'message': 'Material uploaded',
        'material': {
            'id': new_material.id,
            'title': new_material.title,
            'file_url': new_material.file_url
        }
    }), 201

@jwt_required()
def get_material_by_id(material_id):
    material = Material.query.get(material_id)
    
    if not material:
        return jsonify({'error': 'Material not found'}), 404
    
    return jsonify({
        'id': material.id,
        'title': material.title,
        'description': material.content,
        'file_url': material.file_url,
        'course_id': material.course_id,
        'uploaded_at': material.uploaded_at,
    }), 200    
    
@jwt_required()
def get_material_by_course(course_id):
    materials = Material.query.filter_by(course_id=course_id).all()

    result = []
    for material in materials:
        result.append({
            'id': material.id,
            'title': material.title,
            'description': material.content,
            'file_url': material.file_url,
            'course_id': material.course_id,
            'uploaded_at': material.uploaded_at,
        })

    return jsonify({
        'message': 'Materials retrieved successfully',
        'data': result,
    }), 200 

@jwt_required()
def get_all_material():
    materials = Material.query.all()

    return jsonify([{
            'id': material.id,
            'title': material.title,
            'description': material.content,
            'file_url': material.file_url,
            'course': material.course.name,
            'uploaded_at': material.uploaded_at,
        } for material in materials
    ]), 200 

@jwt_required()
def delete_material(material_id):
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404

    match = re.search(r'/d/([a-zA-Z0-9_-]+)', material.file_url)
    if match:
        file_id = match.group(1)
    
    db.session.delete(material)
    db.session.commit()
    
    if file_id:
        try:
            drive_service.files().delete(fileId=file_id).execute()
        except Exception as e:
            print("Failed to delete from Google Drive:", e)
            return jsonify({'error': 'Failed to delete from Google Drive'}), 500
    else:
        return jsonify({'error': 'Invalid file URL'}), 400

    return jsonify({'message': 'Material deleted successfully'}), 200
