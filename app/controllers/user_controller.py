from flask import jsonify, request, jsonify, session, abort, redirect
# from google_auth_oauthlib.flow import Flow
# from google.oauth2 import id_token
# import google.auth.transport.requests
from app.models.user import User
from app.config.database import db


# def google_login():
#     authorization_url, state = flow.authorization_url()
#     session["state"] = state
#     return redirect(authorization_url)

# def callback():
#     flow.fetch_token(authorization_response=request.url)

#     if not session["state"] == request.args["state"]:
#         abort(500)

#     credentials = flow.credentials
#     request_session = req.Session()
#     cached_session = cachecontrol.CacheControl(request_session)
#     token_request = google.auth.transport.requests.Request(
#         session=cached_session)

#     id_info = id_token.verify_oauth2_token(
#         id_token=credentials._id_token,
#         request=token_request,
#         audience=GOOGLE_CLIENT_ID
#     )

#     google_id = id_info.get("sub")
#     email = id_info.get("email")
#     name = id_info.get("name")
#     pfp = id_info.get("picture")

#     # Cari user berdasarkan email atau buat user baru jika belum ada
#     user = User.query.filter_by(email=email).first()

#     if not user:
#         # Simpan user baru jika belum ada
#         user = User(username=name, email=email, google_id=google_id, status="Active",
#                     profile_picture=pfp, created_at=datetime.now())
#         db.session.add(user)
#         db.session.commit()

#     access_token = create_access_token(
#         identity={'user_id': user.id, 'username': user.username, 'role': user.role})
#     # return jsonify({"message": "Login berhasil", "token": access_token}), 200
#     return redirect(f"http://localhost:8080/home?token={access_token}")

def logout():
    session.clear()
    return jsonify({"message": "Logout berhasil"}), 200

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