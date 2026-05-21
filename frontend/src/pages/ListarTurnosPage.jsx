import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../assets/styles/ListarTurnos.css';
import lupa from '../assets/images/lupa.png';
import ModalDialog from '../components/ModalDialog';
import { toast } from 'react-toastify';

import PaymentModal from "../components/PaymentModal";

const DISCIPLINAS = ['paddle', 'futbol', 'basquet', 'voley'];
const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
const HORAS = ['08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21'];

const getMinutos = (hora) => {
    if (hora === '21') return ['00'];
    return ['00', '15', '30', '45'];
};

const ROL_ADMINISTRADOR = 2;
const ROL_EMPLEADO = 3;

export default function ListarTurnosPage() {
    const navigate = useNavigate();

    const [session, setSession] = useState(null);
    const [filtros, setFiltros] = useState({ disciplina: '', dia: '', horaHH: '', horaMM: '' });
    const [turnos, setTurnos] = useState([]);
    const [turnosCliente, setTurnosCliente] = useState([]);
    const [buscado, setBuscado] = useState(false);
    const [cargando, setCargando] = useState(false);

    // para el modal de pagos
    const [modalOpen, setModalOpen] = useState(false);
    const [cards, setCards] = useState([]);
    const [selectedCard, setSelectedCard] = useState(null);
    const [selectedReserva, setSelectedReserva] = useState(null);
    

    useEffect(() => {
        fetch('/api/auth/status', { credentials: 'include' })
            .then(res => res.json())
            .then(data => setSession(data))
            .catch(() => setSession({ loggedIn: false }));
    }, []);

    useEffect(() => {

    if (!session?.loggedIn) return;

    const fetchTurnosCliente = async () => {
    try {
        const [resTurno, resClase] = await Promise.all([
            fetch(`/api/turnos_de_cliente?id_usuario=${session.user_id}`, { credentials: 'include' }),
            fetch(`/api/turnos_de_cliente_clase?id_usuario=${session.user_id}`, { credentials: 'include' })
        ]);

        const dataTurno = await resTurno.json();
        const dataClase = await resClase.json();

        setTurnosCliente([
            ...(dataTurno.turnos || []),
            ...(dataClase.turnos || [])
        ]);

    } catch (error) {
        console.error('Error obteniendo turnos del cliente');
    }
    };

    fetchTurnosCliente();

    }, [session]);

    const esAdmin = session?.rol_id === ROL_ADMINISTRADOR;
    const esEmpleado = session?.rol_id === ROL_EMPLEADO;
    const esPersonalInterno = esAdmin || esEmpleado;
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
            toast.error('Error al buscar turnos.');
        } finally {
            setCargando(false);
        }
    };

    const handleAccionNoLogueado = () => navigate('/login');

    const handleReservar = async (turno) => {

        try {

            const response = await fetch('/api/reservar_turno', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    id_turno: turno.id
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.mensaje);
                return;
            }

            const resCards = await fetch(
                `/api/tarjetas/${session.user_id}`,
                {
                    credentials: 'include'
                }
            );

            const cardsData = await resCards.json();

            setCards(cardsData);
            setSelectedCard(cardsData[0]);

            setSelectedReserva({
                id_reserva: data.id_reserva,
                disciplina: turno.disciplina,
                fecha: turno.fecha,
                hora: turno.hora,
                monto: data.monto_total
            });

            setModalOpen(true);

        } catch (error) {

            toast.error(
                'No se pudo conectar con el servidor.'
            );
        }
    };

        // PAGAR (boton del modal)
        const confirmPay = async () => {
            try {
                const res = await fetch("/api/pago_tarjeta", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                    body: JSON.stringify({
                        id_reserva: selectedReserva.id_reserva,
                        id_tarjeta: selectedCard.id,
                    }),
                });

                const data = await res.json();

                if (!res.ok || data.mensaje?.includes("insuficiente")) {
                    toast.error(
                        data.mensaje ||
                        data.error ||
                        "Error al procesar el pago"
                    );

                     // ELIMINA LA RESERVA SI EL PAGO FALLA
                    await handlePaymentCancelled(selectedReserva.id_reserva);
                    setModalOpen(false);
                    
                    return;
                }

                toast.success(data.mensaje);
                setModalOpen(false);

                // optional: refresh turnos instead of filtering pagos
                // setTurnos(...)
            } catch (err) {
                toast.error("Error procesando pago");
                // Delete reservation if connection fails
                await handlePaymentCancelled(selectedReserva.id_reserva);
                setModalOpen(false);
            }
        };

    const handleAbonarMensual = async () => {
        const idClase = turnos[0]?.id_clase;
        if (!idClase) {
            toast.error('No se pudo determinar la clase. Buscá los turnos nuevamente.'); 
            return;
        }

        try {
            const response = await fetch('/api/abonar_mensual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_clase: idClase }),
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.mensaje); 
                return;
            }

            let mensaje = data.mensaje;
            if (data.descuento) mensaje += ` | ${data.descuento}`;
            if (data.monto_a_pagar) mensaje += ` | Monto: $${data.monto_a_pagar}`;

            toast.success(mensaje); 

        } catch (error) {
            toast.error('No se pudo conectar con el servidor. Intentá de nuevo.'); 
        }
    };

    const handleToggleClase = async (idClase, estaHabilitada) => {
        try {
            const endpoint = estaHabilitada ? '/api/deshabilitarClase' : '/api/habilitarClase';
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_clase: idClase })
            });

            if (response.ok) {
                setTurnos(prev => prev.map(t =>
                    t.id_clase === idClase ? { ...t, habilitada: !estaHabilitada } : t
                ));
                toast.success(estaHabilitada ? 'Clase deshabilitada.' : 'Clase habilitada.'); 
            } else {
                const errData = await response.json();
                toast.error(errData.message || 'Error al cambiar estado de la clase.');
            }
        } catch (error) {
            toast.error('Error al cambiar estado de clase.');
        }
    };

    const handlePaymentCancelled = async (reservaId) => {
    try {
        const res = await fetch(`/api/cancelar_reserva/${reservaId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!res.ok) {
            toast.error('Error al cancelar la reserva');
            return;
        }

        toast.info('No se confirmó la reserva debido a la falta de pago. El turno sigue disponible.');
    } catch (error) {
        toast.error('Error al cancelar la reserva');
    }
};

    const renderBotonAccion = (turno) => {

        const turnoLleno = turno.ocupados >= turno.cupo;

        const inscripto = turnosCliente.some(
            t => t.id_turno === turno.id
        );

        if (inscripto || inscriptoEnTodosLosTurnos) return <></>;

        if (turnoLleno && !inscripto) {
            return (
                <button
                    className="listaEsperaBtn"
                    onClick={!logueado ? handleAccionNoLogueado : undefined}
                >
                    Lista de espera
                </button>
            );
        }
        else if (!inscripto && !turnoLleno){
        return (
            <button
                className="reservarBtn"
                onClick={!logueado ? handleAccionNoLogueado : () => handleReservar(turno)}
            >
                Reservar
            </button>
        );
        }
        return(<></>);
    };

    const hayAlgunTurnoLleno = turnos.some(t => t.ocupados >= t.cupo);

    const inscriptoEnTodosLosTurnosLlenos = turnos
        .filter(t => t.ocupados >= t.cupo)
        .every(t => turnosCliente.some(tc => tc.id_turno === t.id));
        
    const inscriptoEnTodosLosTurnos = turnos.length > 0 &&
    turnos.every(t => turnosCliente.some(tc => tc.id_turno === t.id));

        return (
        <div className="listarTurnosContainer">
            <h1 className="listarTurnosTitle">Buscar Turnos</h1>

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

            {buscado && (
                <div className="resultadosContainer">

                    {!esPersonalInterno && turnos.length > 0 && !(hayAlgunTurnoLleno && inscriptoEnTodosLosTurnosLlenos) && (
                        <div className="abonarContainer">
                            <button
                                className={`abonarBtn ${hayAlgunTurnoLleno ? 'listaEsperaBtn' : ''}`}
                                onClick={
                                    !logueado
                                        ? handleAccionNoLogueado
                                        : hayAlgunTurnoLleno
                                            ? undefined
                                            : handleAbonarMensual
                                }
                            >
                                {hayAlgunTurnoLleno ? 'Lista de espera (mensual)' : 'Abonar (mensual)'}
                            </button>
                        </div>
                    )}

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
                                    {esPersonalInterno && <th>Cupo</th>}
                                    {esAdmin && <th>Clase</th>}
                                    {!esPersonalInterno && <th></th>}
                                </tr>
                            </thead>
                            <tbody>
                                {turnos.map((turno) => (
                                    <tr key={turno.id}>
                                        <td>{turno.fecha}</td>
                                        <td>{turno.disciplina.charAt(0).toUpperCase() + turno.disciplina.slice(1)}</td>
                                        <td>{turno.dia}</td>
                                        <td>{turno.hora}</td>
                                        {esPersonalInterno && <td>{turno.ocupados}/{turno.cupo}</td>}
                                        {esAdmin && (
                                            <td>
                                                <button
                                                    className={turno.habilitada ? 'deshabilitarBtn' : 'habilitarBtn'}
                                                    onClick={() => handleToggleClase(turno.id_clase, turno.habilitada)}
                                                >
                                                    {turno.habilitada ? 'Deshabilitar clase' : 'Habilitar clase'}
                                                </button>
                                            </td>
                                        )}
                                        {!esPersonalInterno && (
                                            <td>{renderBotonAccion(turno)}</td>
                                        )}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}

                    {!logueado && (
                        <p className="loginAviso">
                            Para reservar o abonar turnos tenés que <span onClick={() => navigate('/login')}>iniciar sesión</span>.
                        </p>
                    )}

                    <PaymentModal
                        isOpen={modalOpen}
                        onClose={() => {
                            handlePaymentCancelled(selectedReserva?.id_reserva);
                            setModalOpen(false);
                            }}
                        cards={cards}
                        selectedCard={selectedCard}
                        setSelectedCard={setSelectedCard}
                        onConfirm={confirmPay}
                        reservaInfo={selectedReserva}
                        amount={selectedReserva?.monto ? (selectedReserva.monto / 2) + " - Seña del 50%" : 0}  // Show 50% for first payment
                    />
                </div>
            )}
        </div>
    );
}