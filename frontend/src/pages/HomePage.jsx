import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../assets/styles/HomePage.css';
import sports from '../assets/images/sports.png';

export default function HomePage() {
    const navigate = useNavigate();
    
    const activities = [
        { name: 'Fútbol',  price: '$ 9.000',  emoji: '⚽' },
        { name: 'Pádel',   price: '$ 12.000', emoji: '🎾' },
        { name: 'Vóley',   price: '$ 8.000',  emoji: '🏐' },
        { name: 'Básquet', price: '$ 8.500',  emoji: '🏀' },
    ];

    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        async function checkSession() {
            try {
                const response = await fetch('/api/auth/status', { credentials: 'include' });
                if (!response.ok) { 
                    setIsLoggedIn(false); 
                    return; 
                }
                
                const data = await response.json();
                
                /*
                // Redirección automática si es Cliente (Rol 1)
                const rolId = data.rol_id || data.user?.rol_id;
                if (rolId === 1) {
                    navigate("/mis-Actividades");
                    return; 
                }
                */

                setIsLoggedIn(!!(data.loggedIn || data.logged_in || data.authenticated || data.user));
            } catch {
                setIsLoggedIn(false);
            }
        }
        checkSession();
    }, [navigate]);

    return (
        /* 👇 EL NUEVO CONTENEDOR PARA EL FONDO ONDULADO 👇 */
        <div className="home-wrapper">
            
            <main className="home-root">
                
                {/* ── LEFT COLUMN ── */}
                <section className="home-left">
                    <div className="home-tag">Tu club deportivo</div>
                    
                    <h1 className="home-title">
                        Bienvenido a<br />
                        <span className="home-title-accent">Club 360</span>
                    </h1>

                    <p className="home-sub">
                        Canchas y actividades para todas las edades.<br />
                        Reservá tu turno y viví el deporte en comunidad.
                    </p>

                    <p className="home-address">📍 Av. 1234 N°567, La Plata, ARG</p>

                    {/* ACTIVITIES */}
                    <div className="home-activities">
                        <p className="home-activities-label">Actividades y precios por hora</p>
                        <div className="home-activities-grid">
                            {activities.map(a => (
                                <div className="activity-chip" key={a.name}>
                                    <span className="activity-chip-emoji">{a.emoji}</span>
                                    <span className="activity-chip-name">{a.name}</span>
                                    <span className="activity-chip-price">{a.price}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* BUTTONS */}
                    {!isLoggedIn && (
                        <div className="home-cta-row">
                            <Link to="/login">
                                <button className="home-btn home-btn-primary">Iniciar sesión</button>
                            </Link>
                            <Link to="/signup">
                                <button className="home-btn home-btn-outline">Registrarse</button>
                            </Link>
                            <Link to="/turnos">
                                <button className="home-btn home-btn-ghost">Buscar turnos →</button>
                            </Link>
                        </div>
                    )}
                </section>

                {/* ── RIGHT COLUMN ── */}
                <div className="home-right">
                    <div className="home-image-wrap">
                        <img src={sports} alt="instalaciones Club 360" className="home-image" />
                        <div className="home-image-badge">
                            <span className="badge-number">360°</span>
                            <span className="badge-text">deporte</span>
                        </div>
                    </div>
                </div>

            </main>
            
        </div>
    );
}