```
🔍 Running K-Means Clustering Analysis...

============================================================
           K-MEANS CLUSTERING EVALUATION
============================================================
Silhouette Score: 0.4195
  └─ Moderate clustering structure

Calinski-Harabasz Score: 75.2672
  └─ Moderate cluster separation

Davies-Bouldin Score: 0.8633
  └─ Good cluster compactness

Inertia (WCSS): 6.6519
Cluster Balance (std): 1.2472

Cluster Distribution:
  Cluster 0: 16 students
  Cluster 1: 15 students
  Cluster 2: 18 students

Cluster Centers:
  Cluster 0: [Score: -0.0101, Time: 0.0855]
  Cluster 1: [Score: 0.8881, Time: 0.0299]
  Cluster 2: [Score: -0.7311, Time: -0.1009]

🌳 Running Decision Tree Analysis...

============================================================
           DECISION TREE EVALUATION
============================================================
Accuracy: 1.0000
  └─ Excellent model performance

Weighted Metrics:
  Precision: 1.0000
  Recall: 1.0000
  F1-Score: 1.0000
  └─ Excellent balance between precision and recall

Per-Class Metrics:
  Cluster 0: Precision=1.0000, Recall=1.0000, F1=1.0000
  Cluster 1: Precision=1.0000, Recall=1.0000, F1=1.0000
  Cluster 2: Precision=1.0000, Recall=1.0000, F1=1.0000

Feature Importance:
  Score: 0.9418
  Work Time: 0.0582

Tree Statistics:
  Max Depth: 2
  Number of Leaves: 4
  Number of Nodes: 7

Cross-Validation:
  Mean CV Score: 0.9600
  CV Std: 0.0800

Confusion Matrix:
     Pred 0  Pred 1  Pred 2
Act 0    16     0     0
Act 1     0    15     0
Act 2     0     0    18

============================================================
           DECISION TREE RULES
============================================================
|--- score <= 28.76
|   |--- work_time <= 1620.00
|   |   |--- class: 2
|   |--- work_time >  1620.00
|   |   |--- class: 0
|--- score >  28.76
|   |--- score <= 59.12
|   |   |--- class: 0
|   |--- score >  59.12
|   |   |--- class: 1


============================================================
           ANALYSIS COMPLETE
============================================================
```
# Analisis Model

## **📊 K-Means Clustering Analysis**

### **Kualitas Clustering:**
- **Silhouette Score (0.4195)**: Menunjukkan struktur clustering yang **moderat**. Nilai ini berada di antara 0.3-0.5, yang berarti siswa terbagi dengan cukup baik ke dalam 3 cluster, namun masih ada beberapa overlap.

- **Calinski-Harabasz Score (75.27)**: Menunjukkan **separasi cluster yang moderat**. Cluster tidak terlalu terpisah jauh, namun masih dapat dibedakan.

- **Davies-Bouldin Score (0.86)**: Menunjukkan **kompaktasi cluster yang baik**. Nilai < 1.0 menandakan cluster cukup kompak dan tidak terlalu tersebar.

### **Distribusi Siswa:**
- **Cluster 0**: 16 siswa (cluster sedang)
- **Cluster 1**: 15 siswa (cluster tinggi) 
- **Cluster 2**: 18 siswa (cluster rendah)

Distribusi cukup seimbang dengan standar deviasi 1.25.

### **Karakteristik Cluster:**
- **Cluster 0**: Skor rata-rata, waktu kerja agak lambat
- **Cluster 1**: Skor tinggi, waktu kerja cepat (**siswa berprestasi**)
- **Cluster 2**: Skor rendah, waktu kerja cepat (**siswa yang kesulitan**)

## **🌳 Decision Tree Analysis**

### **Performa Model:**
- **Accuracy 100%**: Model **sempurna** dalam memprediksi cluster berdasarkan skor dan waktu kerja
- **Precision, Recall, F1-Score semua 100%**: Tidak ada kesalahan prediksi sama sekali
- **Cross-validation 96%**: Meski training accuracy 100%, CV menunjukkan kemungkinan sedikit overfitting

### **Confusion Matrix:**
```
        Prediksi
Aktual   0   1   2
   0    16   0   0  ← Cluster 0: 100% benar
   1     0  15   0  ← Cluster 1: 100% benar  
   2     0   0  18  ← Cluster 2: 100% benar
```

### **Feature Importance:**
- **Score (94.18%)**: Skor quiz adalah faktor **dominan** dalam penentuan cluster
- **Work Time (5.82%)**: Waktu kerja hanya berpengaruh **minor**

## **📋 Decision Tree Rules (Aturan Klasifikasi):**

```
1. Jika skor ≤ 28.76:
   - Jika waktu ≤ 1620 detik (27 menit) → Cluster 2 (Rendah)
   - Jika waktu > 1620 detik → Cluster 0 (Sedang)

2. Jika skor > 28.76:
   - Jika skor ≤ 59.12 → Cluster 0 (Sedang)
   - Jika skor > 59.12 → Cluster 1 (Tinggi)
```

## **🎯 Interpretasi Praktis:**

### **Profil Siswa:**
1. **Cluster 1 (Berprestasi)**: Skor > 59.12 - Siswa dengan pemahaman materi yang baik
2. **Cluster 0 (Sedang)**: Skor 28.76-59.12 - Siswa dengan pemahaman rata-rata
3. **Cluster 2 (Perlu Bantuan)**: Skor ≤ 28.76 & cepat selesai - Siswa yang mungkin menyerah atau tidak memahami materi

### **Insight Penting:**
- **Skor adalah faktor utama** (94%) dalam menentukan performa siswa
- **Waktu kerja singkat dengan skor rendah** menunjukkan siswa yang kesulitan
- **Model sangat akurat** dalam mengklasifikasikan siswa berdasarkan pola ini

### **Rekomendasi:**
- Fokus perhatian pada **Cluster 2** (18 siswa) yang memerlukan bantuan ekstra
- **Cluster 1** (15 siswa) dapat diberikan tantangan lebih
- **Cluster 0** (16 siswa) memerlukan pendampingan rutin

Model ini sangat efektif untuk identifikasi dini siswa yang memerlukan intervensi pembelajaran!