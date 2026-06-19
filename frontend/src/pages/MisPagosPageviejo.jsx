import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../assets/styles/MisPagos.css';

import { toast } from 'react-toastify';

import PaymentModal from "../components/PaymentModal";

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

    // para la parte de pagar con tarjeta:
    const [modalOpen, setModalOpen] = useState(false);
    const [selectedPago, setSelectedPago] = useState(null);

    const [reservaInfo, setReservaInfo] = useState(null);

    const [cards, setCards] = useState([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [selectedCard, setSelectedCard] = useState(null);

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

    const handlePagar = async (pago) => {
        try {
            localStorage.setItem("reserva_id", pago.id_reserva);
            localStorage.setItem("user_id", pago.id_cliente);

            setSelectedPago(pago);
            setModalOpen(true);

            // fetch cards
            const resCards = await fetch(`/api/tarjetas/${pago.id_cliente}`, { 
                    method: 'GET',
                    credentials: 'include' });

            const cardsData = await resCards.json();

            if (cardsData.length === 0) {
                toast.error("No tenés tarjetas registradas");
            }

            setCards(cardsData);
            setSelectedIndex(0);
            setSelectedCard(cardsData[0]);

        } catch (err) {
            toast.error("Error cargando datos de pago");
        }
    };

    // --- controles del carrousell
    const nextCard = () => {
        if (!cards.length) return;

        const newIndex = (selectedIndex + 1) % cards.length;
        setSelectedIndex(newIndex);
        setSelectedCard(cards[newIndex]);
    };

    const prevCard = () => {
        if (!cards.length) return;

        const newIndex =
            (selectedIndex - 1 + cards.length) % cards.length;

        setSelectedIndex(newIndex);
        setSelectedCard(cards[newIndex]);
    };

    // ----

    // PAGAR
    const confirmPay = async () => {
    try {
        const res = await fetch("/api/pago_tarjeta", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id_reserva: selectedPago.id_reserva,
                id_tarjeta: selectedCard.id,
            }),
        });

        const data = await res.json();

        if (!res.ok || data.mensaje.includes("insuficiente")) {
            toast.error(data.mensaje || data.error || "Error al procesar el pago");
            return;
        }

        toast.success(data.mensaje);

        // close modal + refresh list
        setModalOpen(false);
        setPagos(prev => prev.filter(p => p.id_reserva !== selectedPago.id_reserva));

    } catch (err) {
        toast.error("Error procesando pago");
    }
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

                        {modalOpen && selectedPago && (
                <PaymentModal
                    isOpen={modalOpen}
                    onClose={() => setModalOpen(false)}
                    cards={cards}
                    selectedCard={selectedCard}
                    setSelectedCard={setSelectedCard}
                    onConfirm={confirmPay}
                    reservaInfo={selectedPago}
                    amount={selectedPago?.monto_deuda}
                />
            )}
        </div>
    );
}