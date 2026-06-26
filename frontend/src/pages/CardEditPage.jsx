import { useNavigate, useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import '../assets/styles/CardRegister.css';
import { toast } from 'react-toastify';

export default function CardEditPage() {
    const { id } = useParams(); // Obtenemos el ID de la url
    const navigate = useNavigate();

    // ESTADOS
    const [initialValue, setInitialValue] = useState(null); // Guarda la copia original
    const [formValue, setFormValue] = useState({ number: "", expirationDate: "", owner: "", cvv: "" });
    const [errors, setErrors] = useState({ number: "", expirationDate: "", owner: "", cvv: "" });

    // CARGAR LOS DATOS DE LA TARJETA AL ENTRAR
    useEffect(() => {
        const fetchTarjeta = async () => {
            try {
                const res = await fetch(`/api/tarjeta/${id}`, { credentials: "include" });
                const data = await res.json();
                if (res.ok) {
                    const datosCargados = {
                        number: data.numero,
                        expirationDate: data.fecha_vencimiento,
                        owner: data.titular,
                        cvv: data.cvv
                    };
                    
                    setFormValue(datosCargados);
                    setInitialValue(datosCargados);
                } else {
                    toast.error("Error al cargar la tarjeta");
                }
            } catch (error) {
                console.error("Error fetching card", error);
            }
        };
        fetchTarjeta();
    }, [id]);

    // FUNCIONES DE VALIDACIÓN
    const validateCardNumber = (number) => {
        const regex = /^\d{16}$/;
        return regex.test(number) ? "" : "Debe tener 16 dígitos";
    };

    const validateExpiration = (dateStr) => {
        // 1. Validar formato YYYY-MM
        const regex = /^\d{4}-\d{2}$/;
        if (!regex.test(dateStr)) return "Formato YYYY-MM";

        // 2. Validar si está vencida
        const [year, month] = dateStr.split('-').map(Number);
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;

        if (year < currentYear || (year === currentYear && month < currentMonth)) {
            return "La tarjeta está vencida";
        }

        return ""; // Si todo está bien, no hay error
    };

    const validateCVV = (cvv) => {
        const regex = /^\d{3}$/;
        return regex.test(cvv) ? "" : "Debe tener 3 dígitos";
    };

    const validators = {
        number: validateCardNumber,
        expirationDate: validateExpiration,
        cvv: validateCVV,
    };

    // ACTUALIZAR ESTADOS AL ESCRIBIR
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormValue({ ...formValue, [name]: value });
        setErrors({
            ...errors,
            [name]: validators[name] ? validators[name](value) : ""
        });
    };

    // VERIFICACIONES PARA HABILITAR EL BOTÓN
    const isFormValid = 
        formValue.number.trim() !== "" &&
        formValue.expirationDate.trim() !== "" &&
        formValue.owner.trim() !== "" &&
        formValue.cvv.trim() !== "" &&
        errors.number === "" &&
        errors.expirationDate === "" &&
        errors.cvv === "";

    const formHaCambiado = initialValue !== null && (
        formValue.number !== initialValue.number ||
        formValue.expirationDate !== initialValue.expirationDate ||
        formValue.owner !== initialValue.owner ||
        formValue.cvv !== initialValue.cvv
    );

    // GUARDAR CAMBIOS
    const handleSubmit = async (e) => {
        e.preventDefault();

        const newErrors = {
            number: validateCardNumber(formValue.number),
            expirationDate: validateExpiration(formValue.expirationDate),
            cvv: validateCVV(formValue.cvv),
        };

        setErrors(newErrors);
        const hasErrors = Object.values(newErrors).some(err => err !== "");
        if (hasErrors) return;

        try {
            const response = await fetch(`/api/editar-tarjeta/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    numero: formValue.number,
                    fecha_vencimiento: formValue.expirationDate,
                    cvv: formValue.cvv,
                    titular: formValue.owner
                })
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.error || data.mensaje || "Error al actualizar tarjeta");
                return;
            }

            toast.success(data.mensaje || "Tarjeta actualizada correctamente");
            navigate("/profile"); // Volvemos al perfil tras guardar exitosamente

        } catch (err) {
            toast.error("Error de conexión con el servidor");
        }
    };

    return (
        <div className="cardRegisterFormContainer">
            <form className="cardRegisterForm" onSubmit={handleSubmit}> 
                <h1 className="cardRegisterFormTitle">Editar Tarjeta</h1>

                {/* NUMBER */}
                <div className="formInput">
                    <div className="labelRow">
                        <label>Número de Tarjeta</label>
                        <span className={`fieldError ${errors.number ? "show" : ""}`}>{errors.number}</span>
                    </div>
                    <div className="inputWrapper">
                        <input className="cardRegisterInput" value={formValue.number} name="number" type="text" inputMode="numeric" pattern="[0-9]*" onChange={handleChange} required />
                    </div>
                </div>

                {/* EXPIRATION DATE */}
                <div className="formInput">
                    <div className="labelRow">
                        <label>Fecha de Vencimiento</label>
                        <span className={`fieldError ${errors.expirationDate ? "show" : ""}`}>{errors.expirationDate}</span>
                    </div>
                    <div className="inputWrapper">
                        <input className="cardRegisterInput" value={formValue.expirationDate} name="expirationDate" type="month" onChange={handleChange} required />
                    </div>
                </div>

                {/* OWNER */}
                <div className="formInput">
                    <label>Titular</label>
                    <div className="inputWrapper">
                        <input className="cardRegisterInput" value={formValue.owner} name="owner" type="text" onChange={handleChange} required />
                    </div>
                </div>

                {/* CVV */}
                <div className="formInput">
                    <div className="labelRow">
                        <label>CVV</label>
                        <span className={`fieldError ${errors.cvv ? "show" : ""}`}>{errors.cvv}</span>
                    </div>
                    <div className="inputWrapper">
                        <input className="cardRegisterInput" value={formValue.cvv} name="cvv" type="text" inputMode="numeric" pattern="[0-9]*" onChange={handleChange} required />
                    </div>
                </div>

                {/* BOTONES DE ACCIÓN */}
                <input 
                    type="submit" 
                    className="cardRegisterSUbmit" 
                    value="Guardar Cambios" 
                    disabled={!isFormValid || !formHaCambiado}
                />
                <button 
                    type="button" 
                    className="cardRegisterSUbmit" 
                    style={{backgroundColor:"#6c757d", marginTop: "10px"}} 
                    onClick={() => navigate("/profile")}
                >
                    Cancelar
                </button>
            </form>
        </div>
    );
}