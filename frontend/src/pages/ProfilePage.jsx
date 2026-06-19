import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import CardItem from "../components/CardItem";
import "../assets/styles/ProfilePage.css";

export default function ProfilePage() {
    const navigate = useNavigate();

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

   useEffect(() => {
        const fetchProfileData = async () => {
            try {
                // 1. Obtener los datos básicos del usuario
                const resProfile = await fetch("/api/profile", {
                    credentials: "include"
                });
                const dataProfile = await resProfile.json();

                // 2. Usar el ID del usuario para ir a buscar sus tarjetas reales
                const resCards = await fetch(`/api/tarjetas/${dataProfile.user.id}`, {
                    credentials: "include"
                });
                
                let realCards = [];
                if (resCards.ok) {
                    realCards = await resCards.json();
                }

                // 3. Juntar todo (Usuario + Tarjetas reales) y guardarlo en el estado
                setData({
                    user: dataProfile.user,
                    cards: realCards
                });

            } catch (err) {
                console.error("Error al cargar el perfil:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchProfileData();
    }, []);

    const handleCambiarContrasena = async () => {
        try {
            const res = await fetch("/api/generar-token-cambio", {
                method: "POST",
                credentials: "include"
            });

            const json = await res.json();

            if (!res.ok) {
                console.error("Error al generar token:", json.error);
                return;
            }

            navigate(`/olvide-contrasena`);

        } catch (err) {
            console.error("Error al cambiar contraseña:", err);
        }
    };

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
                    </div>
                </div>

                {/* BOTON CAMBIAR CONTRASEÑA */}
                <button
                    className="cambiarContrasenaBtn"
                    onClick={handleCambiarContrasena}
                >
                    Recuperar Contraseña 
                </button>

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
                <button onClick={() => navigate("/mis-actividades")}>
                    Mis actividades
                </button>

                <button onClick={() => navigate("/mis-pagos")}>
                    Pagos Pendientes
                </button>

                <button onClick={() => navigate("/historial-pagos")}>
                    Historial de Pagos
                </button>
            </div>

        </div>
    );
}