import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import '../assets/styles/HomePage.css';
import sports from '../assets/images/sports.png';

export default function HomePage() {
    const activities = [
        { name: 'Fútbol', price: '$ 9000' },
        { name: 'Pádel', price: '$ 12000' },
        { name: 'Vóley', price: '$ 8000' },
        { name: 'Básquet', price: '$ 8500' },
    ];

    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // evalúa si el usuario inició sesión o no para ver qué botones mostrar del home
    useEffect(() => {
        async function checkSession() {
            try {
                const response = await fetch('/api/auth/status', {
                    credentials: 'include',
                });

                if (!response.ok) {
                    setIsLoggedIn(false);
                    return;
                }

                const data = await response.json();
                const loggedIn = !!(
                    data.loggedIn ||
                    data.logged_in ||
                    data.authenticated ||
                    data.user
                );

                setIsLoggedIn(loggedIn);
            } catch {
                setIsLoggedIn(false);
            }
        }

        checkSession();
    }, []);

    return (
        <main className="home-root">
            <section className="hero">
                <div className="hero-content">
                    <h1>¡Bienvenido a Club 360!</h1>
                    <p className="subtitle">Tu espacio deportivo cerca de casa</p>
                    <p className="description">Club 360 ofrece canchas y actividades para todas las edades. Reservá tu turno y viví el deporte en comunidad.</p>
                    <div className="address">Av. Principal 1234, Ciudad</div>
                </div>

                <section className="activities">
                    <h2>Actividades y precios (por hora)</h2>
                    <ul>
                        {activities.map(a => (
                            <li key={a.name} className="activity-row">
                                <span className="activity-name">{a.name}</span>
                                <span className="activity-price">{a.price}</span>
                            </li>
                        ))}
                    </ul>
                    
                </section>

                {!isLoggedIn && (
                    <div className="login-prompt">
                        <p>¡Iniciá sesión para reservar!</p>
                        <p>Crea una cuenta si no estás registrado</p>
                    </div> ) }
            </section>

            <div className="hero-image">
                <img src={sports} alt="deportes" />
            </div>
        </main>
    );
}
