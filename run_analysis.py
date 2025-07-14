import sys
from flask import Flask
from src.config.database import db
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text
from src.models import Submission
from sklearn.metrics import (
    silhouette_score, 
    calinski_harabasz_score, 
    davies_bouldin_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost:3306/e_bio"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def evaluate_kmeans_clustering(data_scaled, weighted_data, clusters):
    """
    Evaluasi komprehensif untuk K-Means clustering
    """
    evaluation_metrics = {}
    
    # 1. Silhouette Score (kisaran: -1 hingga 1, semakin tinggi semakin baik)
    silhouette = silhouette_score(weighted_data, clusters)
    evaluation_metrics['silhouette_score'] = silhouette
    
    # 2. Calinski-Harabasz Score (semakin tinggi semakin baik)
    calinski_harabasz = calinski_harabasz_score(weighted_data, clusters)
    evaluation_metrics['calinski_harabasz_score'] = calinski_harabasz
    
    # 3. Davies-Bouldin Score (semakin rendah semakin baik)
    davies_bouldin = davies_bouldin_score(weighted_data, clusters)
    evaluation_metrics['davies_bouldin_score'] = davies_bouldin
    
    # 4. Inertia (Within-cluster sum of squares)
    kmeans_temp = KMeans(n_clusters=3, random_state=0)
    kmeans_temp.fit(weighted_data)
    evaluation_metrics['inertia'] = kmeans_temp.inertia_
    
    # 5. Cluster distribution analysis
    unique, counts = np.unique(clusters, return_counts=True)
    cluster_distribution = dict(zip(unique.tolist(), counts.tolist()))
    evaluation_metrics['cluster_distribution'] = cluster_distribution
    
    # 6. Cluster balance (standard deviation of cluster sizes)
    cluster_balance = np.std(counts)
    evaluation_metrics['cluster_balance'] = cluster_balance
    
    # 7. Cluster centers
    evaluation_metrics['cluster_centers'] = kmeans_temp.cluster_centers_.tolist()
    
    # 8. Interpretasi kualitas clustering
    quality_interpretation = interpret_clustering_quality(silhouette, calinski_harabasz, davies_bouldin)
    evaluation_metrics['quality_interpretation'] = quality_interpretation
    
    return evaluation_metrics

def interpret_clustering_quality(silhouette, calinski_harabasz, davies_bouldin):
    """
    Interpretasi kualitas clustering berdasarkan metrik
    """
    interpretation = {}
    
    # Silhouette Score interpretation
    if silhouette > 0.7:
        interpretation['silhouette'] = "Excellent clustering structure"
    elif silhouette > 0.5:
        interpretation['silhouette'] = "Good clustering structure"
    elif silhouette > 0.3:
        interpretation['silhouette'] = "Moderate clustering structure"
    else:
        interpretation['silhouette'] = "Poor clustering structure"
    
    # Calinski-Harabasz Score interpretation (relative)
    if calinski_harabasz > 100:
        interpretation['calinski_harabasz'] = "High cluster separation"
    elif calinski_harabasz > 50:
        interpretation['calinski_harabasz'] = "Moderate cluster separation"
    else:
        interpretation['calinski_harabasz'] = "Low cluster separation"
    
    # Davies-Bouldin Score interpretation
    if davies_bouldin < 0.5:
        interpretation['davies_bouldin'] = "Excellent cluster compactness"
    elif davies_bouldin < 1.0:
        interpretation['davies_bouldin'] = "Good cluster compactness"
    elif davies_bouldin < 1.5:
        interpretation['davies_bouldin'] = "Moderate cluster compactness"
    else:
        interpretation['davies_bouldin'] = "Poor cluster compactness"
    
    return interpretation

def evaluate_decision_tree(data, labels, clf):
    """
    Evaluasi komprehensif untuk Decision Tree
    """
    evaluation_metrics = {}
    
    # 1. Prediksi pada data training
    predictions = clf.predict(data)
    
    # 2. Accuracy
    accuracy = accuracy_score(labels, predictions)
    evaluation_metrics['accuracy'] = accuracy
    
    # 3. Precision, Recall, F1-Score untuk setiap kelas
    precision = precision_score(labels, predictions, average='weighted')
    recall = recall_score(labels, predictions, average='weighted')
    f1 = f1_score(labels, predictions, average='weighted')
    
    evaluation_metrics['precision_weighted'] = precision
    evaluation_metrics['recall_weighted'] = recall
    evaluation_metrics['f1_weighted'] = f1
    
    # 4. Precision, Recall, F1-Score per kelas
    precision_per_class = precision_score(labels, predictions, average=None)
    recall_per_class = recall_score(labels, predictions, average=None)
    f1_per_class = f1_score(labels, predictions, average=None)
    
    evaluation_metrics['precision_per_class'] = precision_per_class.tolist()
    evaluation_metrics['recall_per_class'] = recall_per_class.tolist()
    evaluation_metrics['f1_per_class'] = f1_per_class.tolist()
    
    # 5. Confusion Matrix
    cm = confusion_matrix(labels, predictions)
    evaluation_metrics['confusion_matrix'] = cm.tolist()
    
    # 6. Classification Report
    class_report = classification_report(labels, predictions, output_dict=True)
    evaluation_metrics['classification_report'] = class_report
    
    # 7. Cross-validation scores (jika data cukup)
    if len(data) >= 5:
        cv_scores = cross_val_score(clf, data, labels, cv=min(5, len(data)))
        evaluation_metrics['cross_validation_scores'] = cv_scores.tolist()
        evaluation_metrics['cv_mean'] = cv_scores.mean()
        evaluation_metrics['cv_std'] = cv_scores.std()
    
    # 8. Feature importance
    feature_importance = clf.feature_importances_
    evaluation_metrics['feature_importance'] = {
        'score': feature_importance[0],
        'work_time': feature_importance[1]
    }
    
    # 9. Tree statistics
    evaluation_metrics['tree_depth'] = clf.tree_.max_depth
    evaluation_metrics['n_leaves'] = clf.tree_.n_leaves
    evaluation_metrics['n_nodes'] = clf.tree_.node_count
    
    # 10. Interpretasi model
    model_interpretation = interpret_decision_tree_quality(accuracy, precision, recall, f1)
    evaluation_metrics['model_interpretation'] = model_interpretation
    
    return evaluation_metrics

def interpret_decision_tree_quality(accuracy, precision, recall, f1):
    """
    Interpretasi kualitas decision tree berdasarkan metrik
    """
    interpretation = {}
    
    # Accuracy interpretation
    if accuracy > 0.9:
        interpretation['accuracy'] = "Excellent model performance"
    elif accuracy > 0.8:
        interpretation['accuracy'] = "Good model performance"
    elif accuracy > 0.7:
        interpretation['accuracy'] = "Moderate model performance"
    else:
        interpretation['accuracy'] = "Poor model performance"
    
    # F1-Score interpretation
    if f1 > 0.9:
        interpretation['f1'] = "Excellent balance between precision and recall"
    elif f1 > 0.8:
        interpretation['f1'] = "Good balance between precision and recall"
    elif f1 > 0.7:
        interpretation['f1'] = "Moderate balance between precision and recall"
    else:
        interpretation['f1'] = "Poor balance between precision and recall"
    
    return interpretation

def kmeans(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    if not submissions:
        return {'message': 'Data tidak ditemukan'}, 404

    data = []
    for s in submissions:
        if s.score is not None:
            total_seconds = s.work_time.hour * 3600 + s.work_time.minute * 60 + s.work_time.second
            data.append([s.score, total_seconds])

    if len(data) < 3:
        return {'message': 'Data yang tersedia terlalu sedikit.'}, 400
    
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    weighted_data = []
    for d in data_scaled:
        weighted_data.append([
            d[0] * 0.7,
            d[1] * 0.3  
        ])

    kmeans_model = KMeans(n_clusters=3, random_state=0)
    clusters = kmeans_model.fit_predict(weighted_data)

    # Evaluasi komprehensif
    evaluation_metrics = evaluate_kmeans_clustering(data_scaled, weighted_data, clusters)
    
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
                'cluster': s.cluster,
            })
            idx += 1
        else:
            s.cluster = None

    db.session.commit()

    return {
        "clusters": hasil,
        "evaluation_metrics": evaluation_metrics
    }

def decision_tree(quiz_id):
    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()
    if not submissions:
        return {'message': 'Data tidak ditemukan'}, 404

    data = []
    labels = []
    for s in submissions:
        if s.score is not None and s.cluster is not None:
            total_seconds = s.work_time.hour * 3600 + s.work_time.minute * 60 + s.work_time.second        
            data.append([s.score, total_seconds])
            labels.append(s.cluster)

    if len(data) < 3:
        return {'message': 'Data yang tersedia terlalu sedikit untuk decision tree'}, 400

    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(data, labels)

    feature_names = ["score", "work_time"]
    rules = export_text(clf, feature_names=feature_names)

    # Evaluasi komprehensif
    evaluation_metrics = evaluate_decision_tree(data, labels, clf)

    return {
        "rules": rules,
        "evaluation_metrics": evaluation_metrics
    }

def print_kmeans_evaluation(evaluation_metrics):
    """
    Print evaluasi K-Means dengan format yang rapi
    """
    print("\n" + "="*60)
    print("           K-MEANS CLUSTERING EVALUATION")
    print("="*60)
    
    print(f"Silhouette Score: {evaluation_metrics['silhouette_score']:.4f}")
    print(f"  └─ {evaluation_metrics['quality_interpretation']['silhouette']}")
    
    print(f"\nCalinski-Harabasz Score: {evaluation_metrics['calinski_harabasz_score']:.4f}")
    print(f"  └─ {evaluation_metrics['quality_interpretation']['calinski_harabasz']}")
    
    print(f"\nDavies-Bouldin Score: {evaluation_metrics['davies_bouldin_score']:.4f}")
    print(f"  └─ {evaluation_metrics['quality_interpretation']['davies_bouldin']}")
    
    print(f"\nInertia (WCSS): {evaluation_metrics['inertia']:.4f}")
    print(f"Cluster Balance (std): {evaluation_metrics['cluster_balance']:.4f}")
    
    print(f"\nCluster Distribution:")
    for cluster, count in evaluation_metrics['cluster_distribution'].items():
        print(f"  Cluster {cluster}: {count} students")
    
    print(f"\nCluster Centers:")
    for i, center in enumerate(evaluation_metrics['cluster_centers']):
        print(f"  Cluster {i}: [Score: {center[0]:.4f}, Time: {center[1]:.4f}]")

def print_decision_tree_evaluation(evaluation_metrics):
    """
    Print evaluasi Decision Tree dengan format yang rapi
    """
    print("\n" + "="*60)
    print("           DECISION TREE EVALUATION")
    print("="*60)
    
    print(f"Accuracy: {evaluation_metrics['accuracy']:.4f}")
    print(f"  └─ {evaluation_metrics['model_interpretation']['accuracy']}")
    
    print(f"\nWeighted Metrics:")
    print(f"  Precision: {evaluation_metrics['precision_weighted']:.4f}")
    print(f"  Recall: {evaluation_metrics['recall_weighted']:.4f}")
    print(f"  F1-Score: {evaluation_metrics['f1_weighted']:.4f}")
    print(f"  └─ {evaluation_metrics['model_interpretation']['f1']}")
    
    print(f"\nPer-Class Metrics:")
    for i, (prec, rec, f1) in enumerate(zip(
        evaluation_metrics['precision_per_class'],
        evaluation_metrics['recall_per_class'],
        evaluation_metrics['f1_per_class']
    )):
        print(f"  Cluster {i}: Precision={prec:.4f}, Recall={rec:.4f}, F1={f1:.4f}")
    
    print(f"\nFeature Importance:")
    print(f"  Score: {evaluation_metrics['feature_importance']['score']:.4f}")
    print(f"  Work Time: {evaluation_metrics['feature_importance']['work_time']:.4f}")
    
    print(f"\nTree Statistics:")
    print(f"  Max Depth: {evaluation_metrics['tree_depth']}")
    print(f"  Number of Leaves: {evaluation_metrics['n_leaves']}")
    print(f"  Number of Nodes: {evaluation_metrics['n_nodes']}")
    
    if 'cross_validation_scores' in evaluation_metrics:
        print(f"\nCross-Validation:")
        print(f"  Mean CV Score: {evaluation_metrics['cv_mean']:.4f}")
        print(f"  CV Std: {evaluation_metrics['cv_std']:.4f}")
    
    print(f"\nConfusion Matrix:")
    cm = evaluation_metrics['confusion_matrix']
    print("     ", end="")
    for i in range(len(cm)):
        print(f"Pred{i:2d}", end="  ")
    print()
    for i, row in enumerate(cm):
        print(f"Act{i:2d}", end="  ")
        for val in row:
            print(f"{val:4d}", end="  ")
        print()

def run_analysis(quiz_id):
    with app.app_context():
        # Panggil K-Means
        print("\n🔍 Running K-Means Clustering Analysis...")
        hasil_kmeans = kmeans(quiz_id)
        if isinstance(hasil_kmeans, tuple):
            print(f"❌ Error: {hasil_kmeans[0]['message']}")
            return

        print_kmeans_evaluation(hasil_kmeans['evaluation_metrics'])
        
        # Panggil Decision Tree
        print("\n🌳 Running Decision Tree Analysis...")
        hasil_tree = decision_tree(quiz_id)
        if isinstance(hasil_tree, tuple):
            print(f"❌ Error: {hasil_tree[0]['message']}")
            return

        print_decision_tree_evaluation(hasil_tree['evaluation_metrics'])
        
        print("\n" + "="*60)
        print("           DECISION TREE RULES")
        print("="*60)
        print(hasil_tree['rules'])
        
        print("\n" + "="*60)
        print("           ANALYSIS COMPLETE")
        print("="*60)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_analysis.py <quiz_id>")
        sys.exit(1)
    
    quiz_id = int(sys.argv[1])
    run_analysis(quiz_id)
