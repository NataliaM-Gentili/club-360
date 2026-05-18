import { useState } from "react";
import axios from "axios";

import { toast, ToastContainer } from "react-toastify";
import '../assets/styles/RegisterCashPayment.css'

export default function RegisterCashPaymentPage() {

  const [email, setEmail] = useState("");
  const [disciplina, setDisciplina] = useState("");
  const [fecha, setFecha] = useState("");
  const [hora, setHora] = useState("");

  const [results, setResults] = useState([]);
  const [selectedReserva, setSelectedReserva] = useState(null);
  const [monto, setMonto] = useState("");

  const buscarReservas = async () => {
    try {
      const res = await axios.post("/api/revisar-reserva", {
        email,
        disciplina,
        fecha,
        hora
      });

      setResults(res.data);
      setSelectedReserva(null);

    } catch (err) {
      console.error(err);
      setResults([]);
      toast.error(err.response?.data?.mensaje || "Error al buscar reservas");
    }
  };

  const registrarPago = async () => {
    if (!selectedReserva) return;

    try {
        await axios.post("/api/registrar_pago_efectivo", {
        id_reserva: selectedReserva.id_reserva,
        monto: parseFloat(monto)
        });

        toast.success("Pago registrado correctamente");

        // ✅ OPTIMISTIC UI UPDATE (remove paid reservation instantly)
        setResults((prev) =>
        prev.filter((r) => r.id_reserva !== selectedReserva.id_reserva)
        );

        setSelectedReserva(null);
        setMonto("");

    } catch (err) {
        console.error(err);
        toast.error(err.response?.data?.mensaje || "Error al registrar pago");
    }
    };

  return (
    <div className="cash-page">

    <h1 className="cash-title">Registrar Pago en Efectivo</h1>

    {/* SEARCH FORM */}
    <div className="cash-form">

        <input
        className="cash-input"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        />

        <input
        className="cash-input"
        placeholder="Disciplina"
        value={disciplina}
        onChange={(e) => setDisciplina(e.target.value)}
        />

        <input
        className="cash-input"
        type="date"
        value={fecha}
        onChange={(e) => setFecha(e.target.value)}
        />

        <input
        className="cash-input"
        type="time"
        value={hora}
        onChange={(e) => setHora(e.target.value)}
        />

        <button className="cash-button primary" onClick={buscarReservas}>
        Buscar reservas
        </button>

    </div>

    {/* RESULTS */}
    <div className="cash-results">

        {results.map((r) => (
        <label key={r.id_reserva} className="cash-result-item">

            <input
            type="radio"
            checked={selectedReserva?.id_reserva === r.id_reserva}
            onChange={() => setSelectedReserva(r)}
            />

            <div className="cash-result-info">
            <span className="cash-result-title">
                Turno / Reserva: {r.disciplina} - {r.fecha_turno} - {r.hora}
            </span>
            <span className="cash-result-sub">
                Deuda: ${r.monto_deuda}
            </span>
            </div>

        </label>
        ))}

    </div>

    {/* PAYMENT */}
    {selectedReserva && (
        <div className="cash-payment">

        <h3>Registrar pago</h3>

        <p className="cash-debt">
            Monto deuda: <strong>${selectedReserva.monto_deuda}</strong>
        </p>

        <input
            className="cash-input"
            placeholder="Monto ingresado"
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
        />

        <button className="cash-button success" onClick={registrarPago}>
            Registrar Pago Efectivo
        </button>

        </div>
    )}

    </div>
  );
}