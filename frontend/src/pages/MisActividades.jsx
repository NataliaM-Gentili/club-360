import React, { useEffect, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import axios from 'axios';
import { toast } from 'react-toastify';

import '../assets/styles/MisActividades.css'; 

export default function MisActividades() {
    const [eventos, setEventos] = useState([]);

    useEffect(() => {
        const fetchActividades = async () => {
            try {
                const response = await axios.get('/api/cliente/mis_actividades', {
                    withCredentials: true
                });
                setEventos(response.data);
            } catch (error) {
                toast.error("No se pudieron cargar las actividades.");
            }
        };
        fetchActividades();
    }, []);

    return (
        <div className="cardRegisterFormContainer"> 
            <div className="calendarioCard">
                <h1 className="cardRegisterFormTitle">Mis Actividades</h1>
                
                <div className="calendarWrapper">
                    <FullCalendar
                        plugins={[dayGridPlugin]}
                        initialView="dayGridMonth"
                        locale="es"
                        events={eventos}
                        height="auto"
                        buttonText={{ today: 'Hoy' }}
                        headerToolbar={{
                            left: 'prev,next today',
                            center: 'title',
                            right: ''
                        }}
                        
                        eventContent={(info) => {
                            const estado = info.event.extendedProps.estado?.toLowerCase();
                            const esCancelada = estado === 'cancelada por club' || estado === 'cancelada por cliente';

                            let colorBorde = '#6c757d';   // gris → asistida
                            if (estado === 'confirmada') colorBorde = '#387246';          // verde
                            if (estado === 'cancelada por club') colorBorde = '#972934';  // rojo
                            if (estado === 'cancelada por cliente') colorBorde = '#972934';

                            return (
                                <div style={{
                                    borderLeft: `3px solid ${colorBorde}`,
                                    paddingLeft: '6px',
                                    backgroundColor: 'transparent',
                                    width: '100%',
                                }}>
                                    <span className="evento-titulo">{info.event.title}</span>
                                    <span className="evento-hora">{info.event.extendedProps.hora} hs</span>
                                    {esCancelada && (
                                        <span className="evento-cancelada">Cancelada</span>
                                    )}
                                </div>
                            );
                        }}

                        dayCellDidMount={(info) => {
                            const today = new Date();
                            if (info.date.toDateString() === today.toDateString()) {
                                const numeroDia = info.el.querySelector('.fc-daygrid-day-number');
                                if (numeroDia) {
                                    numeroDia.classList.add('numero-circulo');
                                    numeroDia.style.backgroundColor = '#adb5bd'; // gris claro neutro
                                }
                            }
                        }}

                        eventDidMount={(info) => {
                            const estado = info.event.extendedProps.estado?.toLowerCase();
                            if (!estado || estado === 'cancelada por cliente') return;

                            const celda = info.el.closest('.fc-daygrid-day');
                            if (!celda) return;

                            const numeroDia = celda.querySelector('.fc-daygrid-day-number');
                            if (!numeroDia) return;

                            let colorCirculo = '#6c757d';
                            if (estado === 'confirmada') colorCirculo = '#387246';
                            if (estado === 'cancelada por club') colorCirculo = '#972934';

                            numeroDia.classList.add('numero-circulo');
                            numeroDia.style.backgroundColor = colorCirculo;

                            // sacar fondo default de FullCalendar al evento
                            info.el.style.backgroundColor = 'transparent';
                            info.el.style.border = 'none';
                            info.el.style.boxShadow = 'none';
                        }}

                        height="auto"         
                        contentHeight="auto" 
                        aspectRatio={1.35}
                    /> 
                </div>
            </div>
        </div>
    ); 
}