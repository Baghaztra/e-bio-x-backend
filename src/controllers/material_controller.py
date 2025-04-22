from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.models.material import Material
from src.config.database import db
from datetime import datetime
import os
import mimetypes

SERVICE_ACCOUNT_FILE = 'src/config/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

@jwt_required()
def upload_material():
    title = request.form.get('title')
    content = request.form.get('content')
    try:
        course_id = int(request.form.get('course_id'))
    except (TypeError, ValueError):
        return jsonify({'error': 'course_id harus berupa angka'}), 400

    file = request.files.get('file')

    print("Form data:", request.form)
    print("File data:", request.files)

    if not all([title, course_id, file]):
        return jsonify({'error': 'Title, course_id, and file are required'}), 400

    # Simpan file sementara
    filename = file.filename
    filepath = os.path.join('temp', filename)
    os.makedirs('temp', exist_ok=True)
    file.save(filepath)

    # Upload ke Google Drive
    file_metadata = {
        'name': filename,
        'parents': [os.getenv("GOOGLE_DRIVE_FOLDER_ID")]
    }

    try:
        mimetype = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        media = MediaFileUpload(filepath, mimetype=mimetype, resumable=False)
        uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
    finally:
        try:
            os.remove(filepath)
        except Exception as e:
            print("Gagal hapus file:", e)

    # Simpan ke database
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
