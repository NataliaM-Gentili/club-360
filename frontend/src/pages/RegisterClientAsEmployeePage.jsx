import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import "../assets/styles/SignUp.css";
import logo from "../assets/images/logo-club360.png";
import eyeopen from "../assets/images/eye-open.png";
import eyeclosed from "../assets/images/eye-closed.png";
import redwarning from "../assets/images/warning-red.png";

export default function RegisterClientAsEmployee() {
  const navigate = useNavigate();

  const [formValue, setFormValue] = useState({
    email: "",
    dni: "",
    name: "",
    password: "",
  });

  const [errors, setErrors] = useState({
    email: "",
    dni: "",
    name: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);

  // ---------------- VALIDATIONS ----------------

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
    return password.length >= 7 ? "" : "Mínimo 7 caracteres";
  };

  const validateField = (name, value) => {
    const validators = {
      email: validateEmail,
      dni: validateDNI,
      name: validateName,
      password: validatePassword,
    };
    return validators[name] ? validators[name](value) : "";
  };

  // ---------------- HANDLE CHANGE ----------------

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormValue({
      ...formValue,
      [name]: value,
    });

    setErrors({
      ...errors,
      [name]: validateField(name, value),
    });
  };

  // ---------------- HANDLE SUBMIT ----------------

  const handleSubmit = async (e) => {
    e.preventDefault();

    const newErrors = {
      email: validateEmail(formValue.email),
      dni: validateDNI(formValue.dni),
      name: validateName(formValue.name),
      password: validatePassword(formValue.password),
    };

    setErrors(newErrors);

    const hasErrors = Object.values(newErrors).some((err) => err !== "");
    if (hasErrors) return;

    try {
      const response = await fetch("/api/registrar_cliente", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // important for session
        body: JSON.stringify({
          email: formValue.email,
          dni: formValue.dni,
          nombres: formValue.name.split(" ")[0],
          apellido: formValue.name.split(" ").slice(1).join(" "),
          contrasena: formValue.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(
          "Cliente registrado y email enviado correctamente ✉️"
        );

        setFormValue({
          email: "",
          dni: "",
          name: "",
          password: "",
        });

        // optional redirect
        // setTimeout(() => navigate("/dashboard"), 2000);
      } else {
        toast.error(data.error || "Error al registrar cliente");
      }
    } catch (error) {
      toast.error("Error de conexión con el servidor");
    }
  };

  // ---------------- JSX ----------------

  return (
    <div className="signupContainer">
      <div className="mainDivider signupWelcome">
        <p>Panel de Empleado</p>
        <h1>Registrar Cliente</h1>
      </div>

      <div className="formContainer mainDivider">
        <h1 className="formTitle">Nuevo Cliente</h1>

        <form className="formRegister" onSubmit={handleSubmit}>
          {/* EMAIL */}
          <div className="formInput">
            <div className="labelRow">
              <label>Email</label>
              <span className={`fieldError ${errors.email ? "show" : ""}`}>
                {errors.email}
              </span>
            </div>

            <div className="inputWrapper">
              <input
                name="email"
                value={formValue.email}
                onChange={handleChange}
                placeholder="cliente@email.com"
              />
              {errors.email && (
                <img src={redwarning} className="errorIcon" alt="error" />
              )}
            </div>
          </div>

          {/* NAME */}
          <div className="formInput">
            <div className="labelRow">
              <label>Nombre completo</label>
              <span className={`fieldError ${errors.name ? "show" : ""}`}>
                {errors.name}
              </span>
            </div>

            <div className="inputWrapper">
              <input
                name="name"
                value={formValue.name}
                onChange={handleChange}
                placeholder="Juan Pérez"
              />
              {errors.name && (
                <img src={redwarning} className="errorIcon" alt="error" />
              )}
            </div>
          </div>

          {/* DNI */}
          <div className="formInput">
            <div className="labelRow">
              <label>DNI</label>
              <span className={`fieldError ${errors.dni ? "show" : ""}`}>
                {errors.dni}
              </span>
            </div>

            <div className="inputWrapper">
              <input
                name="dni"
                value={formValue.dni}
                onChange={handleChange}
                placeholder="12345678"
              />
              {errors.dni && (
                <img src={redwarning} className="errorIcon" alt="error" />
              )}
            </div>
          </div>

          {/* PASSWORD */}
          <div className="formInput">
            <div className="labelRow">
              <label>Contraseña temporal</label>
              <span className={`fieldError ${errors.password ? "show" : ""}`}>
                {errors.password}
              </span>
            </div>

            <div className="passwordWrapper inputWrapper">
              <input
                name="password"
                type={showPassword ? "text" : "password"}
                value={formValue.password}
                onChange={handleChange}
              />

              {errors.password && (
                <img src={redwarning} className="errorIcon" alt="error" />
              )}

              <img
                src={showPassword ? eyeopen : eyeclosed}
                alt="toggle"
                onClick={() => setShowPassword((prev) => !prev)}
              />
            </div>
          </div>

          <input
            type="submit"
            className="signUpSubmit"
            value="Enviar"
          />
        </form>
      </div>
    </div>
  );
}