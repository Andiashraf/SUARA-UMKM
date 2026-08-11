import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { Archive, CheckCircle2, Clock3, ExternalLink, LogOut, RefreshCw, Search, ShieldCheck, Sparkles, XCircle } from "lucide-react";
import { toast } from "sonner";
import { AdminLogin } from "@/components/admin/AdminLogin";
import { AdminMessageCard } from "@/components/admin/AdminMessageCard";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const tabs = [["pending", "Antrean"], ["approved", "Disetujui"], ["rejected", "Ditolak"], ["all", "Semua"]];

export const ModerationDashboard = () => {
  const [token, setToken] = useState(() => sessionStorage.getItem("moderation_token") || "");
  const [messages, setMessages] = useState([]);
  const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, featured: 0 });
  const [status, setStatus] = useState("pending");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [busyId, setBusyId] = useState("");
  const [loginError, setLoginError] = useState("");
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const logout = useCallback(() => { sessionStorage.removeItem("moderation_token"); setToken(""); }, []);
  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [list, count] = await Promise.all([
        axios.get(`${API}/admin/messages`, { headers, params: { status, search: search.trim() } }),
        axios.get(`${API}/admin/stats`, { headers }),
      ]);
      setMessages(list.data); setStats(count.data);
    } catch (error) {
      if (error.response?.status === 401) logout(); else toast.error("Data moderasi belum dapat dimuat.");
    } finally { setLoading(false); }
  }, [token, status, search, logout, headers]);

  useEffect(() => { const timer = setTimeout(load, 250); return () => clearTimeout(timer); }, [load]);

  const login = async (email, password) => {
    setLoading(true); setLoginError("");
    try { const { data } = await axios.post(`${API}/admin/login`, { email, password }); sessionStorage.setItem("moderation_token", data.access_token); setToken(data.access_token); toast.success("Selamat datang di pusat moderasi."); }
    catch (error) { setLoginError(error.response?.data?.detail || "Login belum berhasil."); }
    finally { setLoading(false); }
  };

  const action = async (id, payload, shouldDelete = false) => {
    if (shouldDelete && !window.confirm("Hapus aspirasi ini secara permanen?")) return;
    setBusyId(id);
    try {
      if (shouldDelete) await axios.delete(`${API}/admin/messages/${id}`, { headers });
      else await axios.patch(`${API}/admin/messages/${id}`, payload, { headers });
      toast.success(shouldDelete ? "Aspirasi dihapus." : "Status aspirasi diperbarui.");
      await load();
    } catch (error) { toast.error(error.response?.data?.detail || "Perubahan belum berhasil disimpan."); }
    finally { setBusyId(""); }
  };

  if (!token) return <AdminLogin onLogin={login} loading={loading} error={loginError}/>;
  return <div className="admin-shell" data-testid="moderation-dashboard">
    <header className="admin-header"><div className="admin-title"><span className="brand-mark">12</span><div><b>Pusat Moderasi</b><small>HARNAS UMKM • ABDSI 2026</small></div></div><div className="admin-header-actions"><a href="/" target="_blank" data-testid="admin-view-portal-link">Lihat portal <ExternalLink/></a><button onClick={logout} data-testid="admin-logout-button"><LogOut/> Keluar</button></div></header>
    <main className="admin-main">
      <section className="admin-welcome"><div><div className="eyebrow violet"><ShieldCheck/> Ruang Kendali</div><h1 data-testid="moderation-heading">Jaga kualitas setiap suara.</h1><p>Tinjau aspirasi sebelum tampil di Fan Wall nasional.</p></div><button onClick={load} className="admin-refresh" data-testid="moderation-refresh-button"><RefreshCw className={loading ? "spin" : ""}/> Perbarui</button></section>
      <section className="admin-stats" data-testid="moderation-stats"><article><Clock3/><span>Menunggu</span><b>{stats.pending}</b></article><article><CheckCircle2/><span>Disetujui</span><b>{stats.approved}</b></article><article><XCircle/><span>Ditolak</span><b>{stats.rejected}</b></article><article><Sparkles/><span>Unggulan</span><b>{stats.featured}</b></article></section>
      <section className="moderation-workspace">
        <div className="moderation-toolbar"><div className="moderation-tabs" role="tablist">{tabs.map(([value, label]) => <button key={value} className={status === value ? "active" : ""} onClick={() => setStatus(value)} data-testid={`moderation-tab-${value}`}>{label}{value !== "all" && <span>{stats[value]}</span>}</button>)}</div><label className="admin-search"><Search/><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Cari nama, usaha, atau isi pesan…" data-testid="moderation-search-input"/></label></div>
        <div className="moderation-list" data-testid="moderation-message-list">{loading ? <div className="admin-loading"><RefreshCw className="spin"/> Memuat antrean…</div> : messages.length ? messages.map((message) => <AdminMessageCard key={message.id} message={message} onAction={action} busy={busyId === message.id}/>) : <div className="admin-empty"><Archive/><h3>Tidak ada aspirasi di bagian ini</h3><p>Antrean akan muncul ketika ada kiriman baru.</p></div>}</div>
      </section>
    </main>
  </div>;
};