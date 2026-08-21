# MYnyak Engsel (Sunset Web UI)

A modern, fast, and secure Web UI client for an Indonesian mobile internet service provider.
Originally a CLI application, this project has been completely overhauled into a **Serverless-ready Web Application** built with FastAPI and Vanilla JS.

## 🌟 Fitur Utama
- **Modern Glassmorphism UI**: Antarmuka responsif dan mulus tanpa reload halaman (*Single Page Application*).
- **Vercel Ready**: Dirancang khusus agar bisa di-*deploy* ke Vercel secara gratis menggunakan *Serverless Functions*.
- **Multi-Account**: Mendukung pergantian akun dengan sangat cepat menggunakan `localStorage` browser.
- **PostgreSQL Caching**: Menggunakan PostgreSQL (Supabase/Neon) via SQLAlchemy + pg8000 untuk melakukan *cache* terhadap token dan mengurangi beban limit API provider.
- **Stateless Backend**: Aman dari kebocoran sesi antar-pengguna (*No Race Conditions*).
- **Vercel Cron Job**: Dilengkapi fitur `keepalive` harian untuk memastikan *database* gratisan kamu tidak dimatikan paksa.

## 🚀 Cara Instalasi (Lokal)

1. Pastikan kamu memiliki Python 3.10 atau versi lebih baru.
2. Buat file `.env` di folder proyek ini (lihat bagian *Environment Variables* di bawah).
3. Instal semua kebutuhan pustaka Python:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan *backend* server FastAPI:
   ```bash
   uvicorn webapp.server:app --reload
   ```
5. Buka `http://127.0.0.1:8000` di browsermu!

*(Catatan: Jika dijalankan di lokal tanpa URL PostgreSQL di file `.env`, sistem secara otomatis akan menggunakan `local_cache.db` bawaan SQLite).*

## 🌍 Cara Deployment (Vercel & Supabase)
1. Buat database PostgreSQL gratis di Supabase, dan catat `Connection URL`-nya.
2. Push repositori ini ke GitHub milikmu.
3. Import ke Vercel, lalu isi **Environment Variables** berikut di pengaturan Vercel:
   - `DATABASE_URL`: Isi dengan link dari Supabase.
   - `API_KEY`: Rahasia API kamu.
4. Klik Deploy!

## 🔐 Environment Variables (.env)
Buat file `.env` sejajar dengan folder utama, lalu isi dengan konfigurasi berikut:
```env
API_KEY=KODE_RAHASIA_PROVIDER_DI_SINI
DATABASE_URL=postgresql://... (Opsional jika run di lokal, wajib jika di Vercel)
```

## ⚠️ Disclaimer & Terms of Service
**Pesan untuk penyedia layanan:** Daripada sekadar menyembunyikan paket promo dari aplikasi resmi, pastikan celah pembelian di server kalian benar-benar ditutup. Tidak ada gunanya keamanan UI yang ketat jika API server tidak memvalidasinya.

Dengan menggunakan alat ini, pengguna setuju untuk mematuhi seluruh hukum yang berlaku dan melepaskan *developer* dari segala macam tuntutan hukum. Proyek ini murni dibuat sebagai bahan edukasi dan pengembangan UI/UX.

---
**Contact:** contact@mashu.lol
