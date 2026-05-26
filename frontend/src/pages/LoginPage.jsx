
import { Link } from 'react-router-dom';
import { useState } from 'react';

import '../assets/styles/SignUp.css'; // USES SAME STYLES AS SIGNUP
import mesh from '../assets/images/mesh.png'
import logo from '../assets/images/logo-club360.png'
import eyeopen from '../assets/images/eye-open.png'
import eyeclosed from '../assets/images/eye-closed.png'
import redwarning from '../assets/images/warning-red.png'

import { useNavigate } from "react-router-dom";

import { toast } from 'react-toastify';

export default function SignUpPage(){

    const navigate = useNavigate(); // will be used for redirection once the user is registered

    // initial value for the array that represents the form values.
    const [formValue, setFormValue] = useState({ email: "", password: ""});

    // error array for frontend validations --> missing backend errors
    const [errors, setErrors] = useState({ email: "", password: ""});

    // state for toggling password visibility
    const [showPassword, setShowPassword] = useState(false);


    // frontend form validations --> just email for login

    const validateEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email) ? "" : "Correo inválido";
    };

    // central form validator
    const validators = {
        email: validateEmail
    };

    const validateField = (name, value) => {
        return validators[name] ? validators[name](value) : "";
    };


    // handleChange se usa para actualizar los valores de formValue y de sus errores correspondientes
    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormValue({
            ...formValue,
            [name]: value
        });

        setErrors({
            ...errors,
            [name]: validateField(name, value)
        });
    };

    

    // backend api communication is here!!
    
    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include", // REQUIRED for Flask session
                body: JSON.stringify({
                    email: formValue.email,
                    password: formValue.password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.mensaje || "Error al iniciar sesión");
                return;
            }

            toast.success(data.message);

            // redirect after login success
            navigate("/"); 

        } catch (error) {
            toast.error("Error de conexión con el servidor");
        }
    };


/// -----------------------------------------------


    // JSX
     // which page does the web server recieve: 

    return (
        <div className="signupContainer">
            <div className="mainDivider signupWelcome">

                {/*
                <div className="loginRedirection">
                    <p>¿No tenés una cuenta?</p>
                    <button onClick={() => navigate('/signup')}>Registrate</button>
                </div>
                */}

                <img src={logo} alt="Company logo"/>
                <p>¡Hola de nuevo!</p>
                <h1>CLUB 360</h1>
            </div>
            <div className="formContainer mainDivider">
            <h1 className="formTitle">Iniciá tu sesión</h1>
            <form className='formRegister'  onSubmit={handleSubmit}> 

                {/*E-MAIL*/}
                <div className="formInput">
                    <div className="labelRow">
                        <label>Correo electrónico</label>

                        <span className={`fieldError ${errors.email ? "show" : ""}`}>
                            {errors.email}
                        </span>
                    </div>

                    <div className="inputWrapper">
                        <input
                            className={errors.email ? "inputError" : ""}
                            value={formValue.email}
                            name="email"
                            type="text"
                            placeholder="tu-email@gmail.com"
                            onChange={handleChange}
                            required
                        />

                        {errors.email && (
                            <img src={redwarning} className="errorIcon" alt="error" />
                        )}
                    </div>
                </div>

                {/*PASSWORD*/}
                <div className="formInput">
                <div className="labelRow">
                        <label>Contraseña</label>

                        <span className={`fieldError ${errors.password ? "show" : ""}`}>
                            {errors.password}
                        </span>
                    </div>

                <div className="passwordWrapper inputWrapper">
                    <input
                        value={formValue.password}
                        name="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Elige tu contraseña!"
                        onChange={handleChange}
                        required
                    />

                    {errors.password && (
                            <img src={redwarning} className="errorIcon" alt="error" />
                    )}

                    <img
                        src={showPassword ? eyeopen : eyeclosed}
                        alt="toggle password visibility"
                        onClick={() => setShowPassword(prev => !prev)}
                    />
                </div>
            </div>

            <input type="submit" className="signUpSubmit" value="Enviar"/>

              {/* OLVIDE CONTRASEÑA */}
            <p className="olvidéLink">
                <span onClick={() => navigate('/olvide-contrasena')}>
                    Recuperar Contraseña
                </span>
            </p>

            </form>
            </div>
        </div>
    )
}