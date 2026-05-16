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
                // conexion con back
                const response = await axios.get('http://127.0.0.1:5000/api/cliente/mis_actividades', {
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
                        
                        eventContent={(info) => (
                            <div className="evento-texto-container">
                                <span className="evento-titulo">{info.event.title}</span>
                                <span className="evento-hora">{info.event.extendedProps.hora} hs</span>
                            </div>
                        )}

                        dayCellDidMount={(info) => {
                            const today = new Date();
                            
                            // resaltar dia de hoy
                            if (info.date.toDateString() === today.toDateString()) {
                                info.el.style.backgroundColor = '#85ad88'; 
                            }
                            
                            const fechaCelda = info.date.toISOString().split('T')[0];
                            
                            // canceladas por cliente (no tener en cuenta)
                            const ev = eventos.find(e => 
                                e.start === fechaCelda && 
                                e.extendedProps.estado.toLowerCase() !== 'cancelada por cliente'
                            );
                            
                            if (ev) {
                                const numeroDia = info.el.querySelector('.fc-daygrid-day-number');
                                if (numeroDia) {
                                    const estado = ev.extendedProps.estado.toLowerCase();
                                    let colorCirculo = '#6c757d'; // pasada

                                    if (estado === 'confirmada') colorCirculo = '#387246'; // futura
                                    if (estado === 'cancelada por club') colorCirculo = '#972934'; // cancelada

                                    numeroDia.classList.add('numero-circulo');
                                    numeroDia.style.backgroundColor = colorCirculo;
                                }
                            }
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