# PRD — Portal HARNAS UMKM 12 Agustus 2026 & Digital Fan Wall ABDSI

## Original Problem Statement
"ikuti intruksi markdown berikut lalu kerjakan, khusus fan wall dan profile card nya tiru gaya desain nya 100 % dengan tambahan role"

Pilihan user:
- Membangun seluruh portal HARNAS UMKM: Fan Wall, sejarah, ABDSI, TNP IV, dan katalog UMKM.
- Target database adalah Supabase PostgreSQL; Transaction Pooler URI belum diberikan.
- Role tambahan menggunakan default `Lainnya`.

## Architecture Decisions
- Frontend mempertahankan scaffold React 19 + Tailwind/CSS, Framer Motion, Lucide, Axios, dan Sonner.
- Backend menggunakan FastAPI dengan database MongoDB yang sudah aktif di environment agar alur end-to-end langsung fungsional.
- API publik: list/search/filter/sort Fan Wall, statistik, submit moderasi, dan like dengan deduplikasi berbasis fingerprint privat.
- Kiriman baru disimpan dengan `is_approved=false` dan tidak muncul sebelum moderasi.
- Supabase PostgreSQL tetap menjadi target migrasi setelah user memberikan Transaction Pooler URI port 6543.

## Implemented
- Hero nasional, countdown HARNAS, statistik, navigasi desktop/mobile, dan CTA aspirasi.
- Digital Fan Wall bergaya referensi MSMEs Day 2026: profile/story cards, role, lokasi, pesan editorial, hover, loading skeleton, search, filter, sort, detail modal, like, dan WhatsApp share.
- Form aspirasi lengkap dengan role `Lainnya`, provinsi, kota, foto, validasi, loading, success state, dan moderasi.
- Bagian sejarah Bung Hatta/Piagam Yogyakarta, ekosistem ABDSI, kepemimpinan, TNP IV/ICCME Pontianak, katalog UMKM, serta footer CTA.
- Responsif desktop/tablet/mobile, akses keyboard, focus states, reduced motion, dan data-testid pada flow utama.
- Pengujian: frontend build sukses, lint bersih, 9/9 API tests lulus, E2E desktop/mobile lulus.

## Prioritized Backlog
### P0
- Migrasikan persistence dari MongoDB ke Supabase PostgreSQL setelah Transaction Pooler URI diberikan.
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
1. Terima Supabase Transaction Pooler URI dan jalankan migrasi schema/data.
2. Bangun moderasi aspirasi dan pengelolaan katalog.
3. Isi konten/foto resmi ABDSI, TNP IV, dan produk UMKM final.