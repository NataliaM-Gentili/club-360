import { useState, useEffect } from 'react';
import '../assets/styles/HistorialPagos.css';

const TIPO_PAGO_LABEL = {
    tarjeta:  'Tarjeta',
    efectivo: 'Efectivo',
    credito:  'Crédito',
};

const TIPO_PAGO_CLASS = {
    tarjeta:  'badge--tarjeta',
    efectivo: 'badge--efectivo',
    credito:  'badge--credito',
};

const TIPO_RESERVA_LABEL = {
    clase: 'Mensual',
    turno: 'Turno',
};

const TIPO_RESERVA_CLASS = {
    clase: 'badge--mensual',
    turno: 'badge--turno',
};

export default function HistorialPagosPage() {
    const [session,    setSession]    = useState(null);
    const [pagos,      setPagos]      = useState([]);
    const [cargando,   setCargando]   = useState(true);
    const [error,      setError]      = useState(null);
    const [filtroTipo, setFiltroTipo] = useState('');

    useEffect(() => {
        fetch('/api/auth/status', { credentials: 'include' })
            .then(res => res.json())
            .then(data => setSession(data))
            .catch(() => setSession({ loggedIn: false }));
    }, []);

    useEffect(() => {
        if (!session) return;
        if (!session.loggedIn) { setCargando(false); return; }

        fetch('/api/historial-pagos', { credentials: 'include' })
            .then(res => {
                if (!res.ok) throw new Error('Error al obtener el historial');
                return res.json();
            })
            .then(data => { setPagos(data.pagos || []); setCargando(false); })
            .catch(err  => { setError(err.message);    setCargando(false); });
    }, [session]);

    const pagosFiltrados = filtroTipo
        ? pagos.filter(p => p.tipo_pago === filtroTipo)
        : pagos;

    const totalAbonado = pagosFiltrados
        .reduce((acc, p) => acc + parseFloat(p.monto || 0), 0);

    /* ── helpers de presentación ── */
    const detallePago = (p) => {
        if (p.tipo_pago === 'tarjeta' && p.numero_tarjeta)
            return `•••• ${p.numero_tarjeta}`;
        return null;
    };

    return (
        <div className="historialContainer">
            <h1 className="historialTitle">Historial de pagos</h1>

            {/* Filtro */}
            <div className="historialFiltros">
                <select value={filtroTipo} onChange={e => setFiltroTipo(e.target.value)}>
                    <option value="">Todos los métodos</option>
                    <option value="tarjeta">Tarjeta</option>
                    <option value="efectivo">Efectivo</option>
                    <option value="credito">Crédito</option>
                </select>
            </div>

            {cargando ? (
                <p className="sinResultados">Cargando...</p>
            ) : error ? (
                <p className="sinResultados">{error}</p>
            ) : pagosFiltrados.length === 0 ? (
                <p className="sinResultados">No hay pagos realizados aún.</p>
            ) : (
                <>
                    {/* Banner total */}
                    <div className="resumenBanner">
                        <span className="resumenLabel">
                            Total abonado{filtroTipo ? ` · ${TIPO_PAGO_LABEL[filtroTipo]}` : ''}
                        </span>
                        <span className="resumenMonto">${totalAbonado.toFixed(2)}</span>
                    </div>

                    <table className="historialTable">
                        <thead>
                            <tr>
                                <th>Tipo</th>
                                <th>Fecha</th>
                                <th>Día</th>
                                <th>Horario</th>
                                <th>Método</th>
                                <th>Monto</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pagosFiltrados.map((pago, idx) => (
                                <tr key={pago.id_reserva ?? idx}>
                                    <td className="tdTipo">
                                        <span className={`tipoReservaBadge ${TIPO_RESERVA_CLASS[pago.tipo_reserva] ?? ''}`}>
                                            {TIPO_RESERVA_LABEL[pago.tipo_reserva] ?? pago.tipo_reserva}
                                        </span>
                                    </td>
                                    <td className="tdFecha">{pago.fecha_turno ?? '-'}</td>
                                    <td className="tdDia">{pago.dia ?? '—'}</td>
                                    <td className="tdHora">{pago.hora ?? '—'}</td>
                                    <td>
                                        <div className="metodoCell">
                                            <span className={`tipoBadge ${TIPO_PAGO_CLASS[pago.tipo_pago] ?? ''}`}>
                                                {TIPO_PAGO_LABEL[pago.tipo_pago] ?? pago.tipo_pago}
                                            </span>
                                            {detallePago(pago) && (
                                                <span className="numeroTarjeta">{detallePago(pago)}</span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="tdMonto">${parseFloat(pago.monto).toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </>
            )}
        </div>
    );
}
