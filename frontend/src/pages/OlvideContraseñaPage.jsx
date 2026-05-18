import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

import '../assets/styles/SignUp.css';
import logo from '../assets/images/logo-club360.png';
import redwarning from '../assets/images/warning-red.png';

export default function OlvideContrasenaPage() {
    const navigate = useNavigate();

    const [email, setEmail] = useState('');
    const [error, setError] = useState('');

    const validateEmail = (value) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(value) ? '' : 'Correo inválido';
    };

    const handleChange = (e) => {
        setEmail(e.target.value);
        setError(validateEmail(e.target.value));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const emailError = validateEmail(email);
        if (emailError) {
            setError(emailError);
            return;
        }

        try {
            const response = await fetch('/api/generar-token-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.error || 'Error al procesar la solicitud');
                return;
            }

            navigate(`/reset-password?token=${data.token}`);

        } catch (err) {
            toast.error('Error de conexión con el servidor');
        }
    };

    return (
        <div className="signupContainer">
            <div className="mainDivider signupWelcome">
                <img src={logo} alt="Company logo" />
                <p>No te preocupes</p>
                <h1>CLUB 360</h1>
            </div>

            <div className="formContainer mainDivider">
                <h1 className="formTitle">Recuperar contraseña</h1>
                <form className="formRegister" onSubmit={handleSubmit}>

                    <div className="formInput">
                        <div className="labelRow">
                            <label>Correo electrónico</label>
                            <span className={`fieldError ${error ? 'show' : ''}`}>
                                {error}
                            </span>
                        </div>
                        <div className="inputWrapper">
                            <input
                                className={error ? 'inputError' : ''}
                                value={email}
                                name="email"
                                type="text"
                                placeholder="tu-email@gmail.com"
                                onChange={handleChange}
                                required
                            />
                            {error && (
                                <img src={redwarning} className="errorIcon" alt="error" />
                            )}
                        </div>
                    </div>

                    <input type="submit" className="signUpSubmit" value="Continuar" />

                </form>
            </div>
        </div>
    );
}