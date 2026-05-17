import { useState } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { toast } from 'react-toastify';

import '../assets/styles/CrearClase.css';
import logo from '../assets/images/logo-club360.png';

const DISCIPLINAS = ['paddle', 'futbol', 'basquet', 'voley'];
const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
const HORAS = ['08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21'];

const getMinutos = (hora) => {
    if (hora === '21') return ['00'];
    return ['00', '15', '30', '45'];
};

const ROL_ADMINISTRADOR = 2;

export default function CrearClasePage() {

    const navigate = useNavigate();
    const { rol_id } = useOutletContext();

    if (rol_id !== ROL_ADMINISTRADOR) {
        navigate("/");
        return null;
    }

    const [formValue, setFormValue] = useState({
        disciplina: '',
        dia: '',
        horaHH: '',
        horaMM: '',
        cupo: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;

        // si cambia la hora, resetear los minutos
        if (name === 'horaHH') {
            setFormValue({ ...formValue, horaHH: value, horaMM: '' });
            return;
        }

        setFormValue({ ...formValue, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('/api/crear_clase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    disciplina: formValue.disciplina,
                    dia: formValue.dia,
                    hora: `${formValue.horaHH}:${formValue.horaMM}`,
                    cupo: parseInt(formValue.cupo)
                })
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.error || 'Error al crear la clase');
                return;
            }

            toast.success(data.message);
            navigate('/');

        } catch (error) {
            toast.error('Error de conexión con el servidor');
        }
    };

    return (
        <div className="crearClaseContainer">
            <div className="crearClaseWelcome">
                <img src={logo} alt="Company logo" />
                <p>Nueva</p>
                <h1>CLASE</h1>
            </div>

            <div className="crearClaseFormContainer">
                <h1 className="crearClaseTitle">Crear clase</h1>

                <form className="crearClaseForm" onSubmit={handleSubmit}>

                    {/* DISCIPLINA */}
                    <div className="crearClaseInput">
                        <label>Disciplina</label>
                        <select name="disciplina" value={formValue.disciplina} onChange={handleChange} required>
                            <option value="">-- Seleccioná --</option>
                            {DISCIPLINAS.map((d) => (
                                <option key={d} value={d}>
                                    {d.charAt(0).toUpperCase() + d.slice(1)}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* DIA */}
                    <div className="crearClaseInput">
                        <label>Día</label>
                        <select name="dia" value={formValue.dia} onChange={handleChange} required>
                            <option value="">-- Seleccioná --</option>
                            {DIAS.map((d) => (
                                <option key={d} value={d}>{d}</option>
                            ))}
                        </select>
                    </div>

                    {/* HORA */}
                    <div className="crearClaseInput">
                        <label>Hora</label>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <select name="horaHH" value={formValue.horaHH} onChange={handleChange} required>
                                <option value="">HH</option>
                                {HORAS.map((h) => (
                                    <option key={h} value={h}>{h}</option>
                                ))}
                            </select>
                            <select name="horaMM" value={formValue.horaMM} onChange={handleChange} required disabled={!formValue.horaHH}>
                                <option value="">MM</option>
                                {getMinutos(formValue.horaHH).map((m) => (
                                    <option key={m} value={m}>{m}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* CUPO */}
                    <div className="crearClaseInput">
                        <label>Cupo</label>
                        <input
                            type="number"
                            name="cupo"
                            value={formValue.cupo}
                            onChange={handleChange}
                            min="1"
                            placeholder="Ej: 20"
                            required
                        />
                    </div>

                    <input type="submit" className="crearClaseSubmit" value="Crear" />

                </form>
            </div>
        </div>
    );
}