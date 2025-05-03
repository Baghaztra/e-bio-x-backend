from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.submission import Submission
from src.services.analysis_service import analyze_quiz_data, analyze_with_decision_tree

# @jwt_required()
def analyze_quiz(quiz_id):
    result = analyze_quiz_data(quiz_id)
    if isinstance(result, tuple): 
        return jsonify(result[0]), result[1]

    rules = analyze_with_decision_tree(quiz_id)
    if isinstance(rules, dict):
        return jsonify(rules), 400

    return jsonify({
        'clusters': result,
        'decision_tree_rules': rules
    })


# @jwt_required()
def get_analyze(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    if not submissions:
        return jsonify({'message': 'Data tidak ditemukan'}), 404

    rules = analyze_with_decision_tree(quiz_id)
    if isinstance(rules, dict):
        return jsonify(rules), 400

    result = []
    for s in submissions:
        result.append({
            'id': s.id,
            'nama': s.student.name,
            'score': s.score,
            'work_time': s.work_time.strftime('%H:%M:%S') if s.work_time else None,
            'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'cluster': int(s.cluster) if s.cluster is not None else None
        })

    return jsonify({
        'clusters': result,
        'decision_tree_rules': rules
    })