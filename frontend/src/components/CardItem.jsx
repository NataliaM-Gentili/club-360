import { useNavigate } from "react-router-dom";
import '../assets/styles/CardItem.css'

export default function CardItem({ card }) {
    const navigate = useNavigate();

    return (
        <div className="cardItem">
            <p><strong>•••• •••• •••• {card.numero.slice(-4)}</strong></p>
            <p>{card.titular}</p>
            <p>{card.fecha_vencimiento}</p>

            <button
                className="editBtn"
                onClick={() => navigate(`/edit-card/${card.id}`)}
            >
                Editar
            </button>
        </div>
    );
}