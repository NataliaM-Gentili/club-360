import '../assets/styles/PaymentModal.css';

export default function PaymentModal({
    isOpen,
    onClose,
    cards,
    selectedCard,
    setSelectedCard,
    onConfirm,
    reservaInfo,
    amount
}) {

    if (!isOpen) return null;

    const currentIndex = cards.findIndex(c => c.id === selectedCard?.id);

    const nextCard = () => {
        const next = (currentIndex + 1) % cards.length;
        setSelectedCard(cards[next]);
    };

    const prevCard = () => {
        const prev = (currentIndex - 1 + cards.length) % cards.length;
        setSelectedCard(cards[prev]);
    };

    return (
        <div className="modalOverlay" onClick={onClose}>

            <div
                className="modalContent"
                onClick={(e) => e.stopPropagation()}
            >

                <h2>Confirmar pago</h2>

                {reservaInfo && (
                    <div className="modalReserva">
                        <h3>{reservaInfo.disciplina}</h3>

                        {reservaInfo.fecha && (
                            <p>📅 {reservaInfo.fecha}</p>
                        )}

                        {reservaInfo.hora && (
                            <p>🕐 {reservaInfo.hora}</p>
                        )}
                    </div>
                )}

                <div className="modalAmount">
                    Total: ${amount?.toLocaleString('es-AR')}
                </div>

                {cards.length > 0 && (
                    <div className="carousel">

                        <button onClick={prevCard}>
                            ◀
                        </button>

                        <div className="card">
                            <p>
                                **** **** **** {selectedCard?.numero}
                            </p>

                            <p>{selectedCard?.titular}</p>

                            <p>
                                {selectedCard?.fecha_vencimiento}
                            </p>
                        </div>

                        <button onClick={nextCard}>
                            ▶
                        </button>

                    </div>
                )}

                <div className="modalActions">

                    <button onClick={onClose}>
                        Cancelar
                    </button>

                    {selectedCard && (
                        <button onClick={onConfirm}>
                            Confirmar pago
                        </button>
                    )}

                </div>

            </div>
        </div>
    );
}