import { Check, MapPin, ShieldX, Sparkles, Star, Trash2 } from "lucide-react";

const labels = { pending: "Menunggu", approved: "Disetujui", rejected: "Ditolak" };

export const AdminMessageCard = ({ message, onAction, busy }) => <article className="moderation-card" data-testid={`moderation-card-${message.id}`}>
  <div className="moderation-avatar">
    {message.avatar_url ? <img src={message.avatar_url} alt={`Foto ${message.full_name}`}/> : <div>{message.full_name.slice(0, 2).toUpperCase()}</div>}
    {message.is_featured && <span data-testid={`featured-badge-${message.id}`}><Star fill="currentColor"/> Unggulan</span>}
  </div>
  <div className="moderation-content">
    <div className="moderation-topline"><span className={`status-badge ${message.status}`} data-testid={`moderation-status-${message.id}`}>{labels[message.status]}</span><time>{new Date(message.created_at).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}</time></div>
    <h3 data-testid={`moderation-name-${message.id}`}>{message.full_name}</h3>
    <p className="moderation-business">{message.business_name} • {message.role}</p>
    <p className="moderation-location"><MapPin/>{message.city_regency || message.province}, {message.province}</p>
    <blockquote data-testid={`moderation-message-${message.id}`}>“{message.message}”</blockquote>
    <div className="moderation-actions">
      {message.status !== "approved" && <button className="approve" onClick={() => onAction(message.id, { status: "approved" })} disabled={busy} data-testid={`approve-message-${message.id}`}><Check/> Setujui</button>}
      {message.status !== "rejected" && <button className="reject" onClick={() => onAction(message.id, { status: "rejected" })} disabled={busy} data-testid={`reject-message-${message.id}`}><ShieldX/> Tolak</button>}
      {message.status === "approved" && <button className={message.is_featured ? "feature active" : "feature"} onClick={() => onAction(message.id, { is_featured: !message.is_featured })} disabled={busy} data-testid={`feature-message-${message.id}`}><Sparkles/> {message.is_featured ? "Lepas unggulan" : "Jadikan unggulan"}</button>}
      <button className="delete" onClick={() => onAction(message.id, null, true)} disabled={busy} data-testid={`delete-message-${message.id}`}><Trash2/> Hapus</button>
    </div>
  </div>
</article>;