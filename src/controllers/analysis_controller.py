from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.submission import Submission
from src.models.quiz import Quiz
from src.services.analysis_service import analyze_quiz_data, analyze_with_decision_tree

# @jwt_required()
def analyze_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404

    result = analyze_quiz_data(quiz_id)
    if isinstance(result, tuple): 
        return jsonify(result[0]), result[1]

    rules = analyze_with_decision_tree(quiz_id)
    if isinstance(rules, dict):
        return jsonify(rules), 400

    # Nilai tertinggi & terendah
    highest = max(result, key=lambda x: x['score'])
    lowest = min(result, key=lambda x: x['score'])

    # Work time tercepat & terlambat
    fastest = min(result, key=lambda x: x['work_time'])
    slowest = max(result, key=lambda x: x['work_time'])

    # Rata-rata nilai
    avg_score = sum(item['score'] for item in result) / len(result)

    return jsonify({
        'quiz_title': quiz.title,
        'total_questions': len(quiz.questions),
        'total_students': len(result),
        'clusters': result,
        'decision_tree_rules': rules,
        'highest_score': {
            'nama': highest['nama'],
            'score': highest['score'],
            'cluster': highest['cluster'],
            'work_time': highest['work_time']
        },
        'lowest_score': {
            'nama': lowest['nama'],
            'score': lowest['score'],
            'cluster': lowest['cluster'],
            'work_time': lowest['work_time']
        },
        'fastest_work_time': {
            'nama': fastest['nama'],
            'score': fastest['score'],
            'cluster': fastest['cluster'],
            'work_time': fastest['work_time']
        },
        'slowest_work_time': {
            'nama': slowest['nama'],
            'score': slowest['score'],
            'cluster': slowest['cluster'],
            'work_time': slowest['work_time']
        },
        'average_score': avg_score
    })


# @jwt_required()
def get_analyze(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404

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

    # Nilai tertinggi & terendah
    highest = max(result, key=lambda x: x['score'])
    lowest = min(result, key=lambda x: x['score'])

    # Work time tercepat & terlambat
    fastest = min(result, key=lambda x: x['work_time'])
    slowest = max(result, key=lambda x: x['work_time'])

    # Rata-rata nilai
    avg_score = sum(item['score'] for item in result) / len(result)

    return jsonify({
        'quiz_title': quiz.title,
        'total_questions': len(quiz.questions),
        'total_students': len(result),
        'clusters': result,
        'decision_tree_rules': rules,
        'highest_score': {
            'nama': highest['nama'],
            'score': highest['score'],
            'cluster': highest['cluster'],
            'work_time': highest['work_time']
        },
        'lowest_score': {
            'nama': lowest['nama'],
            'score': lowest['score'],
            'cluster': lowest['cluster'],
            'work_time': lowest['work_time']
        },
        'fastest_work_time': {
            'nama': fastest['nama'],
            'score': fastest['score'],
            'cluster': fastest['cluster'],
            'work_time': fastest['work_time']
        },
        'slowest_work_time': {
            'nama': slowest['nama'],
            'score': slowest['score'],
            'cluster': slowest['cluster'],
            'work_time': slowest['work_time']
        },
        'average_score': avg_score
    })
