
import { Link } from 'react-router-dom';
import { useState } from 'react';

import '../assets/styles/SignUp.css';
import mesh from '../assets/images/mesh.png'
import logo from '../assets/images/logo-club360.png'
import eyeopen from '../assets/images/eye-open.png'
import eyeclosed from '../assets/images/eye-closed.png'
import redwarning from '../assets/images/warning-red.png'

// import toastify?? --> research other libraries for showing errors

export default function SignUpPage(){

    // stores the state for the registered succesfully/unsuccesfully message
    const [isRegistered, setRegistered] = useState(false);

    // initial value for the array that represents the form values.
    const [formValue, setFormValue] = useState({ email: "", name: "", dni: "", password: ""});

    // error array for frontend validations --> missing backend errors
    const [errors, setErrors] = useState({ email: "", name: "", dni: "", password: ""});

    // state for toggling password visibility
    const [showPassword, setShowPassword] = useState(false);


    // frontend form validations

    const validateEmail = (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email) ? "" : "Correo inválido";
    };

    const validateDNI = (dni) => {
        const regex = /^\d{8}$/;
        return regex.test(dni) ? "" : "El DNI debe tener 8 dígitos";
    };

    const validateName = (name) => {
        const regex = /^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)(\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*$/;
        return regex.test(name)
            ? ""
            : "Cada palabra debe empezar con mayúscula";
    };

    const validatePassword = (password) => {
        return password.length > 6 ? "" : "Mínimo 7 caracteres";
    };

    // central form validator
    const validators = {
        email: validateEmail,
        dni: validateDNI,
        name: validateName,
        password: validatePassword
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

    

    // backend api communication should be here!!
    const handleSubmit = (e) => {

        // re-checks frontend input errors when the submit button ins clicked
        e.preventDefault();

        const newErrors = {
            email: validateEmail(formValue.email),
            name: validateName(formValue.name),
            dni: validateDNI(formValue.dni),
            password: validatePassword(formValue.password)
        };

        setErrors(newErrors);

        const hasErrors = Object.values(newErrors).some(err => err !== "");

        if (hasErrors) return;

        // simulate success
        setRegistered(true);
    };


    // JSX
     // which page does the web server recieve: 

    if (!isRegistered){ // this is shown in the user is not registered

    return (
        <div className="signupContainer">
            <div className="mainDivider signupWelcome">
                <div className="loginRedirection">
                    <p>¿Ya tenés una cuenta?</p>
                    <button>Login</button>
                </div>
                <img src={logo} alt="Company logo"/>
                <p>Bienvenido a</p>
                <h1>CLUB 360</h1>
            </div>
            <div className="formContainer mainDivider">
            <h1 className="formTitle">Creá tu cuenta</h1>
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

                {/*NAMES AND SURNAME*/}
                <div className="formInput">
                    <div className="labelRow">
                        <label>Nombre(s) y Apellido</label>

                        <span className={`fieldError ${errors.name ? "show" : ""}`}>
                            {errors.name}
                        </span>
                    </div>
                    <div className="inputWrapper">
                        <input
                            className={errors.name ? "inputError" : ""}
                            value={formValue.name}
                            name="name"
                            type="text"
                            placeholder="Juan Perez"
                            onChange={handleChange}
                            required
                        />

                        {errors.name && (
                            <img src={redwarning} className="errorIcon" alt="error" />
                        )}
                    </div>
                </div>

                {/*DNI*/}
                <div className="formInput">
                    <div className="labelRow">
                        <label>DNI</label>

                        <span className={`fieldError ${errors.dni ? "show" : ""}`}>
                            {errors.dni}
                        </span>
                    </div>
                    <div className="inputWrapper">
                        <input
                            className={errors.dni ? "inputError" : ""}
                            value={formValue.dni}
                            name="dni"
                            type="text"
                            placeholder="12345678"
                            onChange={handleChange}
                            required
                        />

                        {errors.dni && (
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

            </form>
            </div>
        </div>
    )

    }

    else{ // this is shown if the user is correctly registered

    }
}