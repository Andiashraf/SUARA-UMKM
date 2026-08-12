import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import { Heart, MapPin, Search, Share2, SlidersHorizontal, X, Instagram, Linkedin } from "lucide-react";
import { FanCard } from "@/components/FanCard";
import { provinces, roles } from "@/data/content";

const API = `${process.env.REACT_APP_BACKEND_URL || ""}/api`;

const DetailModal = ({ message, onClose }) => {
  if (!message) return null;
  const share = () => window.open(`https://wa.me/?text=${encodeURIComponent(`Suara ${message.full_name}: “${message.message}”\n${window.location.href}`)}`, "_blank", "noopener,noreferrer");
  return <div className="modal-backdrop" onMouseDown={onClose} data-testid="profile-detail-modal">
    <motion.div className="detail-modal" onMouseDown={(e) => e.stopPropagation()} initial={{ opacity: 0, y: 30, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 25 }} role="dialog" aria-modal="true" aria-labelledby="detail-name">
      <button className="modal-close" onClick={onClose} data-testid="profile-detail-close-button" aria-label="Tutup detail"><X /></button>
      <div className="detail-portrait"><img src={message.avatar_url} alt={`Foto ${message.full_name}`} /><span>{message.role}</span></div>
      <div className="detail-copy">
        <div className="eyebrow" data-testid="profile-detail-province"><MapPin size={15}/>{message.city_regency}, {message.province}</div>
        <h2 id="detail-name" data-testid="profile-detail-name">{message.full_name}</h2>
        <p className="detail-business" data-testid="profile-detail-business">{message.business_name}</p>
        {(message.instagram_url || message.linkedin_url) && (
          <div className="social-links" style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
            {message.instagram_url && <a href={message.instagram_url} target="_blank" rel="noopener noreferrer" style={{ color: "#E1306C" }}><Instagram size={20}/></a>}
            {message.linkedin_url && <a href={message.linkedin_url} target="_blank" rel="noopener noreferrer" style={{ color: "#0077B5" }}><Linkedin size={20}/></a>}
          </div>
        )}
        <blockquote data-testid="profile-detail-message">“{message.message}”</blockquote>
        <div className="detail-actions"><span data-testid="profile-detail-likes"><Heart size={18}/> {message.likes_count} dukungan</span><button onClick={share} data-testid="profile-detail-share-button"><Share2 size={18}/> Bagikan via WhatsApp</button></div>
      </div>
    </motion.div>
  </div>;
};

export const FanWall = ({ onSubmit, refreshKey }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState("Semua");
  const [province, setProvince] = useState("Semua Provinsi");
  const [sort, setSort] = useState("newest");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const requestSequence = useRef(0);
  const params = useMemo(() => ({ role, province, sort, search: search.trim() }), [role, province, sort, search]);
  useEffect(() => {
    const requestId = ++requestSequence.current;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      setLoading(true);
      axios.get(`${API}/fan-wall`, { params, signal: controller.signal })
        .then(({ data }) => {
          if (requestId === requestSequence.current) setMessages(data);
        })
        .catch((error) => {
          if (requestId === requestSequence.current && error.code !== "ERR_CANCELED") setMessages([]);
        })
        .finally(() => {
          if (requestId === requestSequence.current) setLoading(false);
        });
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [params, refreshKey]);
  return (
    <section id="fan-wall" className="fan-section" data-testid="fan-wall-section">
      <div className="section-heading fan-heading">
        <div><div className="eyebrow gold" data-testid="fan-wall-eyebrow">Mosaic of Voices</div><h2 data-testid="fan-wall-heading">Suara UMKM Indonesia</h2><p data-testid="fan-wall-description">Kisah, harapan, dan aspirasi manusia yang menggerakkan ekonomi Indonesia.</p></div>
        <button className="button primary" onClick={onSubmit} data-testid="fan-wall-submit-button">Ikut bersuara <span>+</span></button>
      </div>
      <div className="wall-toolbar" data-testid="fan-wall-filter-toolbar">
        <label className="search-box"><Search size={19}/><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Cari nama, usaha, atau pesan…" data-testid="fan-wall-search-input" /></label>
        <label className="select-wrap"><SlidersHorizontal size={17}/><select value={role} onChange={(e) => setRole(e.target.value)} data-testid="fan-wall-role-filter">{roles.map((item) => <option key={item}>{item}</option>)}</select></label>
        <label className="select-wrap"><MapPin size={17}/><select value={province} onChange={(e) => setProvince(e.target.value)} data-testid="fan-wall-province-filter">{provinces.map((item) => <option key={item}>{item}</option>)}</select></label>
        <select className="sort-select" value={sort} onChange={(e) => setSort(e.target.value)} data-testid="fan-wall-sort-select"><option value="newest">Terbaru</option><option value="popular">Terpopuler</option></select>
      </div>
      <div className="wall-count" data-testid="fan-wall-result-count">
        {loading ? <span data-testid="fan-wall-result-loading">Mencari suara…</span> : <><span>{messages.length}</span> suara ditemukan</>}
      </div>
      {loading ? <div className="voice-grid" data-testid="fan-wall-loading">{[1,2,3].map((n) => <div className="voice-skeleton" key={n}><i/><b/><span/><span/></div>)}</div>
        : messages.length ? <motion.div className="voice-grid" layout data-testid="fan-wall-grid">{messages.map((message) => <motion.div layout key={message.id}><FanCard message={message} onOpen={setSelected}/></motion.div>)}</motion.div>
        : <div className="wall-empty" data-testid="fan-wall-empty-state"><Search/><h3>Belum ada suara yang cocok</h3><p>Coba kata kunci atau filter lain.</p></div>}
      <AnimatePresence>{selected && <DetailModal message={selected} onClose={() => setSelected(null)} />}</AnimatePresence>
    </section>
  );
};