import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../assets/styles/ListarTurnos.css';
import lupa from '../assets/images/lupa.png';

const DISCIPLINAS = ['paddle', 'futbol', 'basquet', 'voley'];
const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
const HORAS = ['08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21'];

const getMinutos = (hora) => {
    if (hora === '21') return ['00'];
    return ['00', '15', '30', '45'];
};

const ROL_ADMINISTRADOR = 2;

export default function ListarTurnosPage() {
    const navigate = useNavigate();

    const [session, setSession] = useState(null);
    const [filtros, setFiltros] = useState({ disciplina: '', dia: '', horaHH: '', horaMM: '' });
    const [turnos, setTurnos] = useState([]);
    const [buscado, setBuscado] = useState(false);
    const [cargando, setCargando] = useState(false);

    useEffect(() => {
        fetch('/api/auth/status', { credentials: 'include' })
            .then(res => res.json())
            .then(data => setSession(data))
            .catch(() => setSession({ loggedIn: false }));
    }, []);

    const esAdmin = session?.rol_id === ROL_ADMINISTRADOR;
    const logueado = session?.loggedIn;

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name === 'horaHH') {
            setFiltros({ ...filtros, horaHH: value, horaMM: '' });
            return;
        }
        setFiltros({ ...filtros, [name]: value });
    };

    const handleBuscar = async (e) => {
        e.preventDefault();

        setCargando(true);
        setBuscado(false);

        const hora = `${filtros.horaHH}:${filtros.horaMM}`;
        const params = new URLSearchParams({ disciplina: filtros.disciplina, dia: filtros.dia, hora });

        try {
            const response = await fetch(`/api/buscar_turnos?${params}`, { credentials: 'include' });
            const data = await response.json();
            setTurnos(data.turnos);
            setBuscado(true);
        } catch (error) {
            console.error('Error al buscar turnos:', error);
        } finally {
            setCargando(false);
        }
    };

    const handleAccionNoLogueado = () => navigate('/login');

    return (
        <div className="listarTurnosContainer">
            <h1 className="listarTurnosTitle">Buscar Turnos</h1>

            {/* FILTROS */}
            <form onSubmit={handleBuscar}>
                <div className="filtrosContainer">
                    <select name="disciplina" value={filtros.disciplina} onChange={handleChange} required>
                        <option value="">Disciplina</option>
                        {DISCIPLINAS.map((d) => (
                            <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
                        ))}
                    </select>

                    <select name="dia" value={filtros.dia} onChange={handleChange} required>
                        <option value="">Día</option>
                        {DIAS.map((d) => (
                            <option key={d} value={d}>{d}</option>
                        ))}
                    </select>

                    <div className="horaFiltro">
                        <select name="horaHH" value={filtros.horaHH} onChange={handleChange} required>
                            <option value="">HH</option>
                            {HORAS.map((h) => (
                                <option key={h} value={h}>{h}</option>
                            ))}
                        </select>
                        <select name="horaMM" value={filtros.horaMM} onChange={handleChange} disabled={!filtros.horaHH} required>
                            <option value="">MM</option>
                            {getMinutos(filtros.horaHH).map((m) => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                    </div>

                    <button type="submit" className="buscarBtn">
                        <img src={lupa} alt="buscar" />
                    </button>
                </div>
            </form>

            {/* RESULTADOS */}
            {buscado && (
                <div className="resultadosContainer">

                    {/* BOTON ABONAR - solo si no es admin */}
                    {!esAdmin && (
                        <div className="abonarContainer">
                            <button
                                className="abonarBtn"
                                onClick={!logueado ? handleAccionNoLogueado : undefined}
                            >
                                Abonar (mensual)
                            </button>
                        </div>
                    )}

                    {/* TABLA */}
                    {turnos.length === 0 ? (
                        <p className="sinResultados">No hay turnos disponibles para este mes.</p>
                    ) : (
                        <table className="turnosTable">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Disciplina</th>
                                    <th>Día</th>
                                    <th>Hora</th>
                                    {esAdmin && <th>Cupo</th>}
                                    {!esAdmin && <th></th>}
                                </tr>
                            </thead>
                            <tbody>
                                {turnos.map((turno) => (
                                    <tr key={turno.id}>
                                        <td>{turno.fecha}</td>
                                        <td>{turno.disciplina.charAt(0).toUpperCase() + turno.disciplina.slice(1)}</td>
                                        <td>{turno.dia}</td>
                                        <td>{turno.hora}</td>
                                        {esAdmin && <td>{turno.ocupados}/{turno.cupo}</td>}
                                        {!esAdmin && (
                                            <td>
                                                <button
                                                    className="reservarBtn"
                                                    onClick={!logueado ? handleAccionNoLogueado : undefined}
                                                >
                                                    Reservar
                                                </button>
                                            </td>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}

                    {/* MENSAJE SI NO ESTA LOGUEADO */}
                    {!logueado && (
                        <p className="loginAviso">
                            Para reservar o abonar turnos tenés que <span onClick={() => navigate('/login')}>iniciar sesión</span>.
                        </p>
                    )}
                </div>
            )}
        </div>
    );
}