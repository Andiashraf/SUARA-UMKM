import { useEffect, useState } from "react";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { FanWall } from "@/components/FanWall";
import { PortalSections } from "@/components/PortalSections";
import { SubmitModal } from "@/components/SubmitModal";
import { Footer } from "@/components/Footer";
import "@/App.css";

export const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function App() {
  const [submitOpen, setSubmitOpen] = useState(false);
  const [stats, setStats] = useState({ voices: 5000, provinces: 38, organizations: 34, supports: 12026 });
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    axios.get(`${API}/fan-wall/stats`).then(({ data }) => setStats((prev) => ({ ...prev, ...data }))).catch(() => {});
  }, [refreshKey]);

  return (
    <div className="portal-shell" data-testid="harnas-umkm-portal">
      <Navbar onSubmit={() => setSubmitOpen(true)} />
      <main>
        <Hero stats={stats} onSubmit={() => setSubmitOpen(true)} />
        <FanWall onSubmit={() => setSubmitOpen(true)} refreshKey={refreshKey} />
        <PortalSections />
      </main>
      <Footer onSubmit={() => setSubmitOpen(true)} />
      <SubmitModal open={submitOpen} onClose={() => setSubmitOpen(false)} onSubmitted={() => setRefreshKey((key) => key + 1)} />
      <Toaster richColors position="top-center" />
    </div>
  );
}