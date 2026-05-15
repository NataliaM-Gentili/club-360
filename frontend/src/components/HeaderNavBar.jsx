import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useNavigate } from "react-router-dom";

import '../assets/styles/HeaderNavBar.css';
import logo from '../assets/images/logo-club360.png'

export default function HeaderNavBar(){

    const navigate = useNavigate();

    return(
        <header className="main-header">

            <button className="headerLogo" onClick={() => navigate('/dashboard')}>
                <img src={logo} alt="logo" />
            </button>

            <nav className="headerNav">
                <ul>
                    <li><Link to="/profile">Perfil</Link></li>
                    <li><Link to="/book">Reservar</Link></li>
                </ul>
            </nav>

        </header>
    )
}