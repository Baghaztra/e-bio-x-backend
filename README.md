# Flask REST API dengan MySQL
Aplikasi REST API sederhana menggunakan Flask dan MySQL dengan implementasi konsep MVC (Model-View-Controller) untuk backend aplikasi e-learning E-Bio X.
#### By *Baghaztra Van Ril*
---

## Struktur Proyek
```
.
├── src/
│   ├── __init__.py          # Inisialisasi aplikasi Flask
│   ├── config/
│   ├── controllers/
│   ├── database/
│   └── models/
├── app.py                   # Entry point aplikasi
└── requirements.txt         # Dependensi proyek
```

## Prasyarat

- Python 3.8+
- MySQL Server

## Instalasi

1. Clone repositori
```bash
git clone https://github.com/Baghaztra/e-bio-x-backend.git
cd e-bio-x-backend
```

2. Buat dan aktifkan virtual environment
```bash
python -m venv .venv
```
> windows
```bash
.venv\Scripts\activate 
```
> linux/mac
```bash
source .venv/bin/activate
```

3. Install dependensi
```bash
pip install -r requirements.txt
```

4. Konfigurasi Environment

Salin file `.env.example` menjadi `.env`, kemudian sesuaikan isinya.
> windows
```bash
cp .env.example .env
```
> linux/mac
```bash
copy .env.example .env
```

Simpan data *credentials* dari *google developer console* ke `./src/config/credentials.json` 


5. Buat database MySQL
```sql
CREATE DATABASE e_bio;
```

6. Migrasi databse
Pastikan sudah ada database dengan nama sesuai dengan yanga ada pada `.env`
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```
7. Seeder database (Optional)
```bash
python -m src.database.seeder
```
8. Reset databse (Jika dibutuhkan)
```bash
python -m src.database.reset
```
9. Jalankan analisis diluar aplikasi
```bash
python run_analysis.py <quiz_id>
```
Catatan: Ganti `<quiz_id>` dengan ID kuis yang ingin dianalisis. ID kuis dapat ditemukan di database pada tabel `quiz`.

1. Jalankan aplikasi
```bash
python app.py
```
Aplikasi akan berjalan di `http://localhost:5000`

## Teknologi yang Digunakan

- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM untuk database
- **Flask-Migrate**: Database migrations
- **MySQL**: Database
- **python-dotenv**: Environment variables
- **Faker**: Generate data dummy
