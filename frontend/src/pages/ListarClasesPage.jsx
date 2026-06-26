import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../assets/styles/ListarTurnos.css'; 
import lupa from '../assets/images/lupa.png';
import ModalDialog from '../components/ModalDialog';
import { toast } from 'react-toastify';

const DISCIPLINAS = ['paddle', 'futbol', 'basquet', 'voley'];
const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
const HORAS = ['08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21'];

const getMinutos = (hora) => {
    if (hora === '21') return ['00'];
    return ['00', '15', '30', '45'];
};

export default function ListarClasesPage() {
    const navigate = useNavigate();
    const [clases, setClases] = useState([]);
    const [cargando, setCargando] = useState(true);
    const [tabActivo, setTabActivo] = useState('activas'); 

    const [filtros, setFiltros] = useState({ disciplina: '', dia: '', horaHH: '', horaMM: '' });
    const [filtrosAplicados, setFiltrosAplicados] = useState({ disciplina: '', dia: '', horaHH: '', horaMM: '' });

    const [confirmEliminarClase, setConfirmEliminarClase] = useState({ 
        open: false, 
        id_clase: null, 
        total_inscriptos: 0 
    });

    const fetchClases = async () => {
        try {
            const res = await fetch('/api/listar_clases', { credentials: 'include' });
            if (res.status === 403) {
                navigate('/');
                return;
            }
            const data = await res.json();
            setClases(data.clases || []);
        } catch (error) {
            toast.error("Error al cargar las clases");
        } finally {
            setCargando(false);
        }
    };

    useEffect(() => {
        fetchClases();
    }, []);

    // ----------------------------------------------------------------
    // LÓGICA DEL BUSCADOR 
    // ----------------------------------------------------------------

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name === 'horaHH') {
            setFiltros({ ...filtros, horaHH: value, horaMM: '' });
            return;
        }
        setFiltros({ ...filtros, [name]: value });
    };

    const handleBuscar = (e) => {
        e.preventDefault();
        setFiltrosAplicados(filtros);
    };

    useEffect(() => {
        if (filtros.disciplina === '' && filtros.dia === '' && filtros.horaHH === '') {
            setFiltrosAplicados({ disciplina: '', dia: '', horaHH: '', horaMM: '' });
        }
    }, [filtros]);

    const isFormEmpty = filtros.disciplina === '' && filtros.dia === '' && filtros.horaHH === '';

    // ----------------------------------------------------------------
    // LÓGICA DE ELIMINAR / REACTIVAR CLASE
    // ----------------------------------------------------------------
    
    const prepararEliminacionClase = async (idClase) => {
        try {
            const res = await fetch(`/api/calcular_impacto_clase/${idClase}`);
            const data = await res.json();
            if (data.total_inscriptos === 0) {
                // LE AGREGAMOS EL 0 ACÁ
                ejecutarEliminacionTotal(idClase, 0);
            } else {
                setConfirmEliminarClase({ 
                    open: true, 
                    id_clase: idClase, 
                    total_inscriptos: data.total_inscriptos 
                });
            }
        } catch (error) {
            toast.error("Error al calcular el impacto de la clase");
        }
    };

    // LE AGREGAMOS 'totalInscriptos' COMO PARÁMETRO
    const ejecutarEliminacionTotal = async (idClase, totalInscriptos = 0) => {
        try {
            const response = await fetch('/api/cancelar_clase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_clase: idClase })
            });

            if (response.ok) {
                // NUEVO: Verificamos si había gente para armar el mensaje
                if (totalInscriptos > 0) {
                    toast.success("Clase eliminada y alumnos notificados");
                } else {
                    toast.success("Clase eliminada con éxito");
                }
                
                setConfirmEliminarClase({ ...confirmEliminarClase, open: false });
                fetchClases(); 
            }
        } catch (error) {
            toast.error("Error al eliminar la clase");
        }
    };

    const deshabilitarTurnosVacios = async (idClase) => {
        try {
            const response = await fetch('/api/deshabilitarClase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_clase: idClase })
            });

            if (response.ok) {
                const data = await response.json();
                toast.success(data.message || "Turnos vacíos cancelados"); // <-- CORREGIDO EL MENSAJE ACÁ
                setConfirmEliminarClase({ ...confirmEliminarClase, open: false });
                fetchClases(); 
            } else {
                toast.error("Error al cancelar turnos vacíos");
            }
        } catch (error) {
            toast.error("Error de conexión");
        }
    };

    const reactivarClase = async (idClase) => {
        try {
            const response = await fetch('/api/habilitarClase', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_clase: idClase })
            });

            if (response.ok) {
                toast.success("Clase reactivada con éxito");
                fetchClases(); 
            }
        } catch (error) {
            toast.error("Error al reactivar la clase");
        }
    };

    // ----------------------------------------------------------------
    // FILTRADO Y RENDERIZADO
    // ----------------------------------------------------------------

    const clasesFiltradas = clases.filter(c => {
        let coincide = true;
        if (filtrosAplicados.disciplina && c.disciplina !== filtrosAplicados.disciplina) coincide = false;
        if (filtrosAplicados.dia && c.dia !== filtrosAplicados.dia) coincide = false;
        if (filtrosAplicados.horaHH) {
            if (filtrosAplicados.horaMM) {
                const horaFiltro = `${filtrosAplicados.horaHH}:${filtrosAplicados.horaMM}`;
                if (c.hora !== horaFiltro) coincide = false;
            } else {
                if (!c.hora.startsWith(`${filtrosAplicados.horaHH}:`)) coincide = false;
            }
        }
        return coincide;
    });

    const clasesActivas = clasesFiltradas.filter(c => c.habilitada);
    const clasesEliminadas = clasesFiltradas.filter(c => !c.habilitada);

    if (cargando) return <div className="listarTurnosContainer"><p>Cargando clases...</p></div>;

    return (
        <div className="listarTurnosContainer">
            <h1 className="listarTurnosTitle">Gestión de Clases</h1>

            <form onSubmit={handleBuscar}>
                <div className="filtrosContainer">
                    <select name="disciplina" value={filtros.disciplina} onChange={handleChange}>
                        <option value="">Disciplina</option>
                        {DISCIPLINAS.map((d) => (
                            <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
                        ))}
                    </select>

                    <select name="dia" value={filtros.dia} onChange={handleChange}>
                        <option value="">Día</option>
                        {DIAS.map((d) => (
                            <option key={d} value={d}>{d}</option>
                        ))}
                    </select>

                    <div className="horaFiltro">
                        <select name="horaHH" value={filtros.horaHH} onChange={handleChange}>
                            <option value="">HH</option>
                            {HORAS.map((h) => (
                                <option key={h} value={h}>{h}</option>
                            ))}
                        </select>
                        <select name="horaMM" value={filtros.horaMM} onChange={handleChange} disabled={!filtros.horaHH}>
                            <option value="">MM</option>
                            {getMinutos(filtros.horaHH).map((m) => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                    </div>

                    <button type="submit" className="buscarBtn" disabled={isFormEmpty}>
                        <img src={lupa} alt="buscar" />
                    </button>
                </div>
            </form>

            <div style={{ display: 'flex', gap: '15px', marginBottom: '20px', marginTop: '20px', justifyContent: 'center' }}>
                <button 
                    onClick={() => setTabActivo('activas')}
                    style={{ 
                        padding: '10px 20px', 
                        borderRadius: '8px', 
                        border: 'none', 
                        fontWeight: 'bold', 
                        cursor: 'pointer',
                        backgroundColor: tabActivo === 'activas' ? '#598849' : '#e0e0e0',
                        color: tabActivo === 'activas' ? 'white' : '#333'
                    }}
                >
                    Clases Activas ({clasesActivas.length})
                </button>
                <button 
                    onClick={() => setTabActivo('eliminadas')}
                    style={{ 
                        padding: '10px 20px', 
                        borderRadius: '8px', 
                        border: 'none', 
                        fontWeight: 'bold', 
                        cursor: 'pointer',
                        backgroundColor: tabActivo === 'eliminadas' ? '#dc3545' : '#e0e0e0',
                        color: tabActivo === 'eliminadas' ? 'white' : '#333'
                    }}
                >
                    Clases Eliminadas ({clasesEliminadas.length})
                </button>
            </div>

            <div className="resultadosContainer">
                <table className="turnosTable">
                    <thead>
                        <tr>
                        <th>Disciplina</th>
                        <th>Día</th>
                        <th>Hora</th>
                        {tabActivo === 'activas' && (
                            <>
                                <th>Inscriptos</th>
                                <th>Cupo Clase</th>
                            </>
                        )}
                        <th>Acciones</th>
                    </tr>
                    </thead>
                    <tbody>
                        {(tabActivo === 'activas' ? clasesActivas : clasesEliminadas).map((clase) => (
                            <tr key={clase.id}>
                                <td>{clase.disciplina.charAt(0).toUpperCase() + clase.disciplina.slice(1)}</td>
                                <td>{clase.dia}</td>
                                <td>{clase.hora}</td>
                                
                                {/* Si estamos en activas, mostramos las dos columnas nuevas */}
                                {tabActivo === 'activas' && (
                                    <>
                                        <td>{clase.inscriptos}</td>
                                        <td>{clase.cupo_clase}</td>
                                    </>
                                )}
                                
                                <td>
                                    {tabActivo === 'activas' ? (
                                        <button 
                                            style={{ backgroundColor: '#dc3545', color: 'white', border: 'none', padding: '6px 16px', borderRadius: '20px', cursor: 'pointer', fontWeight: 'bold' }}
                                            onClick={() => prepararEliminacionClase(clase.id)}
                                        >
                                            Eliminar clase
                                        </button>
                                    ) : (
                                        <button 
                                            style={{ backgroundColor: '#28a745', color: 'white', border: 'none', padding: '6px 16px', borderRadius: '20px', cursor: 'pointer', fontWeight: 'bold' }}
                                            onClick={() => reactivarClase(clase.id)}
                                        >
                                            Reactivar clase
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                        {(tabActivo === 'activas' ? clasesActivas : clasesEliminadas).length === 0 && (
                            <tr>
                                {/* colSpan 5 para Activas (Disciplina, Dia, Hora, Inscriptos, Cupo, Acciones) -> 6 en realidad si contamos Acciones */}
                                {/* colSpan 4 para Eliminadas (Disciplina, Dia, Hora, Acciones) */}
                                <td colSpan={tabActivo === 'activas' ? "6" : "4"} style={{ textAlign: 'center', padding: '20px' }}>
                                    No se encontraron clases que coincidan con los filtros.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table> 
            </div>
            <ModalDialog
                open={confirmEliminarClase.open}
                onClose={() => setConfirmEliminarClase({ ...confirmEliminarClase, open: false })}
                title="Eliminar Clase Completa"
                message={`En esta clase hay ${confirmEliminarClase.total_inscriptos} inscripto(s) en total. ¿Desea continuar con la eliminación total? Puede optar por deshabilitar solo los turnos sin inscriptos para resguardar a los alumnos actuales.`}
                primaryText="Continuar (cancelar todo)"
                secondaryText="Cancelar turnos vacíos"
                onPrimary={() => ejecutarEliminacionTotal(confirmEliminarClase.id_clase, confirmEliminarClase.total_inscriptos)}
                onSecondary={() => deshabilitarTurnosVacios(confirmEliminarClase.id_clase)}
                mostrarCruz={true} 
            />
        </div>
    );
}