import { useState } from "react";
import { Menu, PenLine, X } from "lucide-react";

const links = [
  ["Suara UMKM", "#fan-wall"], ["Sejarah", "#sejarah"], ["ABDSI", "#abdsi"],
  ["TNP IV", "#tnp"], ["Produk UMKM", "#showcase"],
];

export const Navbar = ({ onSubmit }) => {
  const [open, setOpen] = useState(false);
  return (
    <header className="main-nav" data-testid="main-navigation">
      <div className="nav-inner">
        <a href="#beranda" className="brand-lockup" data-testid="brand-home-link">
          <img src="/abdsi_logo.png" alt="ABDSI Logo" className="brand-logo" />
          <span><b>HARNAS UMKM</b><small>ABDSI • 2026</small></span>
        </a>
        <nav className="desktop-links" aria-label="Navigasi utama">
          {links.map(([label, href]) => <a key={href} href={href} data-testid={`nav-${href.slice(1)}-link`}>{label}</a>)}
        </nav>
        <button className="nav-cta" onClick={onSubmit} data-testid="navbar-submit-aspiration-button"><PenLine size={17} /> Kirim Aspirasi</button>
        <button className="menu-button" onClick={() => setOpen(!open)} aria-label="Buka menu" data-testid="mobile-menu-button">{open ? <X /> : <Menu />}</button>
      </div>
      {open && <nav className="mobile-links" aria-label="Navigasi seluler" data-testid="mobile-navigation-menu">
        {links.map(([label, href]) => <a key={href} href={href} onClick={() => setOpen(false)} data-testid={`mobile-nav-${href.slice(1)}-link`}>{label}</a>)}
        <button onClick={() => { setOpen(false); onSubmit(); }} data-testid="mobile-submit-aspiration-button"><PenLine size={17} /> Kirim Aspirasi</button>
      </nav>}
    </header>
  );
};