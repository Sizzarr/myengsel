# MYnyak Engsel (Sunset Web UI)

A modern, fast, and secure Web UI client for an Indonesian mobile internet service provider.
Originally a CLI application, this project has been completely overhauled into a **Serverless-ready Web Application** built with FastAPI and Vanilla JS.

## Login akun dan penyimpanan nomor

1. Buat akun aplikasi dengan username dan password, lalu masuk.
2. Tambahkan nomor XL dan verifikasi OTP dari SMS.
3. Nomor dan token provider tersimpan di database, terpisah untuk setiap akun aplikasi.
4. Saat halaman di-refresh, cookie sesi memulihkan akun dan daftar nomor. Setelah logout dan login lagi, nomor tersimpan tetap tersedia.

Password disimpan sebagai hash PBKDF2; token provider dienkripsi dengan AES-GCM. Browser hanya menerima metadata nomor dan cookie sesi HttpOnly, bukan token provider. Cookie sesi berlaku 30 hari. Masa berlaku dan pencabutan sesi provider tetap mengikuti provider; OTP ulang mungkin diperlukan jika refresh token sudah tidak berlaku.

Konfigurasi server membutuhkan `DATABASE_URL` dan `TOKEN_ENCRYPTION_KEY`, selain semua variabel integrasi provider di `.env.template`. Buat kunci sekali dengan:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Simpan hasilnya sebagai `TOKEN_ENCRYPTION_KEY` di environment server. Gunakan nilai yang sama pada setiap deploy dan instance yang memakai database tersebut. Jika kunci berubah, token tersimpan tidak dapat dibuka.

Inisialisasi aplikasi hanya membuat tabel akun, sesi, dan nomor baru; tabel cache lama tidak dibuat ulang. Token dari `localStorage` atau cache versi lama tidak dikaitkan otomatis ke username baru. Setelah upgrade ini, daftar akun aplikasi dan verifikasi nomor sekali lagi.

## 🌟 Fitur Utama
- **Modern Glassmorphism UI**: Antarmuka responsif dan mulus tanpa reload halaman (*Single Page Application*).
- **Vercel Ready**: Dirancang khusus agar bisa di-*deploy* ke Vercel secara gratis menggunakan *Serverless Functions*.
- **Multi-Account**: Mendukung beberapa nomor XL per akun aplikasi, dengan pilihan nomor aktif tersimpan di database.
- **PostgreSQL Caching**: Menggunakan PostgreSQL (Supabase/Neon) via SQLAlchemy + pg8000 untuk melakukan *cache* terhadap token dan mengurangi beban limit API provider.
- **Sesi tersimpan**: Cookie sesi dan kepemilikan nomor diverifikasi di server; token provider tersimpan terenkripsi di database.
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

*(Catatan: Tanpa `DATABASE_URL`, pengembangan lokal memakai SQLite `local_accounts.db` yang diabaikan Git. Jalankan satu proses server saat memakai SQLite. Deploy Vercel dan beberapa proses server wajib menggunakan database PostgreSQL eksternal.)*

## 🌍 Cara Deployment (Vercel & Supabase)
1. Buat database PostgreSQL gratis di Supabase, dan catat `Connection URL`-nya.
2. Push repositori ini ke GitHub milikmu.
3. Import ke Vercel, lalu isi **Environment Variables** berikut di pengaturan Vercel:
   - `DATABASE_URL`: Isi dengan link dari Supabase.
   - `API_KEY`: Rahasia API kamu.
   - `TOKEN_ENCRYPTION_KEY`: Kunci tetap dari perintah di atas untuk enkripsi token tersimpan.
   - Isi juga variabel integrasi provider lainnya sesuai `.env.template`.
4. Klik Deploy!

## 🔐 Environment Variables (.env)
Buat file `.env` sejajar dengan folder utama, lalu isi dengan konfigurasi berikut:
```env
API_KEY=KODE_RAHASIA_PROVIDER_DI_SINI
DATABASE_URL=postgresql://... (Opsional jika run di lokal, wajib jika di Vercel)
TOKEN_ENCRYPTION_KEY=HASIL_GENERATOR_KUNCI_DI_ATAS
```

Jangan commit `.env` atau database lokal. `TOKEN_ENCRYPTION_KEY` berbeda dari kunci enkripsi protokol provider seperti `XDATA_KEY`.

## Pengujian akun

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Pengujian memakai SQLite sementara dan mock provider: tidak mengirim OTP atau transaksi nyata. Cakupannya meliputi pemulihan sesi setelah refresh, logout/login ulang, pemisahan nomor antar pengguna, token terenkripsi, rotasi refresh token, dan pembatasan percobaan login.

## ⚠️ Disclaimer & Terms of Service
**Pesan untuk penyedia layanan:** Daripada sekadar menyembunyikan paket promo dari aplikasi resmi, pastikan celah pembelian di server kalian benar-benar ditutup. Tidak ada gunanya keamanan UI yang ketat jika API server tidak memvalidasinya.

Dengan menggunakan alat ini, pengguna setuju untuk mematuhi seluruh hukum yang berlaku dan melepaskan *developer* dari segala macam tuntutan hukum. Proyek ini murni dibuat sebagai bahan edukasi dan pengembangan UI/UX.

---
**Contact:** contact@mashu.lol
