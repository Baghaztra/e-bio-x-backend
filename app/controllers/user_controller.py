from flask import jsonify, request
from app.models.user import User
from app.config.database import db

def get_all_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email
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
            'message': 'User berhasil dibuat',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400 