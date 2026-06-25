import { useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import '../assets/styles/RegisterCashPayment.css';

export default function RegisterCashPaymentPage() {

  const [email, setEmail] = useState("");
  const [results, setResults] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [monto, setMonto] = useState("");

  const getItemKey = (r) => r.tipo === "suspension" ? `susp-${r.id_suspension}` : `res-${r.id_reserva}`;

  const buscarReservas = async () => {
    try {
      const res = await axios.post("/api/revisar-reserva", { email });
      setResults(res.data);
      setMonto(res.data[0].monto_deuda);
      setSelectedItem(null);
    } catch (err) {
      console.error(err);
      setResults([]);
      toast.error(err.response?.data?.mensaje || "Error al buscar deudas");
    }
  };

  const registrarPago = async () => {
    if (!selectedItem) return;

    try {
      if (selectedItem.tipo === "suspension") {
        await axios.post("/api/registrar_pago_suspension", {
          id_suspension: selectedItem.id_suspension,
          monto: parseFloat(monto),
        });
      } else {
        await axios.post("/api/registrar_pago_efectivo", {
          id_reserva: selectedItem.id_reserva,
          monto: parseFloat(monto),
        });
      }

      toast.success("Pago registrado con éxito");

      setResults((prev) => prev.filter((r) => getItemKey(r) !== getItemKey(selectedItem)));
      setSelectedItem(null);
      setMonto("");

    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.mensaje || "Error al registrar pago");
    }
  };

  const getLabel = (r) => {
    if (r.tipo === "turno") return `Turno: ${r.disciplina} - ${r.fecha} - ${r.hora}`;
    if (r.tipo === "clase") return `Clase mensual: ${r.disciplina}`;
    if (r.tipo === "suspension") return `Suspensión: ${r.disciplina} - ${r.fecha === "Mensual" ? "Mensual" : r.fecha} ${r.hora}hs`;
    return r.disciplina;
  };

  return (
    <div className="cash-page">

      <h1 className="cash-title">Registrar Pago en Efectivo</h1>

      <div className="cash-form">
        <input
          className="cash-input"
          placeholder="Email del cliente"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button
          className="cash-button primary"
          onClick={buscarReservas}
          disabled={!email.trim()}
        >
          Buscar deudas
        </button>
      </div>

      <div className="cash-results">
        {results.map((r) => (
          <label key={getItemKey(r)} className="cash-result-item">
            <input
              type="radio"
              checked={selectedItem ? getItemKey(selectedItem) === getItemKey(r) : false}
              onChange={() => { setSelectedItem(r); setMonto(r.monto_deuda); }}
            />
            <div className="cash-result-info">
              <span className="cash-result-title">{getLabel(r)}</span>
              <span className="cash-result-sub">Deuda: ${r.monto_deuda}</span>
            </div>
          </label>
        ))}
      </div>

      {selectedItem && (
        <div className="cash-payment">
          <h3>Registrar pago</h3>
          <p className="cash-debt"><strong>{getLabel(selectedItem)}</strong></p>
          <p className="cash-debt">Monto deuda: <strong>${selectedItem.monto_deuda}</strong></p>
          <button className="cash-button success" onClick={registrarPago}>
            Registrar Pago Efectivo
          </button>
        </div>
      )}

    </div>
  );
}
