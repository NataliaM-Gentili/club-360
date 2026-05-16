import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import CardItem from "../components/CardItem";
import "../assets/styles/ProfilePage.css";

export default function ProfilePage() {
    const navigate = useNavigate();

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await fetch("http://localhost:5000/profile", {
                    credentials: "include"
                });

                const json = await res.json();
                setData(json);
            } catch (err) {
                console.error("Error fetching profile:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    if (loading) return <div className="profileContainer">Cargando...</div>;
    if (!data) return <div className="profileContainer">Error al cargar perfil</div>;

    const { user, cards } = data;

    return (
        <div className="profileContainer">

            {/* TOP SECTION */}
            <div className="profileHeader">

                <div className="profileLeft">
                    <div className="profilePic">
                        {user.avatar ? (
                            <img src={user.avatar} alt="profile" />
                        ) : (
                            <div className="avatarFallback">
                                {user.email[0].toUpperCase()}
                            </div>
                        )}
                    </div>

                    <div className="profileMainInfo">
                        <h2>{user.email}</h2>
                        <p>{user.nombres + " " + user.apellido}</p>

                        {/* LOGICA TEMPORAL --> NO FUNCIONA EN REALIDAD 
                        <span className={`status ${user.suspended ? "suspended" : "active"}`}>
                            {user.suspended ? "Suspendido" : "Activo"}
                        </span>
                        */}

                    </div>
                </div>

            </div>

            {/* CARDS SECTION */}
            <div className="cardsSection">
                <h3>Mis tarjetas</h3>

                {cards.length === 0 ? (
                    <p className="emptyState">No posees tarjetas registradas</p>
                ) : (
                    <div className="cardsGrid">
                        {cards.map(card => (
                            <CardItem key={card.id} card={card} />
                        ))}
                    </div>
                )}

                <button
                    className="primaryBtn"
                    onClick={() => navigate("/card-register")}
                >
                    Nueva tarjeta
                </button>
            </div>

            {/* ACTIONS */}
            <div className="profileActions">
                <button onClick={() => navigate("/books")}>
                    Mis Reservas
                </button>

                <button onClick={() => navigate("/payments")}>
                    Pagos Pendientes
                </button>
            </div>

        </div>
    );
}