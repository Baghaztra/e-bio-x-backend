from flask import jsonify, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from google.auth.transport import requests
from google.oauth2 import id_token
from src.config.database import db
from src.models.user import User
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

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            name=name,
            email=email, 
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
    }), 200

@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'role': user.role,
        'email': user.email,
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
