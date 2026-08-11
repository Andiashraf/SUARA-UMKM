import { ArrowRight, Award, CalendarDays, CheckCircle2, ExternalLink, MapPin, Users } from "lucide-react";
import { agenda, milestones, products } from "@/data/content";

export const PortalSections = () => <>
  <section id="sejarah" className="history-section section-pad" data-testid="history-section">
    <div className="section-heading"><div><div className="eyebrow violet">Akar Gerakan</div><h2 data-testid="history-heading">Dari pemikiran Bung Hatta,<br/>menuju gerakan nasional.</h2></div><p data-testid="history-description">Hari UMKM Nasional membawa semangat ekonomi kerakyatan: usaha yang tumbuh bersama, berdaulat, dan menyejahterakan.</p></div>
    <div className="history-layout">
      <div className="history-portrait" data-testid="bung-hatta-visual"><div className="portrait-caption"><span>12 Agustus 1902</span><b>Mohammad Hatta</b><small>Bapak Koperasi Indonesia</small></div></div>
      <div className="timeline" data-testid="history-timeline">{milestones.map((item, index) => <article key={item.year} data-testid={`history-milestone-${item.year}`}><span>{String(index + 1).padStart(2, "0")}</span><div><b>{item.year}</b><h3>{item.title}</h3><p>{item.text}</p></div></article>)}</div>
    </div>
    <blockquote className="history-quote" data-testid="history-motto">“UKM Kuat, Bangsa Berdaulat”<span>— Semangat Piagam Yogyakarta</span></blockquote>
  </section>

  <section id="abdsi" className="abdsi-section section-pad" data-testid="abdsi-section">
    <div className="abdsi-bento">
      <article className="abdsi-main"><div className="eyebrow light">Ekosistem Pendamping Nasional</div><h2 data-testid="abdsi-heading">ABDSI hadir agar UMKM tidak berjalan sendiri.</h2><p>Asosiasi Business Development Services Indonesia adalah organisasi profesi pendamping KUMKM sejak 2002—menghubungkan kompetensi, kebijakan, dan kebutuhan nyata pelaku usaha.</p><a href="#tnp" data-testid="abdsi-learn-link">Lihat agenda nasional <ArrowRight/></a></article>
      <article className="abdsi-number" data-testid="abdsi-stat-members"><Users/><strong>5.000<sup>+</sup></strong><span>Pendamping di seluruh Indonesia</span></article>
      <article className="abdsi-number amber" data-testid="abdsi-stat-regions"><MapPin/><strong>34<sup>+</sup></strong><span>DPW terhubung secara nasional</span></article>
      <article className="leader-card" data-testid="abdsi-leader-card"><div className="leader-photo"/><div><span>Ketua Umum 2026–2030</span><h3>Dr. Bahrul Ulum Ilham, S.Pd., M.M., Ph.D.</h3><p>Memimpin kolaborasi pendamping untuk pertumbuhan UMKM yang inklusif dan berkelanjutan.</p></div></article>
      <article className="standards-card" data-testid="abdsi-standards-card"><Award/><div><span>Standar Kompetensi</span><h3>SKKNI 181/2017 & BNSP</h3><p>Pendampingan profesional, terukur, dan berorientasi hasil.</p></div></article>
    </div>
  </section>

  <section id="tnp" className="event-section section-pad" data-testid="tnp-event-section">
    <div className="event-intro"><div className="eyebrow gold">Puncak Agenda Nasional</div><h2 data-testid="tnp-heading">TNP IV ABDSI<br/>& ICCME 2026</h2><p data-testid="tnp-description">Pertemuan para pendamping, akademisi, pemerintah, dan pelaku UMKM untuk merumuskan masa depan ekosistem usaha Indonesia.</p><div className="event-meta"><span><CalendarDays/>11–15 Agustus 2026</span><span><MapPin/>Universitas Tanjungpura, Pontianak</span></div><button className="button warm" data-testid="tnp-registration-button">Daftar TNP IV <ExternalLink size={18}/></button></div>
    <div className="agenda-list" data-testid="tnp-agenda-list">{agenda.map((item, index) => <article key={item.date} data-testid={`tnp-agenda-${index + 1}`}><b>{item.date}</b><div><span>0{index + 1}</span><h3>{item.title}</h3><p>{item.text}</p></div></article>)}</div>
  </section>

  <section id="showcase" className="showcase-section section-pad" data-testid="umkm-showcase-section">
    <div className="section-heading"><div><div className="eyebrow violet">Buatan Indonesia</div><h2 data-testid="showcase-heading">Produk lokal,<br/>kualitas tanpa batas.</h2></div><p>Kenali pilihan produk UMKM unggulan yang bertumbuh dengan legalitas, cerita, dan kesiapan pasar.</p></div>
    <div className="product-grid" data-testid="product-grid">{products.map((product, index) => <article className="product-card" key={product.name} data-testid={`product-card-${index + 1}`}><div className="product-image"><img src={product.image} alt={product.name} loading="lazy"/><span>0{index + 1}</span></div><div className="product-copy"><p>{product.business}</p><h3>{product.name}</h3><span className="product-location"><MapPin/>{product.location}</span><div className="product-tags">{product.tags.map((tag) => <span key={tag}><CheckCircle2/>{tag}</span>)}</div><a href={`https://wa.me/?text=${encodeURIComponent(`Halo, saya tertarik dengan ${product.name} dari ${product.business}`)}`} target="_blank" rel="noreferrer" data-testid={`product-whatsapp-${index + 1}`}>Hubungi penjual <ArrowRight/></a></div></article>)}</div>
  </section>
</>;