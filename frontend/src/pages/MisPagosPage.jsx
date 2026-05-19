import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../assets/styles/MisPagos.css';

const ICONOS_DISCIPLINA = {
    futbol: '⚽',
    padel: '🎾',
    paddle: '🎾',
    voley: '🏐',
    basquet: '🏀',
};

export default function MisPagos() {
    const navigate = useNavigate();
    const [pagos, setPagos] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPagos = async () => {
            try {
                const authRes = await fetch('/api/auth/status', { credentials: 'include' });
                const authData = await authRes.json();

                if (!authData.loggedIn || !authData.email) {
                    navigate('/login');
                    return;
                }

                const res = await fetch('/api/revisar-reserva', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ email: authData.email }),
                });

                if (res.status === 404) {
                    setPagos([]);
                    return;
                }

                const data = await res.json();
                setPagos(data);
            } catch (err) {
                setError('No se pudieron cargar los pagos pendientes.');
            } finally {
                setCargando(false);
            }
        };

        fetchPagos();
    }, []);

    const handlePagar = (pago) => {
        localStorage.setItem("reserva_id", pago.id_reserva);
        localStorage.setItem("user_id", pago.id_cliente);
        navigate(`/pagar/${pago.id_reserva}`);
    };

    const getIcono = (disciplina) => {
        return ICONOS_DISCIPLINA[disciplina?.toLowerCase()] || '🏃';
    };

    return (
        <div className="misPagosContainer">
            <h1 className="misPagosTitle">Mis Pagos Pendientes</h1>

            {cargando && <p className="misPagosEstado">Cargando...</p>}
            {error && <p className="misPagosEstado misPagosError">{error}</p>}

            {!cargando && !error && pagos.length === 0 && (
                <p className="misPagosEstado">¡No tenés pagos pendientes! 🎉</p>
            )}

            {!cargando && !error && pagos.length > 0 && (
                <div className="pagosGrid">
                    {pagos.map((pago) => (
                        <div className="pagoCard" key={pago.id_reserva}>

                            {/* BADGE TIPO */}
                            <span className={`tipoBadge ${pago.tipo === 'clase' ? 'tipoBadgeClase' : 'tipoBadgeTurno'}`}>
                                {pago.tipo === 'clase' ? 'Abono (turno fijo)' : 'Clase suelta'}
                            </span>

                            {/* ICONO Y DISCIPLINA */}
                            <div className="pagoHeader">
                                <div className="pagoIcono">{getIcono(pago.disciplina)}</div>
                                <h2 className="pagoDisciplina">
                                    {pago.disciplina.charAt(0).toUpperCase() + pago.disciplina.slice(1)}
                                </h2>
                            </div>

                            {/* DETALLES */}
                            <div className="pagoDetalles">
                                <p>📅 {pago.fecha}</p>
                                <p>🕐 {pago.hora && pago.hora !== '-' ? `${pago.hora} hs` : 'Horario de clase'}</p>
                                <p>⏱ Duración: 1 hora</p>
                            </div>

                            {/* MONTO Y BOTON */}
                            <div className="pagoFooter">
                                <div className="pagoMonto">
                                    <span className="pagoMontoLabel">Total a pagar</span>
                                    <span className="pagoMontoValor">
                                        ${pago.monto_deuda.toLocaleString('es-AR')}
                                    </span>
                                </div>
                                <button
                                    className="pagarBtn"
                                    onClick={() => handlePagar(pago)}
                                >
                                    Pagar
                                </button>
                            </div>

                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}