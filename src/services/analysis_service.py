from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text
from src.models import Submission
from src.config.database import db

def analyze_quiz_data(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    if not submissions:
        return {'message': 'Data tidak ditemukan'}, 404

    # Ambil score dan work time jika data berisi
    data = []
    valid_submissions = []
    for s in submissions:
        if s.score is not None:
            total_seconds = s.work_time.hour * 3600 + s.work_time.minute * 60 + s.work_time.second
            weighted_score = s.score * 9
            weighted_time = total_seconds * 1
            data.append([weighted_score, weighted_time])
            valid_submissions.append(s)

    if len(data) < 3:
        return {'message': 'Data yang tersedia terlalu sedikit.'}, 400
    
    # Training model
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    # Clustering
    kmeans = KMeans(n_clusters=3, random_state=0)
    clusters = kmeans.fit_predict(data_scaled)

    # Update cluster ke database dan hasil
    hasil = []
    for s, c in zip(valid_submissions, clusters):
        s.cluster = int(c)
        hasil.append({
            'id': s.id,
            'nama': s.student.name,
            'score': s.score,
            'work_time': s.work_time.strftime('%H:%M:%S'),
            'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'cluster': int(c)
        })

    # Sisanya tetap cluster None
    for s in submissions:
        if s.score is None:
            s.cluster = None

    db.session.commit()

    return hasil


def analyze_with_decision_tree(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    if not submissions:
        return {'message': 'Data tidak ditemukan'}, 404

    # Ambil data nilai & work_time
    data = []
    labels = []
    for s in submissions:
        if s.score is not None and s.cluster is not None:
            total_seconds = s.work_time.hour * 3600 + s.work_time.minute * 60 + s.work_time.second
            data.append([s.score, total_seconds])
            labels.append(s.cluster)

    if len(data) < 3:
        return {'message': 'Data yang tersedia terlalu sedikit.'}, 400

    # Training model
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(data, labels)

    rules = export_text(clf, feature_names=["score", "work_time_seconds"])

    return rules
