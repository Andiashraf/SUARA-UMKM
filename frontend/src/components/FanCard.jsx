import { useState } from "react";
import axios from "axios";
import { Building2, Heart, MapPin, MessageCircle, Share2 } from "lucide-react";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const FanCard = ({ message, onOpen }) => {
  const [liked, setLiked] = useState(false);
  const [likes, setLikes] = useState(message.likes_count || 0);
  const like = async () => {
    if (liked) return;
    setLiked(true); setLikes((n) => n + 1);
    try {
      const { data } = await axios.post(`${API}/fan-wall/${message.id}/like`);
      if (data.already_liked) {
        setLikes(data.likes_count);
        toast.info("Anda sudah mendukung aspirasi ini.");
      }
    }
    catch { setLiked(false); setLikes((n) => n - 1); toast.error("Dukungan belum berhasil dikirim."); }
  };
  const share = () => {
    const text = `Suara ${message.full_name} untuk UMKM Indonesia: “${message.message}”`;
    window.open(`https://wa.me/?text=${encodeURIComponent(`${text}\n${window.location.href}`)}`, "_blank", "noopener,noreferrer");
  };
  return (
    <article className="voice-card" data-testid={`profile-card-${message.id}`}>
      <div className="card-brand" data-testid={`profile-card-brand-${message.id}`}><span>12</span> HARNAS UMKM 2026</div>
      <div className="card-region" data-testid={`profile-card-location-${message.id}`}><span className="flag-dot" /> {message.province}</div>
      <button className="card-open" onClick={() => onOpen(message)} data-testid={`profile-card-open-${message.id}`} aria-label={`Buka profil ${message.full_name}`}>
        <div className="portrait-wrap">
          {message.avatar_url ? <img src={message.avatar_url} alt={`Foto ${message.full_name}`} loading="lazy" /> : <div className="avatar-fallback">{message.full_name.slice(0, 2).toUpperCase()}</div>}
          <span className="role-ribbon" data-testid={`profile-card-role-${message.id}`}>{message.role}</span>
        </div>
        <div className="voice-content">
          <h3 data-testid={`profile-card-name-${message.id}`}>{message.full_name}</h3>
          <p className="business" data-testid={`profile-card-business-${message.id}`}><Building2 size={14}/>{message.business_name}</p>
          <p className="city" data-testid={`profile-card-city-${message.id}`}><MapPin size={13}/>{message.city_regency || message.province}</p>
          <blockquote data-testid={`profile-card-message-${message.id}`}>“{message.message}”</blockquote>
        </div>
      </button>
      <div className="card-actions">
        <button className={liked ? "liked" : ""} onClick={like} data-testid={`profile-card-like-${message.id}`} aria-label="Dukung aspirasi"><Heart size={18} fill={liked ? "currentColor" : "none"}/><span>{likes}</span></button>
        <button onClick={() => onOpen(message)} data-testid={`profile-card-detail-${message.id}`} aria-label="Lihat pesan lengkap"><MessageCircle size={18}/><span>Detail</span></button>
        <button onClick={share} data-testid={`profile-card-share-${message.id}`} aria-label="Bagikan ke WhatsApp"><Share2 size={18}/><span>Bagikan</span></button>
      </div>
    </article>
  );
};