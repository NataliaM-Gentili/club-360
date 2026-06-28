import React, { useCallback, useEffect, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import QRCode from 'react-qr-code';
import axios from 'axios';
import { toast } from 'react-toastify';
import TurnosPendientes from '../components/TurnosPendientes';
import '../assets/styles/MisActividades.css'; 

/* ── Modal ────────────────────────────────────────────────── */
function ModalTurnosDia({ fecha, turnos, onCancelar, onCerrar, cargando }) {
    const fechaLabel = new Date(fecha + 'T12:00:00').toLocaleDateString('es-AR', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    });

    return (
        <div className="mat-overlay" onClick={onCerrar}>
            <div className="mat-sheet" onClick={e => e.stopPropagation()}>
                <div className="mat-header">
                    <span className="mat-fecha">{fechaLabel}</span>
                    <button className="mat-cerrar" onClick={onCerrar}>✕</button>
                </div>

                {turnos.map(ev => {
                    const { id_turno, id_reserva, hora } = ev.extendedProps;
                    // ⚠️  Ajustar al formato que espera /asistencia/registrar
                    const qrData = JSON.stringify({ id_turno, id_reserva });

                    return (
                        <div key={id_turno} className="mat-card">
                            <p className="mat-disciplina">{ev.title}</p>
                            <p className="mat-hora">{hora} hs</p>

                            <div className="mat-qr-wrap">
                                <QRCode value={qrData} size={160} />
                                <p className="mat-qr-hint">Mostrá este código al ingresar</p>
                            </div>

                            <button
                                className="mat-btn-cancelar"
                                disabled={cargando}
                                onClick={() => onCancelar(id_reserva, id_turno)}
                            >
                                {cargando ? 'Cancelando…' : 'Cancelar turno'}
                            </button>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

/* ── Page ─────────────────────────────────────────────────── */
export default function MisActividades() {
    const [eventos, setEventos]               = useState([]);
    const [turnosDelDia, setTurnosDelDia]     = useState(null); // null = modal cerrado
    const [fechaSel, setFechaSel]             = useState(null);
    const [cargandoCancel, setCargandoCancel] = useState(false);

    // Devuelve los datos frescos para que handleCancelar los pueda usar sin
    // depender de un closure sobre el estado anterior
    const cargarEventos = useCallback(async () => {
        try {
            const { data } = await axios.get('/api/cliente/mis_actividades', { withCredentials: true });
            setEventos(data);
            return data;
        } catch {
            toast.error('No se pudieron cargar las actividades.');
            return null;
        }
    }, []);

    useEffect(() => { cargarEventos(); }, [cargarEventos]);

    const abrirDia = (dateStr) => {
        const confirmados = eventos.filter(
            ev => ev.start === dateStr && ev.extendedProps?.estado === 'confirmada'
        );
        if (!confirmados.length) return; // día sin turnos pendientes → no pasa nada
        setFechaSel(dateStr);
        setTurnosDelDia(confirmados);
    };

    const handleCancelar = async (idReserva, idTurno) => {
        if (cargandoCancel) return;
        setCargandoCancel(true);
        try {
            const { data } = await axios.post(
                '/api/cliente/cancelar_actividad',
                { id_reserva: idReserva, id_turno: idTurno },
                { withCredentials: true }
            );
            toast.success(data.mensaje || 'Turno cancelado.');

            // Recargamos y actualizamos el modal en lugar de cerrarlo,
            // por si el día tenía más de un turno
            const frescos = await cargarEventos();
            if (frescos && fechaSel) {
                const restantes = frescos.filter(
                    ev => ev.start === fechaSel && ev.extendedProps?.estado === 'confirmada'
                );
                setTurnosDelDia(restantes.length ? restantes : null);
            }
        } catch (err) {
            toast.error(err.response?.data?.error || 'Error al cancelar.');
        } finally {
            setCargandoCancel(false);
        }
    };

    const cerrarModal = () => { setTurnosDelDia(null); setFechaSel(null); };

    return (
        <div className="cardRegisterFormContainer">
            <div className="calendarioCard">
                <h1 className="cardRegisterFormTitle">Mis Actividades</h1>

                <div className="calendarWrapper">
                    <FullCalendar
                        plugins={[dayGridPlugin, interactionPlugin]}
                        initialView="dayGridMonth"
                        locale="es"
                        events={eventos}
                        height="auto"
                        contentHeight="auto"
                        aspectRatio={1.35}
                        buttonText={{ today: 'Hoy' }}
                        headerToolbar={{ left: 'prev,next today', center: 'title', right: '' }}

                        dateClick={({ dateStr }) => abrirDia(dateStr)}
                        eventClick={({ event }) => abrirDia(event.startStr)}

                        eventContent={({ event }) => {
                            const estado = event.extendedProps.estado?.toLowerCase();
                            const cancelada = estado === 'cancelada por club' || estado === 'cancelada por cliente';
                            const color = estado === 'confirmada' ? '#387246'
                                        : cancelada              ? '#972934'
                                        :                          '#6c757d';
                            return (
                                <div style={{ borderLeft: `3px solid ${color}`, paddingLeft: 6, backgroundColor: 'transparent', width: '100%' }}>
                                    <span className="evento-titulo">{event.title}</span>
                                    <span className="evento-hora">{event.extendedProps.hora} hs</span>
                                    {cancelada && <span className="evento-cancelada">Cancelada</span>}
                                </div>
                            );
                        }}

                        dayCellDidMount={({ el, date }) => {
                            if (date.toDateString() === new Date().toDateString()) {
                                const n = el.querySelector('.fc-daygrid-day-number');
                                if (n) { n.classList.add('numero-circulo'); n.style.backgroundColor = '#adb5bd'; }
                            }
                        }}

                        eventDidMount={({ el, event }) => {
                            const estado = event.extendedProps.estado?.toLowerCase();
                            if (!estado || estado === 'cancelada por cliente') return;
                            const celda = el.closest('.fc-daygrid-day');
                            if (!celda) return;
                            const n = celda.querySelector('.fc-daygrid-day-number');
                            if (!n) return;
                            const color = estado === 'confirmada'       ? '#387246'
                                        : estado === 'cancelada por club' ? '#972934'
                                        :                                    '#6c757d';
                            n.classList.add('numero-circulo');
                            n.style.backgroundColor = color;
                            el.style.backgroundColor = 'transparent';
                            el.style.border = 'none';
                            el.style.boxShadow = 'none';
                        }}
                    />
                </div>

                {turnosDelDia && (
                    <ModalTurnosDia
                        fecha={fechaSel}
                        turnos={turnosDelDia}
                        onCancelar={handleCancelar}
                        onCerrar={cerrarModal}
                        cargando={cargandoCancel}
                    />
                )}
            </div>
        </div>
    );
}