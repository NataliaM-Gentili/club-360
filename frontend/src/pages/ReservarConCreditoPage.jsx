import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import "../assets/styles/ListarTurnos.css";

const LABELS = {
  futbol: "Fútbol", padel: "Pádel", paddle: "Pádel",
  voley: "Vóley", basquet: "Básquet",
};

export default function ReservarConCreditoPage() {
  const { disciplina } = useParams();

  const [turnos, setTurnos] = useState([]);
  const [cargando, setCargando] = useState(true);

  const label = LABELS[disciplina] || disciplina;

  useEffect(() => {
    fetch(`/api/turnos_credito/${disciplina}`, { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setTurnos(data.turnos || []))
      .catch(() => toast.error("No se pudieron cargar los turnos."))
      .finally(() => setCargando(false));
  }, [disciplina]);

  const reservar = async (id_turno) => {
    try {
      const res = await fetch("/api/reservar_turno_credito", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ id_turno, disciplina }),
      });
      const data = await res.json();

      if (res.ok) {
        toast.success(data.mensaje);
        setTurnos((prev) =>
          prev.map((t) =>
            t.id_turno === id_turno
              ? { ...t, disponibles: t.disponibles - 1, reservado: true }
              : t
          )
        );
      } else {
        toast.error(data.mensaje || "Error al reservar.");
      }
    } catch {
      toast.error("No se pudo conectar con el servidor.");
    }
  };

  return (
    <div className="listarTurnosContainer">
      <h1 className="listarTurnosTitle">Reservar con crédito — {label}</h1>

      {cargando ? (
        <p className="sinResultados">Cargando turnos...</p>
      ) : turnos.length === 0 ? (
        <p className="sinResultados" style={{ marginTop: "100px", fontSize: "18px" }}>
          No hay turnos disponibles para {label}.
        </p>
      ) : (
        <div className="resultadosContainer">
          <table className="turnosTable">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Día</th>
                <th>Hora</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {turnos.map((t) => (
                <tr key={t.id_turno}>
                  <td>{t.fecha}</td>
                  <td>{t.dia}</td>
                  <td>{t.hora}hs</td>
                  <td>
                    {!t.reservado && (
                      <button
                        className="reservarBtn"
                        onClick={() => reservar(t.id_turno)}
                      >
                        Reservar con crédito
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
