# Flask REST API dengan MySQL

Aplikasi REST API sederhana menggunakan Flask dan MySQL dengan implementasi konsep MVC (Model-View-Controller).

## Struktur Proyek
```
.
├── app/
│   ├── __init__.py          # Inisialisasi aplikasi Flask
│   ├── config/
│   │   └── database.py      # Konfigurasi database
│   ├── controllers/
│   │   └── user_controller.py  # Controller untuk endpoint users
│   ├── database/
│   │   └── seeder.py        # Script untuk generate data dummy
│   └── models/
│       └── user.py          # Model untuk tabel users
├── app.py                   # Entry point aplikasi
├── .env                     # Environment variables
└── requirements.txt         # Dependensi proyek
```

## Prasyarat

- Python 3.8+
- MySQL Server
- Virtual Environment (venv)

## Instalasi

1. Clone repositori ini
```bash
git clone [url-repositori]
cd [nama-folder]
```

2. Buat dan aktifkan virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependensi
```bash
pip install -r requirements.txt
```

4. Konfigurasi database
   - Buat file `.env` (jika belum ada)
   - Isi dengan konfigurasi berikut:
```env
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_DATABASE=flask_db
SECRET_KEY=your-secret-key-here
```

5. Buat database MySQL
```sql
CREATE DATABASE flask_db;
```

## Menjalankan Aplikasi

1. Jalankan aplikasi
```bash
python app.py
```
Aplikasi akan berjalan di `http://localhost:5000`

2. Generate data dummy (opsional)
```bash
python -m app.database.seeder
```

## API Endpoints

### 1. Root Endpoint
- URL: `/`
- Method: `GET`
- Response: "Hello, World!"
```bash
curl http://localhost:5000/
```

### 2. Get All Users
- URL: `/api/users`
- Method: `GET`
- Response: Array of users
```bash
curl http://localhost:5000/api/users
```
Response format:
```json
[
  {
    "id": 1,
    "username": "username1",
    "email": "email1@example.com"
  }
]
```

### 3. Create New User
- URL: `/api/users`
- Method: `POST`
- Headers: 
  - Content-Type: application/json
- Body:
```json
{
  "username": "new_user",
  "email": "new_user@example.com"
}
```
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"username":"new_user","email":"new_user@example.com"}' \
     http://localhost:5000/api/users
```
Response format:
```json
{
  "message": "User berhasil dibuat",
  "user": {
    "id": 1,
    "username": "new_user",
    "email": "new_user@example.com"
  }
}
```

## Teknologi yang Digunakan

- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM untuk database
- **Flask-Migrate**: Database migrations
- **MySQL**: Database
- **python-dotenv**: Environment variables
- **Faker**: Generate data dummy

## Konsep MVC

Proyek ini mengimplementasikan pola arsitektur MVC:
- **Model**: `app/models/` - Mendefinisikan struktur data
- **View**: Tidak ada karena ini adalah REST API
- **Controller**: `app/controllers/` - Menangani logika bisnis

## Development

### Database Migrations
Migrasi database ditangani oleh Flask-Migrate dan SQLAlchemy. Tabel akan dibuat otomatis saat aplikasi pertama kali dijalankan.

### Data Seeding
Untuk mengisi database dengan data dummy, gunakan seeder:
```bash
python -m app.database.seeder
```
Ini akan membuat 10 user dummy menggunakan Faker.

## Catatan Keamanan

1. Jangan lupa untuk mengubah `SECRET_KEY` di file `.env`
2. Jangan meng-commit file `.env` ke repositori
3. Gunakan password yang kuat untuk database
4. Aplikasi ini masih dalam mode development (`debug=True`), ubah ke `False` untuk production

## Kontribusi

1. Fork repositori
2. Buat branch fitur baru
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request
