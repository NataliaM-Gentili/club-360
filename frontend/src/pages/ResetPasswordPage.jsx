import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-toastify';

import '../assets/styles/SignUp.css';
import logo from '../assets/images/logo-club360.png';
import eyeopen from '../assets/images/eye-open.png';
import eyeclosed from '../assets/images/eye-closed.png';

export default function ResetPasswordPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    const [formValue, setFormValue] = useState({ contrasena: '', confirmar: '' });
    const [errors, setErrors] = useState({ contrasena: '', confirmar: '' });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmar, setShowConfirmar] = useState(false);

    const validateContrasena = (value) => {
        return value.length >= 7 ? '' : 'Mínimo 7 caracteres';
    };

    const validateConfirmar = (value) => {
        return value === formValue.contrasena ? '' : 'Las contraseñas no coinciden';
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormValue({ ...formValue, [name]: value });
        if (name === 'contrasena') setErrors({ ...errors, contrasena: validateContrasena(value) });
        if (name === 'confirmar') setErrors({ ...errors, confirmar: validateConfirmar(value) });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formValue.contrasena !== formValue.confirmar) {
            setErrors({ ...errors, confirmar: 'Las contraseñas no coinciden' });
            return;
        }

        try {
            const response = await fetch('/api/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, contrasena: formValue.contrasena })
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.error || 'Error al actualizar la contraseña');
                return;
            }

            toast.success(data.message);
            navigate('/login');

        } catch (error) {
            toast.error('Error de conexión con el servidor');
        }
    };

    return (
        <div className="signupContainer">
            <div className="mainDivider signupWelcome">
                <img src={logo} alt="Company logo" />
                <p>Bienvenido a</p>
                <h1>CLUB 360</h1>
            </div>

            <div className="formContainer mainDivider">
                <h1 className="formTitle">Nueva contraseña</h1>
                <form className="formRegister" onSubmit={handleSubmit}>

                    {/* CONTRASEÑA */}
                    <div className="formInput">
                        <div className="labelRow">
                            <label>Nueva contraseña</label>
                            <span className={`fieldError ${errors.contrasena ? 'show' : ''}`}>
                                {errors.contrasena}
                            </span>
                        </div>
                        <div className="passwordWrapper inputWrapper">
                            <input
                                value={formValue.contrasena}
                                name="contrasena"
                                type={showPassword ? 'text' : 'password'}
                                placeholder="Mínimo 7 caracteres"
                                onChange={handleChange}
                                required
                            />
                            <img
                                src={showPassword ? eyeopen : eyeclosed}
                                alt="toggle"
                                onClick={() => setShowPassword(prev => !prev)}
                            />
                        </div>
                    </div>

                    {/* CONFIRMAR CONTRASEÑA */}
                    <div className="formInput">
                        <div className="labelRow">
                            <label>Confirmar contraseña</label>
                            <span className={`fieldError ${errors.confirmar ? 'show' : ''}`}>
                                {errors.confirmar}
                            </span>
                        </div>
                        <div className="passwordWrapper inputWrapper">
                            <input
                                value={formValue.confirmar}
                                name="confirmar"
                                type={showConfirmar ? 'text' : 'password'}
                                placeholder="Repetí tu contraseña"
                                onChange={handleChange}
                                required
                            />
                            <img
                                src={showConfirmar ? eyeopen : eyeclosed}
                                alt="toggle"
                                onClick={() => setShowConfirmar(prev => !prev)}
                            />
                        </div>
                    </div>

                    <input type="submit" className="signUpSubmit" value="Confirmar" />

                </form>
            </div>
        </div>
    );
}