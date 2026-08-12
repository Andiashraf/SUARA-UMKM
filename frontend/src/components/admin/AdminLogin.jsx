import { useState } from "react";
import { ArrowLeft, Loader2, LockKeyhole } from "lucide-react";

export const AdminLogin = ({ onLogin, loading, error }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const submit = (event) => { event.preventDefault(); onLogin(email, password); };
  return <main className="admin-login-page" data-testid="admin-login-page">
    <div className="admin-login-brand"><img src="/abdsi_logo.png" alt="ABDSI Logo" className="brand-logo" /><div><b>HARNAS UMKM</b><small>PUSAT MODERASI • ABDSI</small></div></div>
    <section className="admin-login-card">
      <div className="admin-lock"><LockKeyhole/></div>
      <div className="eyebrow violet">Area Terbatas</div>
      <h1 data-testid="admin-login-heading">Masuk sebagai moderator</h1>
      <p>Kelola suara UMKM dengan aman, tertib, dan bertanggung jawab.</p>
      <form onSubmit={submit} data-testid="admin-login-form">
        <label><span>Email admin</span><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="username" required data-testid="admin-email-input"/></label>
        <label><span>Password</span><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required data-testid="admin-password-input"/></label>
        {error && <div className="admin-login-error" data-testid="admin-login-error">{error}</div>}
        <button className="button primary" disabled={loading} data-testid="admin-login-submit-button">{loading ? <><Loader2 className="spin"/> Memverifikasi…</> : <>Masuk ke dashboard</>}</button>
      </form>
      <a href="/" data-testid="admin-back-to-portal-link"><ArrowLeft/> Kembali ke portal</a>
    </section>
  </main>;
};