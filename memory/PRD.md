# PRD — Portal HARNAS UMKM 12 Agustus 2026 & Digital Fan Wall ABDSI

## Original Problem Statement
"ikuti intruksi markdown berikut lalu kerjakan, khusus fan wall dan profile card nya tiru gaya desain nya 100 % dengan tambahan role"

Pilihan user:
- Membangun seluruh portal HARNAS UMKM: Fan Wall, sejarah, ABDSI, TNP IV, dan katalog UMKM.
- Database menggunakan Supabase PostgreSQL melalui Transaction Pooler.
- Role tambahan menggunakan default `Lainnya`.

## Architecture Decisions
- Frontend mempertahankan scaffold React 19 + Tailwind/CSS, Framer Motion, Lucide, Axios, dan Sonner.
- Backend menggunakan FastAPI, SQLAlchemy async, asyncpg, dan Supabase PostgreSQL melalui Transaction Pooler port 6543.
- Seluruh schema dikelola dengan Alembic revision `20260811_0001`; startup menjalankan `alembic upgrade head` sebelum proses seed.
- API publik: list/search/filter/sort Fan Wall, statistik, submit moderasi, dan like dengan deduplikasi berbasis fingerprint privat.
- Kiriman baru disimpan dengan `is_approved=false` dan tidak muncul sebelum moderasi.
- Reaksi disimpan pada tabel terpisah dengan unique constraint untuk mencegah duplikasi dukungan dari fingerprint yang sama.

## Implemented
- Hero nasional, countdown HARNAS, statistik, navigasi desktop/mobile, dan CTA aspirasi.
- Digital Fan Wall bergaya referensi MSMEs Day 2026: profile/story cards, role, lokasi, pesan editorial, hover, loading skeleton, search, filter, sort, detail modal, like, dan WhatsApp share.
- Form aspirasi lengkap dengan role `Lainnya`, provinsi, kota, foto, validasi, loading, success state, dan moderasi.
- Bagian sejarah Bung Hatta/Piagam Yogyakarta, ekosistem ABDSI, kepemimpinan, TNP IV/ICCME Pontianak, katalog UMKM, serta footer CTA.
- Responsif desktop/tablet/mobile, akses keyboard, focus states, reduced motion, dan data-testid pada flow utama.
- Pengujian: frontend build sukses, lint bersih, 9/9 API tests lulus, E2E desktop/mobile lulus.
- Integrasi Supabase aktif: schema, seed, list/search/filter/sort/stats, submit moderasi, dan like dedupe telah diverifikasi; 13/13 regresi backend lulus.

## Prioritized Backlog
### P0
- Tambahkan dashboard moderasi aman untuk approve/reject aspirasi.

### P1
- Pindahkan foto profil ke object storage dan lakukan optimasi gambar.
- Tambahkan pagination/infinite load untuk volume ribuan suara.
- Tambahkan metadata Open Graph unik untuk setiap profil yang dibagikan.

### P2
- Integrasikan data katalog UMKM dengan panel pengelolaan produk.
- Tambahkan peta partisipasi 38 provinsi dan analitik tren aspirasi.
- Tambahkan ekspor laporan partisipasi untuk kebutuhan ABDSI.

## Next Tasks
1. Bangun moderasi aspirasi dan pengelolaan katalog.
2. Pindahkan foto profil ke object storage dan optimasi gambar.
3. Isi konten/foto resmi ABDSI, TNP IV, dan produk UMKM final.