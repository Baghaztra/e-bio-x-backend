from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from src.models import Submission, Answer, Question
from src.config.database import db
import numpy as np

def kmeans(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    if not submissions:
        return {'message': 'Data tidak ditemukan'}, 404

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        return {'message': 'Soal tidak ditemukan'}, 404

    question_ids = [q.id for q in questions]

    data = []
    hasil = []

    for s in submissions:
        if s.score is not None:
            total_seconds = s.work_time.hour * 3600 + s.work_time.minute * 60 + s.work_time.second

            # Ambil jawaban siswa untuk soal-soal di kuis ini
            answers = Answer.query.filter(
                Answer.submission_id == s.id,
                Answer.question_id.in_(question_ids)
            ).order_by(Answer.question_id).all()

            # Kalau jumlah jawaban gak sesuai jumlah soal → skip
            if len(answers) != len(question_ids):
                continue

            # Representasikan opsi jawaban jadi angka (pakai option_id langsung)
            answer_values = [a.option_id for a in answers]

            # Gabungkan score, waktu, dan jawaban ke 1 array
            data.append([s.score, total_seconds] + answer_values)

    if len(data) < 3:
        return {'message': 'Data yang tersedia terlalu sedikit.'}, 400

    # Scaling score dan waktu saja
    scaler = StandardScaler()
    data_np = np.array(data)
    data_scaled = data_np.copy()

    data_scaled[:, 0:2] = scaler.fit_transform(data_np[:, 0:2])

    # Weighting score dan waktu
    data_scaled[:, 0] *= 0.7  # score
    data_scaled[:, 1] *= 0.3  # waktu

    # Clustering
    kmeans = KMeans(n_clusters=3, random_state=0)
    clusters = kmeans.fit_predict(data_scaled)

    # Update cluster ke database
    idx = 0
    for s in submissions:
        if s.score is not None:
            answers = Answer.query.filter(
                Answer.submission_id == s.id,
                Answer.question_id.in_(question_ids)
            ).all()

            if len(answers) != len(question_ids):
                continue

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
