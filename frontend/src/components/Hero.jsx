import { useEffect, useMemo, useState } from "react";
import { ArrowDown, ArrowRight, MapPin, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const Stat = ({ value, label, suffix = "" }) => <div className="hero-stat" data-testid={`hero-stat-${label.toLowerCase().replaceAll(" ", "-")}`}><strong>{value}{suffix}</strong><span>{label}</span></div>;

export const Hero = ({ stats, onSubmit }) => {
  const target = useMemo(() => new Date("2026-08-12T00:00:00+07:00"), []);
  const [remaining, setRemaining] = useState({ days: 0, hours: 0, minutes: 0 });
  useEffect(() => {
    const tick = () => {
      const diff = Math.max(0, target.getTime() - Date.now());
      setRemaining({ days: Math.floor(diff / 86400000), hours: Math.floor(diff / 3600000) % 24, minutes: Math.floor(diff / 60000) % 60 });
    };
    tick(); const timer = setInterval(tick, 60000); return () => clearInterval(timer);
  }, [target]);
  return (
    <section id="beranda" className="hero" data-testid="hero-section">
      <div className="hero-orbit orbit-one" /><div className="hero-orbit orbit-two" />
      <div className="hero-grid">
        <motion.div className="hero-copy" initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7 }}>
          <div className="eyebrow light" data-testid="hero-event-label"><Sparkles size={16} /> Portal Nasional • 12 Agustus 2026</div>
          <h1 data-testid="hero-heading">Suara kecil.<br/><span>Dampak besar.</span></h1>
          <p className="hero-lead" data-testid="hero-description">Terhubung, tumbuh, berinovasi—sampaikan suara dan aspirasi UMKM-mu untuk Indonesia Emas 2045.</p>
          <div className="hero-actions">
            <button className="button primary light-shadow" onClick={onSubmit} data-testid="hero-submit-aspiration-button">Kirim Aspirasi UMKM <ArrowRight size={19} /></button>
            <a className="button outline-light" href="#fan-wall" data-testid="hero-explore-wall-link">Jelajahi Fan Wall <ArrowDown size={18} /></a>
          </div>
          <div className="countdown" data-testid="hero-countdown"><span>Menuju HARNAS</span><b>{remaining.days}<small>hari</small></b><b>{remaining.hours}<small>jam</small></b><b>{remaining.minutes}<small>menit</small></b></div>
        </motion.div>
        <motion.div className="hero-visual" initial={{ opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: .8, delay: .12 }}>
          <div className="hero-photo" role="img" aria-label="Komunitas pelaku UMKM Indonesia" data-testid="hero-community-image" />
          <div className="floating-note note-top" data-testid="hero-theme-note"><span>TEMA 2026</span><b>UMKM Terkoneksi,<br/>Tumbuh Berinovasi</b></div>
          <div className="floating-note note-bottom" data-testid="hero-location-note"><MapPin size={19}/><span><b>Dari 38 Provinsi</b><small>Untuk Indonesia</small></span></div>
        </motion.div>
      </div>
      <div className="hero-stats" data-testid="participation-statistics">
        <Stat value={stats.provinces || 38} label="Provinsi" />
        <Stat value={Math.max(stats.voices || 0, 5000).toLocaleString("id-ID")} suffix="+" label="Suara UMKM" />
        <Stat value="5.000" suffix="+" label="Pendamping" />
        <Stat value={stats.supports?.toLocaleString("id-ID")} label="Dukungan" />
      </div>
    </section>
  );
};