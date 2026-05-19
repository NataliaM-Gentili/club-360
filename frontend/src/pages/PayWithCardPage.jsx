import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import '../assets/styles/PayWithCard.css'

import { toast } from "react-toastify";

export default function PayWithCardPage() {
    const navigate = useNavigate();

    const reservaId = localStorage.getItem("reserva_id");
    const userId = localStorage.getItem("user_id");

    const [loading, setLoading] = useState(true);

    const [reservaInfo, setReservaInfo] = useState(null);

    const [cards, setCards] = useState([]);
    const [selectedIndex, setSelectedIndex] = useState(0);

    const [selectedCard, setSelectedCard] = useState(null);

    // -----------------------------
    // FETCH RESERVA DETAILS
    // -----------------------------
    useEffect(() => {
        const fetchReserva = async () => {
            try {

                const response = await fetch(
                    `/api/reservas/${reservaId}`
                );

                if (!response.ok) {
                    throw new Error();
                }

                const data = await response.json();

                setReservaInfo(data);
            } catch (error) {
                toast.error("Error al cargar las reservas");
            }
        };

        const fetchCards = async () => {
            try {
                const response = await fetch(
                    `/api/tarjetas/${userId}`
                );

                if (!response.ok) {
                    throw new Error();
                }

                const data = await response.json();

                setCards(data);

                if (data.length === 0) {
                    toast.error("No posees tarjetas registradas. Asociá una desde tu perfil");
                } else {
                    setSelectedCard(data[0]);
                }
            } catch (error) {
                toast.error("Error al cargar las tarjetas");
            } finally {
                setLoading(false);
            }
        };

        fetchReserva();
        fetchCards();
    }, [reservaId, userId]);

    // -----------------------------
    // CAROUSEL
    // -----------------------------
    const nextCard = () => {
        if (cards.length === 0) return;

        const newIndex =
            selectedIndex === cards.length - 1 ? 0 : selectedIndex + 1;

        setSelectedIndex(newIndex);
        setSelectedCard(cards[newIndex]);
    };

    const prevCard = () => {
        if (cards.length === 0) return;

        const newIndex =
            selectedIndex === 0 ? cards.length - 1 : selectedIndex - 1;

        setSelectedIndex(newIndex);
        setSelectedCard(cards[newIndex]);
    };

    // -----------------------------
    // PAY
    // -----------------------------
    const handlePay = async () => {
        try {
            const response = await fetch(
                "/api/pago_tarjeta",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        id_reserva: reservaId,
                        id_tarjeta: selectedCard.id,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.mensaje);
                return;
            }

            // your backend returns 200 even for insufficient funds
            if (data.mensaje.includes("Saldo insuficiente")) {
                toast.error(data.mensaje);
                return;
            }

            toast.success(data.mensaje);

            setTimeout(() => {
                navigate("/");
            }, 1500);
        } catch (error) {
            toast.error("Error de procesamiento de pago");
        }
    };

    if (loading) {
        return <p className="pay-loading">Loading...</p>;
    }

    return (
        <div className="pay-page">

            <h1>Pagar Reserva</h1>

            {/* -----------------------------
                RESERVA INFO
            ------------------------------ */}
            {reservaInfo && (
                <div className="reservation-card">

                    <h2>{reservaInfo.disciplina}</h2>

                    <p>
                        <strong>Hour:</strong> {reservaInfo.hora}
                    </p>

                    {reservaInfo.tipo === "turno" ? (
                        <p>
                            <strong>Fecha:</strong> {reservaInfo.fecha}
                        </p>
                    ) : (
                        <p>
                            <strong>Todos los </strong> {reservaInfo.dia}
                        </p>
                    )}

                </div>
            )}

            {/* -----------------------------
                CARD CAROUSEL
            ------------------------------ */}
            {cards.length > 0 && (
                <div className="carousel-container">

                    <button
                        className="carousel-btn"
                        onClick={prevCard}
                    >
                        ◀
                    </button>

                    <div className="card-preview">

                        <h3>Tarjeta de crédito</h3>

                        <p>
                            **** **** **** {selectedCard?.numero}
                        </p>

                        <p>{selectedCard?.titular}</p>

                        <p>
                            Exp: {selectedCard?.fecha_vencimiento}
                        </p>

                    </div>

                    <button
                        className="carousel-btn"
                        onClick={nextCard}
                    >
                        ▶
                    </button>

                </div>
            )}

            {/* -----------------------------
                CONFIRM BUTTON
            ------------------------------ */}
            {selectedCard && (
                <button
                    className="confirm-pay-btn"
                    onClick={handlePay}
                >
                    Confirmar Pago
                </button>
            )}
        </div>
    );
}