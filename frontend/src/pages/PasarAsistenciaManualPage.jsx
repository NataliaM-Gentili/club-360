import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import "../assets/styles/PasarAsistenciaManual.css";

export default function PasarAsistenciaManualPage() {
  const navigate = useNavigate();

  const [turnos, setTurnos] = useState([]);
  const [cargandoTurnos, setCargandoTurnos] = useState(true);
  const [idTurno, setIdTurno] = useState("");
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    fetch("/api/turnos_hoy", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setTurnos(data.turnos || []))
      .catch(() => toast.error("No se pudieron cargar los turnos de hoy."))
      .finally(() => setCargandoTurnos(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!idTurno || !email.trim()) return;

    setEnviando(true);
    try {
      const res = await fetch("/api/asistencia/registrar_manual", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: email.trim(), id_turno: Number(idTurno) }),
      });
      const data = await res.json();

      if (data.ok) {
        toast.success(data.mensaje);
        setEmail("");
      } else {
        toast.error(data.mensaje || "Ocurrió un error inesperado.");
      }
    } catch {
      toast.error("No se pudo conectar con el servidor.");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="pam-page">
      <div className="pam-card">

        <div className="pam-header">
          <span className="pam-logo-tag">Club 360</span>
          <h1 className="pam-titulo">Pasar asistencia manual</h1>
        </div>

        <form className="pam-body" onSubmit={handleSubmit}>
          <div className="pam-campo">
            <label className="pam-label" htmlFor="turno">Turno de hoy</label>

            {cargandoTurnos ? (
              <p className="pam-instruccion">Cargando turnos…</p>
            ) : turnos.length === 0 ? (
              <p className="pam-instruccion">No hay turnos programados para hoy.</p>
            ) : (
              <select
                id="turno"
                className="pam-select"
                value={idTurno}
                onChange={(e) => setIdTurno(e.target.value)}
                required
              >
                <option value="">Seleccionar turno…</option>
                {turnos.map((t) => (
                  <option key={t.id_turno} value={t.id_turno}>
                    {t.disciplina.charAt(0).toUpperCase() + t.disciplina.slice(1)} · {t.dia} {t.hora}hs
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="pam-campo">
            <label className="pam-label" htmlFor="email">Email del cliente</label>
            <input
              id="email"
              type="email"
              className="pam-input"
              placeholder="cliente@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="pam-btn-grupo">
            <button type="button" className="pam-btn pam-btn--secondary" onClick={() => navigate(-1)}>
              Volver
            </button>
            <button
              type="submit"
              className="pam-btn pam-btn--primary"
              disabled={enviando || !idTurno || !email.trim()}
            >
              {enviando ? "Registrando…" : "Pasar asistencia"}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}