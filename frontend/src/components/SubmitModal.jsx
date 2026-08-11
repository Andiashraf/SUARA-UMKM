import { useEffect, useState } from "react";
import axios from "axios";
import { Camera, CheckCircle2, Loader2, Send, X } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import imageCompression from "browser-image-compression";
import { provinces, roles } from "@/data/content";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const initial = { full_name: "", business_name: "", role: "Pelaku UMKM", province: "Kalimantan Barat", city_regency: "", message: "", avatar_url: "", avatar_path: null };

export const SubmitModal = ({ open, onClose, onSubmitted }) => {
  const [form, setForm] = useState(initial);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [photo, setPhoto] = useState(null);
  const [preview, setPreview] = useState("");
  useEffect(() => { if (!open) { setTimeout(() => { setForm(initial); setErrors({}); setSuccess(false); setPhoto(null); setPreview(""); }, 250); } }, [open]);
  if (!open) return null;
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));
  const upload = (file) => {
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) { toast.error("Gunakan foto JPG, PNG, atau WebP."); return; }
    if (file.size > 8_000_000) { toast.error("Ukuran foto awal maksimal 8 MB."); return; }
    setPhoto(file);
    const reader = new FileReader(); reader.onload = () => setPreview(reader.result); reader.readAsDataURL(file);
  };
  const submit = async (event) => {
    event.preventDefault();
    const next = {};
    if (form.full_name.trim().length < 2) next.full_name = "Tuliskan nama lengkap.";
    if (form.business_name.trim().length < 2) next.business_name = "Tuliskan nama usaha atau organisasi.";
    if (form.message.trim().length < 20) next.message = "Aspirasi minimal 20 karakter agar pesannya bermakna.";
    setErrors(next); if (Object.keys(next).length) return;
    setLoading(true);
    try {
      let payload = { ...form };
      if (photo) {
        const compressed = await imageCompression(photo, { maxSizeMB: .95, maxWidthOrHeight: 1200, useWebWorker: true, fileType: photo.type });
        const uploadData = new FormData();
        uploadData.append("file", compressed, photo.name);
        const { data } = await axios.post(`${API}/uploads/avatar`, uploadData);
        payload = { ...payload, avatar_url: data.avatar_url, avatar_path: data.avatar_path };
      }
      await axios.post(`${API}/fan-wall`, payload); setSuccess(true); onSubmitted(); toast.success("Aspirasi berhasil dikirim untuk moderasi.");
    }
    catch (error) {
      const detail = error.response?.data?.detail;
      toast.error(typeof detail === "string" ? detail : detail?.[0]?.msg || "Aspirasi belum berhasil dikirim.");
    }
    finally { setLoading(false); }
  };
  return <div className="modal-backdrop submit-backdrop" onMouseDown={onClose} data-testid="submit-aspiration-modal">
    <motion.div className="submit-modal" onMouseDown={(e) => e.stopPropagation()} initial={{ opacity: 0, y: 32, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} role="dialog" aria-modal="true" aria-labelledby="submit-title">
      <button className="modal-close" onClick={onClose} data-testid="submit-modal-close-button" aria-label="Tutup form"><X/></button>
      {success ? <div className="success-state" data-testid="submit-success-state"><CheckCircle2/><span>Aspirasi diterima</span><h2>Terima kasih telah ikut bersuara.</h2><p>Pesan Anda akan tampil setelah proses moderasi.</p><button className="button primary" onClick={onClose} data-testid="submit-success-close-button">Kembali ke Fan Wall</button></div>
      : <><header className="submit-header"><div className="eyebrow gold">Suara Anda berarti</div><h2 id="submit-title" data-testid="submit-form-heading">Kirim Aspirasi UMKM</h2><p>Satu pesan tulus dapat membuka percakapan dan perubahan.</p></header>
      <form onSubmit={submit} className="aspiration-form" data-testid="submit-aspiration-form">
        <label className={errors.full_name ? "field error" : "field"}><span>Nama lengkap *</span><input value={form.full_name} onChange={(e) => update("full_name", e.target.value)} placeholder="Nama Anda" data-testid="aspiration-full-name-input"/>{errors.full_name && <small data-testid="full-name-error">{errors.full_name}</small>}</label>
        <label className={errors.business_name ? "field error" : "field"}><span>Usaha / organisasi *</span><input value={form.business_name} onChange={(e) => update("business_name", e.target.value)} placeholder="Nama usaha atau organisasi" data-testid="aspiration-business-input"/>{errors.business_name && <small data-testid="business-name-error">{errors.business_name}</small>}</label>
        <label className="field"><span>Peran *</span><select value={form.role} onChange={(e) => update("role", e.target.value)} data-testid="aspiration-role-select">{roles.filter((r) => r !== "Semua").map((r) => <option key={r}>{r}</option>)}</select></label>
        <label className="field"><span>Provinsi *</span><select value={form.province} onChange={(e) => update("province", e.target.value)} data-testid="aspiration-province-select">{provinces.filter((p) => p !== "Semua Provinsi").map((p) => <option key={p}>{p}</option>)}</select></label>
        <label className="field span-two"><span>Kota / Kabupaten</span><input value={form.city_regency} onChange={(e) => update("city_regency", e.target.value)} placeholder="Contoh: Kota Pontianak" data-testid="aspiration-city-input"/></label>
        <label className={errors.message ? "field message-field error span-two" : "field message-field span-two"}><span>Aspirasi Anda *</span><textarea value={form.message} onChange={(e) => update("message", e.target.value)} placeholder="Apa harapan Anda untuk masa depan UMKM Indonesia?" maxLength={800} data-testid="aspiration-message-textarea"/><em>{form.message.length}/800</em>{errors.message && <small data-testid="message-error">{errors.message}</small>}</label>
        <label className="photo-field span-two" data-testid="aspiration-photo-upload"><input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => upload(e.target.files[0])} data-testid="aspiration-photo-input"/><span>{preview ? <img src={preview} alt="Pratinjau foto profil"/> : <Camera/>}<b>{preview ? "Ganti foto" : "Tambahkan foto profil"}</b><small>JPG, PNG, atau WebP • otomatis dikompresi hingga 1 MB</small></span></label>
        <button className="button primary submit-final span-two" disabled={loading} data-testid="aspiration-submit-button">{loading ? <><Loader2 className="spin"/> Mengirim…</> : <>Kirim untuk Indonesia <Send size={18}/></>}</button>
      </form></>}
    </motion.div>
  </div>;
};