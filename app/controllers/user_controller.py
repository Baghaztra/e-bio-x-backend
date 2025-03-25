from flask import jsonify, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from google.auth.transport import requests
from google.oauth2 import id_token
from app.config.database import db
from app.models.user import User
import os

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
    picture = user_data.get("picture")

    # Cek apakah user sudah ada di database
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username=name,
            email=email, 
            profile_pic=picture)
        db.session.add(user)
        db.session.commit()
        user.role = "student"

    # Buat JWT token untuk user
    access_token = create_access_token(identity=email)
    
    return jsonify({
        "access_token": access_token, 
        "username": user.username, 
        "email": user.email, 
        "role": user.role, 
        "profile_pic": user.profile_pic
    })

# Debug endpoint dengan jwt
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": "You are logged in", "user": current_user})

def get_all_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'email': user.email,
        'profile_picture': user.profile_pic,
    } for user in users])

def create_user():
    data = request.get_json()
    
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400 