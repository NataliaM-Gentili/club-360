import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { useEffect } from 'react';

import '../assets/styles/HeaderNavBar.css';
import logo from '../assets/images/logo-club360.png'

export default function HeaderNavBar(){

    const navigate = useNavigate();

   const [auth, setAuth] = useState({
        loggedIn: false,
        rol_id: null
    });

    // corre cada vez que se renderiza la página
    useEffect(() => {
        fetch("api/auth/status", {
            credentials: "include"
        })
        .then(res => res.json())
        .then(data => {
            setAuth({
                loggedIn: data.loggedIn,
                rol_id: data.rol_id || null
            });
        })
        .catch(() => {
            setAuth({ loggedIn: false, rol_id: null });
        });
    }, []);


    const logout = async () => {
        try {
            await fetch("api/logout", {
                method: "POST",
                credentials: "include", //(sends session cookie)
            });

            navigate("/"); // go home or login page
            window.location.reload(); // optional but often useful
        } catch (err) {
            console.error("Logout error:", err);
        }
    };

    // lógica de qué botones se renderizan según el rol:
        const renderLinks = () => {
        if (!auth.loggedIn) {
            return (
                <>
                  {/*  <li><Link to="/signup">Registrarse</Link></li>
                    <li><Link to="/login">Iniciar Sesión</Link></li> */}
                </>
            );
        }

        switch (auth.rol_id) {

            case 1: // CLIENT
                return (
                    <>
                        <li><Link to="/profile">Ver Perfil</Link></li>
                        <li><Link to="/book">Reservar</Link></li>
                        <li><button className="logoutBtn" onClick={logout}>Cerrar Sesión</button></li>
                    </>
                );

            case 2: // ADMIN
                return (
                    <>
                        <li><Link to="/classes">Ver Clases/Turnos</Link></li>
                        <li><button className="logoutBtn" onClick={logout}>Cerrar Sesión</button></li>
                    </>
                );

            case 3: // EMPLOYEE
                return (
                    <>
                        <li><Link to="/qr">Escanear QR</Link></li>
                        <li><Link to="/attendance">Asistencia Manual</Link></li>
                        <li><Link to="/register-client">Registrar Cliente</Link></li>
                        <li><Link to="/payments">Registrar Pago</Link></li>
                        <li><button className="logoutBtn" onClick={logout}>Cerrar Sesión</button></li>
                    </>
                );

            default:
                return null;
        }
    };

    if (!auth.loggedIn) return null;

    return (
        <header className="main-header">

            <button className="headerLogo" onClick={() => navigate('/')}>
                <img src={logo} alt="logo" />
            </button>

            <nav className="headerNav">
                <ul>
                    {renderLinks()}
                </ul>
            </nav>

        </header>
    );
}