import { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import ModalDialog from "./ModalDialog";

export default function TurnosPendientes() {
    const [turnos, setTurnos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [seleccionado, setSeleccionado] = useState(null);
    const navigate = useNavigate();

    const cargar = async () => {
        try {
            setLoading(true);
            const { data } = await axios.get("/api/cliente/mis_turnos_pendientes", { withCredentials: true });
            setTurnos(data);
       } catch (e) {
            console.error("pendientes:", e?.response?.status, e?.response?.config?.url, e?.response?.data);
            toast.error("No se pudieron cargar los turnos pendientes.");
        
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { cargar(); }, []);

    const confirmarCancelacion = async () => {
        if (!seleccionado) return;
        const sel = seleccionado;
        try {
            const { data } = await axios.post(
                `/api/cancelar_turno/${sel.id_reserva}`,
                { id_turno: sel.id_turno },
                { withCredentials: true }
            );
            toast.success(data.mensaje || "Turno cancelado");
            if (data.detalle) toast.info(data.detalle);
            if (data.reintegro) toast.info(data.reintegro);

            await cargar();
        } catch (e) {
            toast.error(e?.response?.data?.mensaje || "No se pudo cancelar el turno.");
        } finally {
            setSeleccionado(null);
        }
    };

    if (loading) return <p>Cargando turnos…</p>;
    if (turnos.length === 0) return <p className="sinTurnos">No tenés turnos pendientes.</p>;

    return (
        <div className="turnosPendientes">
            <h2>Turnos pendientes</h2>
            <ul className="listaTurnos">
                {turnos.map((t) => (
                    <li key={`${t.id_reserva}-${t.id_turno}`} className="turnoCard">
                        <div className="turnoInfo">
                            <strong>{t.disciplina}</strong>
                            <span>{t.fecha} · {t.hora} hs</span>
                            <span className="turnoTipo">
                                {t.tipo === "abono" ? "Abono mensual" : "Turno suelto"}
                            </span>
                        </div>
                        <button className="cancelarBtn" onClick={() => setSeleccionado(t)}>
                            Cancelar turno
                        </button>
                    </li>
                ))}
            </ul>

            <ModalDialog
                open={!!seleccionado}
                onClose={() => setSeleccionado(null)}
                title="Cancelar turno"
                message={seleccionado
                    ? `¿Seguro que querés cancelar ${seleccionado.disciplina} del ${seleccionado.fecha} a las ${seleccionado.hora} hs?`
                    : ""}
                primaryText="Sí, cancelar"
                secondaryText="Volver"
                onPrimary={confirmarCancelacion}
                onSecondary={() => setSeleccionado(null)}
            />
        </div>
    );
}