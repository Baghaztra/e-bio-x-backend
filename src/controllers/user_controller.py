# Bagian profil picture belum digunakan karean memperberat sistem

from flask import jsonify, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport import requests
from google.oauth2 import id_token
from src.config.database import db
from src.models.user import User
# from src.config.drive import drive_service
import os
# import re

def google_login():
    data = request.json
    token = data.get("token")
    
    if not token:
        return jsonify({"error": "Token is required"}), 400

    user_data = id_token.verify_oauth2_token(
        token, 
        requests.Request(), 
        os.getenv("GOOGLE_CLIENT_ID"), 
        clock_skew_in_seconds=10
    )
    
    if not user_data:
        return jsonify({"error": "Invalid token"}), 400

    email = user_data.get("email")
    name = user_data.get("name")
    # picture = user_data.get("picture")

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            name=name,
            email=email, 
            # profile_pic=picture
        )
        db.session.add(user)
        db.session.commit()
        user.role = "student"

    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        "access_token": access_token, 
        "name": user.name, 
        "email": user.email, 
        "role": user.role, 
        "has_password":  bool(user.password_hash),
        # "profile_pic": user.profile_pic
    })

def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.password_hash == None:
        return jsonify({'message': 'Please login with Google'}), 418
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'access_token': access_token,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        "has_password": bool(user.password_hash),
        # 'profile_pic': user.profile_pic
    }), 200

@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'role': user.role,
        'email': user.email,
        # 'profile_picture': user.profile_pic,
    } for user in users])

@jwt_required()
def create_user():
    data = request.get_json()
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400
    
    new_user = User(
        name=data['name'],
        email=data['email'],
        role=data['role']
    )
    
    new_user.set_password(data['password'])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@jwt_required()
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # if user.profile_pic:
    #     file_id = None
    #     if user.profile_pic:
    #         match = re.search(r'/d/([a-zA-Z0-9_-]+)', user.profile_pic)
    #         if match:
    #             file_id = match.group(1)
        
    #     if file_id:
    #         try:
    #             drive_service.files().delete(fileId=file_id).execute()
    #         except Exception as e:
    #             print("Failed to delete from Google Drive:", e)
        
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "User deleted successfully"}), 200

@jwt_required()
def update_user(user_id):
    data = request.get_json()
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if "name" in data:
        user.name = data["name"]
    if "password" in data:
        user.set_password(data["password"])
    # if 'profile_pic' in request.files:
    #     file = request.files.get('profile_pic')
    #     if not file:
    #         return jsonify({'error': 'File required'}), 400
        
    #     web_view_link = upload_profile_pic_to_drive(user, file, drive_service)
    #     if web_view_link:
    #         user.profile_pic = web_view_link
    if "role" in data:
        user.role = data["role"]

    db.session.commit()

    return jsonify({"message": "User updated successfully"}), 200

@jwt_required()
def update_user_me():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)

    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        # if request.content_type.startswith('multipart/form-data'):
        #     if 'profile_pic' in request.files:
        #         file = request.files.get('profile_pic')
        #         if not file:
        #             return jsonify({'error': 'File required'}), 400
                # web_view_link = upload_profile_pic_to_drive(user, file, drive_service)
                # if web_view_link:
                #     user.profile_pic = web_view_link
        # else:
        data = request.get_json()
        if "name" in data:
            user.name = data["name"]
        elif "current_password" in data and "new_password" in data:
            if not user.check_password(data["current_password"]):
                return jsonify({"message": "Incorrect current password"}), 400
            user.set_password(data["new_password"])
        elif "new_password" in data:
            user.set_password(data["new_password"])
        else:
            return jsonify({"message": "Nothing to update"}), 400
            
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        print("Failed to update user", e)
        db.session.rollback()
        return jsonify({"message": "Failed to update user"}), 500

@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": "You are logged in", "user": current_user})

# Not used yet
# def upload_profile_pic_to_drive(user, file, drive_service):
#     try:
#         file_id = None
#         if user.profile_pic:
#             match = re.search(r'/d/([a-zA-Z0-9_-]+)', user.profile_pic)
#             if match:
#                 file_id = match.group(1)
        
#         if file_id:
#             try:
#                 drive_service.files().delete(fileId=file_id).execute()
#             except Exception as e:
#                 print("Failed to delete from Google Drive:", e)
        
#         # Cek atau buat folder user di Drive
#         folder_name = f"user-{user.id}"

#         # Cari folder user di Drive
#         response = drive_service.files().list(
#             q=f"'{os.getenv('GOOGLE_DRIVE_FOLDER_PROFILE_ID')}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
#             spaces='drive',
#             fields='files(id, name)'
#         ).execute()

#         folders = response.get('files', [])
#         if folders:
#             folder_id = folders[0]['id']
#         else:
#             # Kalau belum ada, buat folder baru
#             folder_metadata = {
#                 'name': folder_name,
#                 'mimeType': 'application/vnd.google-apps.folder',
#                 'parents': [os.getenv("GOOGLE_DRIVE_FOLDER_PROFILE_ID")]
#             }
#             folder = drive_service.files().create(
#                 body=folder_metadata,
#                 fields='id'
#             ).execute()
#             folder_id = folder.get('id')

#         # Upload file ke folder user
#         file_metadata = {
#             'name': 'profile.jpg',
#             'parents': [folder_id]
#         }

#         media = MediaIoBaseUpload(file.stream, mimetype=file.mimetype, resumable=False)

#         uploaded = drive_service.files().create(
#             body=file_metadata,
#             media_body=media,
#             fields='id, webViewLink'
#         ).execute()

#         return uploaded['webViewLink']

#     except Exception as e:
#         print("Failed to upload to Google Drive:", e)
#         return None
