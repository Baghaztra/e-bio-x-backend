from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text
from src.models import Submission, Answer, Question
from src.config.database import db

def kmeans(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    if not submissions:
        return {'message': 'Data tidak ditemukan'}, 404

    # Ambil score dan work time jika data berisi
    data = []
    for s in submissions:
        if s.score is not None:
            total_seconds = s.work_time.hour * 3600 + s.work_time.minute * 60 + s.work_time.second
            data.append([s.score, total_seconds])

    if len(data) < 3:
        return {'message': 'Data yang tersedia terlalu sedikit.'}, 400
    
    # Scaling
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    weighted_data = []
    for d in data_scaled:
        weighted_data.append([
            d[0] * 0.7,
            d[1] * 0.3  
        ])

    # Clustering
    kmeans = KMeans(n_clusters=3, random_state=0)
    clusters = kmeans.fit_predict(weighted_data)

    data_scaled = scaler.fit_transform(data)

    # Update cluster ke database dan hasil
    hasil = []
    idx = 0
    for s in submissions:
        if s.score is not None:
            s.cluster = int(clusters[idx])
            hasil.append({
                'id': s.id,
                'nama': s.student.name,
                'score': s.score,
                'work_time': s.work_time.strftime('%H:%M:%S'),
                'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                'cluster': int(clusters[idx])
            })
            idx += 1
        else:
            s.cluster = None

    db.session.commit()

    return hasil


def decision_tree(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    if not submissions:
        return {'message': 'Data tidak ditemukan'}, 404

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        return {'message': 'Soal tidak ditemukan'}, 404

    question_ids = [q.id for q in questions]

    data = []
    labels = []

    for s in submissions:
        if s.score is not None and s.cluster is not None:
            total_seconds = s.work_time.hour * 3600 + s.work_time.minute * 60 + s.work_time.second

            answers = Answer.query.filter(
                Answer.submission_id == s.id,
                Answer.question_id.in_(question_ids)
            ).order_by(Answer.question_id).all()

            if len(answers) != len(question_ids):
                continue

            answer_values = [a.option_id for a in answers]

            # Gabungkan ke array data
            data.append([s.score, total_seconds] + answer_values)
            labels.append(s.cluster)

    if len(data) < 3:
        return {'message': 'Data yang tersedia terlalu sedikit.'}, 400

    # Training model
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(data, labels)

    # Bikin feature_names
    feature_names = ["score", "work_time_seconds"] + [f"answer_q{qid}" for qid in question_ids]

    rules = export_text(clf, feature_names=feature_names)

    return rules
