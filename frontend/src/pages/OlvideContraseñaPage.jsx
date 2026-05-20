import { useState } from 'react';
import { toast } from 'react-toastify';

import '../assets/styles/SignUp.css';
import logo from '../assets/images/logo-club360.png';
import redwarning from '../assets/images/warning-red.png';

export default function OlvideContrasenaPage() {

    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [enviado, setEnviado] = useState(false);

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

        if (enviado) return;

        const emailError = validateEmail(email);
        if (emailError) {
            setError(emailError);
            return;
        }

        setEnviado(true);

        try {
            const response = await fetch('/api/generar-token-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.error || 'Error al procesar la solicitud');
                setEnviado(false);
                return;
            }

            toast.success(data.message);

        } catch (err) {
            toast.error('Error de conexión con el servidor');
            setEnviado(false);
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
                                disabled={enviado}
                            />
                            {error && (
                                <img src={redwarning} className="errorIcon" alt="error" />
                            )}
                        </div>
                    </div>

                    <input
                        type="submit"
                        className="signUpSubmit"
                        value={enviado ? 'Email enviado ✓' : 'Continuar'}
                        disabled={enviado}
                    />

                </form>
            </div>
        </div>
    );
}