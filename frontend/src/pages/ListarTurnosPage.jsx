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
    const [listasEspera, setListasEspera] = useState({ abonado: [], noAbonado: [] });
    const [buscado, setBuscado] = useState(false);
    const [cargando, setCargando] = useState(false);

    const [modalOpen, setModalOpen] = useState(false);
    const [cards, setCards] = useState([]);
    const [selectedCard, setSelectedCard] = useState(null);
    const [selectedReserva, setSelectedReserva] = useState(null);
    const [confirmDeleteModal, setConfirmDeleteModal] = useState(false);
    const [listaAEliminar, setListaAEliminar] = useState(null);
    const [esListaMensual, setEsListaMensual] = useState(false);
    const [abonoModalOpen, setAbonoModalOpen] = useState(false);
    const [abonoModalData, setAbonoModalData] = useState(null);

    // Estados para los modales de cancelación
    const [turnoACancelar, setTurnoACancelar] = useState(null);
    const [confirmCancelarClase, setConfirmCancelarClase] = useState({ 
        open: false, 
        id_clase: null, 
        total_inscriptos: 0 
    });

    useEffect(() => {
        fetch('/api/auth/status', { credentials: 'include' })
            .then(res => res.json())
            .then(data => setSession(data))
            .catch(() => setSession({ loggedIn: false }));
    }, []);

    const fetchTurnosCliente = async () => {
        if (!session?.loggedIn) return;

        try {
            const [resTurno, resClase, resListasEspera] = await Promise.all([
                fetch(`/api/turnos_de_cliente?id_usuario=${session.user_id}`, { credentials: 'include' }),
                fetch(`/api/turnos_de_cliente_clase?id_usuario=${session.user_id}`, { credentials: 'include' }),
                fetch(`/api/listas-espera/${session.user_id}`, { credentials: 'include' })
            ]);

            const dataTurno = await resTurno.json();
            const dataClase = await resClase.json();
            const dataListasEspera = await resListasEspera.json();

            setTurnosCliente([
                ...(dataTurno.turnos || []),
                ...(dataClase.turnos || [])
            ]);

            const listas = dataListasEspera.listas || [];
            setListasEspera({
                abonado: listas.filter(item => item.clase_id != null),
                noAbonado: listas.filter(item => item.turno_id != null),
            });
        } catch (error) {
            console.error('Error obteniendo turnos del cliente');
        }
    };

    useEffect(() => {
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

    const isFormValid = filtros.disciplina !== '' && filtros.dia !== '' && filtros.horaHH !== '' && filtros.horaMM !== '';

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
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_turno: turno.id }),
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.mensaje);
                return;
            }

            const resCards = await fetch(`/api/tarjetas/${session.user_id}`, { credentials: 'include' });
            const cardsData = await resCards.json();

            setCards(cardsData);
            setSelectedCard(cardsData[0]);
            setSelectedReserva({
                id_reserva: data.id_reserva,
                id_turno: turno.id,
                id_clase: turno.id_clase,
                disciplina: turno.disciplina,
                fecha: turno.fecha,
                hora: turno.hora,
                monto: data.monto_total
            });

            setModalOpen(true);
        } catch (error) {
            toast.error('No se pudo conectar con el servidor.');
        }
    };

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
                toast.error(data.mensaje || data.error || "Error al procesar el pago");
                await handlePaymentCancelled(selectedReserva.id_reserva);
                setModalOpen(false);
                return;
            }

            toast.success(data.mensaje);
            setModalOpen(false);

            // Actualizar turnosCliente después de reserva exitosa
            setTurnosCliente(prev => [
                ...prev,
                {
                    id_reserva: selectedReserva.id_reserva,
                    id_turno: selectedReserva.id_turno,
                    fecha: selectedReserva.fecha,
                    disciplina: selectedReserva.disciplina,
                    hora: selectedReserva.hora,
                }
            ]);
        } catch (err) {
            toast.error("Error procesando pago");
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

            await fetchTurnosCliente();

            const ocupadosIds = data.turnos_ocupados || [];
            const ocupados = turnos.filter((turno) => ocupadosIds.includes(turno.id));
            const inscriptos = turnos.filter((turno) => !ocupadosIds.includes(turno.id));

            if (ocupados.length > 0) {
                const montoInfo = `Monto: $${data.monto_a_pagar}` + (data.descuento ? ` | ${data.descuento}` : '');
                const message = `Te inscribiste en ${inscriptos.length} turno(s).\n` +
                    `Los siguientes turnos están completos:\n` +
                    ocupados.map((turno) => `- ${turno.fecha} ${turno.hora}`).join('\n') +
                    `\n\n${montoInfo}\n\n¿Querés inscribirte en lista de espera para esos turnos?`;

                setAbonoModalData({ ocupados, inscriptos, mensaje: message });
                setAbonoModalOpen(true);
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

    const handleListaEsperaNoAbonado = async (turno) => {
        try {
            const response = await fetch(`/api/lista-espera/${session.user_id}/${turno.id}/3`, {
                method: 'POST',
                credentials: 'include',
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.mensaje || 'Error al agregar a lista de espera');
                return;
            }

            setListasEspera(prev => ({
                abonado: prev.abonado,
                noAbonado: [...prev.noAbonado, {
                    id: data.id,
                    id_cliente: session.user_id,
                    clase_id: null,
                    turno_id: turno.id,
                    tipo_lista_id: 3
                }],
            }));

            toast.success(data.mensaje || 'Te has agregado a la lista de espera');
        } catch (error) {
            toast.error('No se pudo conectar con el servidor.');
        }
    };

    const handleInscribirseListaEsperaTurnosOcupados = async () => {
        if (!abonoModalData?.ocupados?.length) {
            setAbonoModalOpen(false);
            return;
        }

        const resultados = await Promise.all(abonoModalData.ocupados.map(async (turno) => {
            try {
                const response = await fetch(`/api/lista-espera/${session.user_id}/${turno.id}/2`, {
                    method: 'POST',
                    credentials: 'include',
                });
                const data = await response.json();
                return { turno, ok: response.ok, data };
            } catch (error) {
                return { turno, ok: false, data: { mensaje: 'Error de conexión' } };
            }
        }));

        const exitosos = resultados.filter(r => r.ok);
        const fallidos = resultados.filter(r => !r.ok);

        if (exitosos.length > 0) {
            setListasEspera(prev => ({
                abonado: prev.abonado,
                noAbonado: [
                    ...prev.noAbonado,
                    ...exitosos.map((resultado) => ({
                        id: resultado.data.id,
                        id_cliente: session.user_id,
                        clase_id: null,
                        turno_id: resultado.turno.id,
                        tipo_lista_id: 3,
                    }))
                ]
            }));
        }

        if (fallidos.length > 0) {
            toast.error(`No se pudo inscribir en lista de espera para ${fallidos.length} turno(s).`);
        }

        if (exitosos.length > 0) {
            toast.success(`Te inscribiste en lista de espera para ${exitosos.length} turno(s).`);
        }

        setAbonoModalOpen(false);
        setAbonoModalData(null);
    };

    const handleSalirListaEspera = (idLista, esMensual) => {
        setListaAEliminar(idLista);
        setEsListaMensual(esMensual);
        setConfirmDeleteModal(true);
    };

    const confirmSalirListaEspera = async () => {
        try {
            let response = await fetch(`/api/lista-espera/salir/${session.user_id}/${listaAEliminar}`, {
                method: 'DELETE',
                credentials: 'include',
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.mensaje || 'Error al salir de la lista de espera');
                return;
            }

            setListasEspera(prev => ({
                abonado: esListaMensual ? prev.abonado.filter(item => item.id !== listaAEliminar) : prev.abonado,
                noAbonado: !esListaMensual ? prev.noAbonado.filter(item => item.turno_id !== listaAEliminar) : prev.noAbonado,
            }));

            toast.success(data.mensaje || 'Saliste de la lista de espera');
            setConfirmDeleteModal(false);
        } catch (error) {
            toast.error('No se pudo conectar con el servidor.');
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
                    t.id_clase === idClase ? { 
                        ...t, 
                        habilitada: !estaHabilitada,
                        // SI estamos deshabilitando (true) y el turno no tiene inscriptos, lo marcamos como cancelado
                        // SI estamos habilitando de nuevo (false), limpiamos la cancelación para que vuelvan a estar activos
                        turno_cancelado: estaHabilitada ? (t.ocupados === 0 ? true : t.turno_cancelado) : false
                    } : t
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

    // Nueva lógica de Cancelar Turno (con modal)
    const intentarCancelarTurno = (turno) => {
        if (turno.ocupados > 0) {
            setTurnoACancelar(turno);
        } else {
            ejecutarCancelacionTurno(turno.id);
        }
    };

    const ejecutarCancelacionTurno = async (idTurno) => {
        try {
            const response = await fetch('/api/cancelar_turno', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_turno: idTurno })
            });

            const data = await response.json();
            
            if (response.ok) {
                toast.success(data.mensaje);
                // NUEVO: Lo dejamos en pantalla, le ponemos ocupados 0 y avisamos que está cancelado
                setTurnos(prev => prev.map(t => 
                    t.id === idTurno ? { ...t, ocupados: 0, turno_cancelado: true } : t
                ));
                setTurnoACancelar(null); 
            } else {
                toast.error(data.error || 'Error al cancelar');
            }
        } catch (error) {
            console.error("Error:", error);
            toast.error('Error de conexión con el servidor');
        }
    };

    // Lógica para Cancelar Clase (con modal)
    const prepararCancelacionClase = async (idClase) => {
        try {
            const res = await fetch(`/api/calcular_impacto_clase/${idClase}`);
            const data = await res.json();
            if (data.total_inscriptos === 0) {
                ejecutarCancelacionClase(idClase);
            } else {
                setConfirmCancelarClase({ 
                    open: true, 
                    id_clase: idClase, 
                    total_inscriptos: data.total_inscriptos 
                });
            }
        } catch (error) {
            toast.error("Error al calcular impacto");
        }
    };

    const ejecutarCancelacionClase = async (idClase) => {
        try {
            const response = await fetch('/api/cancelar_clase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_clase: idClase })
            });

            if (response.ok) {
                toast.success("Clase cancelada correctamente");
                setConfirmCancelarClase({ ...confirmCancelarClase, open: false });
                
                setTurnos(prev => prev.map(t => 
                    t.id_clase === idClase ? { ...t, habilitada: false, ocupados: 0, turno_cancelado: true } : t
                ));
            }
        } catch (error) {
            toast.error("Error al cancelar la clase");
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

    const inscriptoEnTodosLosTurnos = turnos.length > 0 &&
        turnos.every(t => turnosCliente.some(tc => tc.id_turno === t.id));

    const estaEnListaEsperaIndividual = (idTurno) => {
        return listasEspera.noAbonado.some(item => item.turno_id === idTurno);
    };

    const todosTurnosCubiertosPorReservaOLista = turnos.length > 0 &&
        turnos.every(t =>
            turnosCliente.some(tc => tc.id_turno === t.id) ||
            estaEnListaEsperaIndividual(t.id)
        );

    const renderBotonAccion = (turno) => {
        const turnoLleno = turno.ocupados >= turno.cupo;
        const inscripto = turnosCliente.some(t => t.id_turno === turno.id);
        const entradaMensual = listasEspera.abonado.find(item => item.clase_id === turno.id_clase);
        const entradaIndividual = listasEspera.noAbonado.find(item => item.turno_id === turno.id);
        const enListaMensual = !!entradaMensual;
        const enListaIndividual = !!entradaIndividual;

        if (enListaIndividual) {
            return (
                <button
                    className="listaEsperaBtn"
                    style={{ backgroundColor: '#c0392b', borderColor: '#c0392b', color: '#fff' }}
                    onClick={
                        !logueado
                            ? handleAccionNoLogueado
                            : () => handleSalirListaEspera(turno.id, false)
                    }
                >
                    Salir de lista de espera
                </button>
            );
        }

        if (inscripto || inscriptoEnTodosLosTurnos) {
            return (
                <button className="reservarBtn" disabled>
                    Reservar
                </button>
            );
        }

        if (enListaMensual && turnoLleno) {
            return (
                <button className="listaEsperaBtn" disabled>
                    En lista de espera mensual
                </button>
            );
        }

        if (turnoLleno) {
            return (
                <button
                    className="listaEsperaBtn"
                    onClick={
                        !logueado
                            ? handleAccionNoLogueado
                            : () => handleListaEsperaNoAbonado(turno)
                    }
                >
                    Lista de Espera
                </button>
            );
        }

        return (
            <button
                className="reservarBtn"
                onClick={
                    !logueado
                        ? handleAccionNoLogueado
                        : () => handleReservar(turno)
                }
            >
                Reservar
            </button>
        );
    };

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

                    <button type="submit" className="buscarBtn" disabled={!isFormValid}>
                        <img src={lupa} alt="buscar" />
                    </button>
                </div>
            </form>

            {buscado && (
                <div className="resultadosContainer">

                    {!esPersonalInterno && turnos.length > 0 && !inscriptoEnTodosLosTurnos && !todosTurnosCubiertosPorReservaOLista && (
                        <div className="abonarContainer">
                            <button
                                className="abonarBtn"
                                onClick={
                                    !logueado
                                        ? handleAccionNoLogueado
                                        : handleAbonarMensual
                                }
                            >
                                Abonar (mensual)
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
                                                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                                    
                                                    {/* COLUMN 1: ESTADO Y ACCIÓN DEL TURNO INDIVIDUAL */}
                                                    {!turno.turno_cancelado ? (
                                                        <button 
                                                            className="cancelarTurnoBtn" 
                                                            style={{ 
                                                                backgroundColor: '#dc3545', 
                                                                color: 'white', 
                                                                border: 'none', 
                                                                padding: '6px 16px', 
                                                                borderRadius: '20px',
                                                                cursor: 'pointer',
                                                                fontSize: '0.85rem',
                                                                fontWeight: 'bold'
                                                            }}
                                                            onClick={() => intentarCancelarTurno(turno)} 
                                                        >
                                                            Cancelar turno
                                                        </button>
                                                    ) : (
                                                        <span style={{ fontSize: '0.85rem', color: '#dc3545', fontWeight: 'bold', padding: '6px 10px' }}>
                                                            Turno Cancelado
                                                        </span>
                                                    )}

                                                    {/* COLUMN 2: ESTADO Y ACCIÓN DE LA CLASE COMPLETA */}
                                                    {turno.habilitada ? (
                                                        <button 
                                                            className="cancelarClaseBtn" 
                                                            style={{ 
                                                                backgroundColor: '#6c757d', 
                                                                color: 'white', 
                                                                border: 'none', 
                                                                padding: '6px 16px', 
                                                                borderRadius: '20px',
                                                                cursor: 'pointer',
                                                                fontSize: '0.85rem',
                                                                fontWeight: 'bold'
                                                            }}
                                                            onClick={() => prepararCancelacionClase(turno.id_clase)} 
                                                        >
                                                            Cancelar clase
                                                        </button>
                                                    ) : (
                                                        <button 
                                                            className="habilitarBtn" 
                                                            style={{ 
                                                                backgroundColor: '#28a745', 
                                                                color: 'white', 
                                                                border: 'none', 
                                                                padding: '6px 16px', 
                                                                borderRadius: '20px',
                                                                cursor: 'pointer',
                                                                fontSize: '0.85rem',
                                                                fontWeight: 'bold'
                                                            }}
                                                            onClick={() => handleToggleClase(turno.id_clase, false)}
                                                        >
                                                            Habilitar clase
                                                        </button>
                                                    )}
                                                    
                                                </div>
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
                        amount={selectedReserva?.monto ? (selectedReserva.monto / 2) + " - Seña del 50%" : 0}
                    />

                    <ModalDialog
                        open={confirmDeleteModal}
                        onClose={() => setConfirmDeleteModal(false)}
                        title="⚠️ Atención"
                        message={"¿Está seguro que quiere salir de la lista de espera? Ésta acción no se puede deshacer y perderá su prioridad."}
                        primaryText="Confirmar"
                        secondaryText="Cancelar"
                        onPrimary={confirmSalirListaEspera}
                        onSecondary={() => setConfirmDeleteModal(false)}
                    />

                    <ModalDialog
                        open={abonoModalOpen}
                        onClose={() => {
                            setAbonoModalOpen(false);
                            setAbonoModalData(null);
                        }}
                        title="Abono mensual"
                        message={abonoModalData?.mensaje || ''}
                        primaryText="Sí, inscribirme en lista de espera"
                        secondaryText="Cerrar"
                        onPrimary={handleInscribirseListaEsperaTurnosOcupados}
                        onSecondary={() => {
                            setAbonoModalOpen(false);
                            setAbonoModalData(null);
                        }}
                    />

                    {/* NUEVO MODAL: Confirmación individual de Turno */}
                    <ModalDialog
                        open={turnoACancelar !== null}
                        onClose={() => setTurnoACancelar(null)}
                        title="Cancelar Turno"
                        message={`Este turno tiene ${turnoACancelar?.ocupados} inscripto(s). Se les notificará por correo y se procesará la devolución del dinero. ¿Desea continuar?`}
                        primaryText="Sí, cancelar turno"
                        secondaryText="Cerrar"
                        onPrimary={() => ejecutarCancelacionTurno(turnoACancelar?.id)}
                        onSecondary={() => setTurnoACancelar(null)}
                    />

                    {/* MODAL EXISTENTE: Confirmación para toda la Clase */}
                    <ModalDialog
                        open={confirmCancelarClase.open}
                        onClose={() => setConfirmCancelarClase({ ...confirmCancelarClase, open: false })}
                        title="Cancelar Clase Completa"
                        message={`En esta clase hay ${confirmCancelarClase.total_inscriptos} inscripto(s) en total. ¿Desea continuar con la cancelación? Puede optar por deshabilitar la clase para eliminar solo los turnos sin inscriptos.`}
                        primaryText="Continuar (Cancelar todo)"
                        secondaryText="Deshabilitar turnos vacíos"
                        onPrimary={() => ejecutarCancelacionClase(confirmCancelarClase.id_clase)}
                        onSecondary={() => {
                            handleToggleClase(confirmCancelarClase.id_clase, true);
                            setConfirmCancelarClase({ ...confirmCancelarClase, open: false });
                        }}
                    />
                </div>
            )}
        </div>
    );
}