import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import '../assets/styles/MisCreditos.css';

const ICONOS = {
  paddle: (
    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="22" fill="currentColor" opacity="0.15" />
      <ellipse cx="20" cy="18" rx="10" ry="13" stroke="currentColor" strokeWidth="3" fill="none" />
      <line x1="26" y1="28" x2="38" y2="42" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
    </svg>
  ),
  voley: (
    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="3" fill="none" />
      <path d="M24 4 Q36 14 36 24" stroke="currentColor" strokeWidth="2.5" fill="none" />
      <path d="M24 4 Q12 14 12 24" stroke="currentColor" strokeWidth="2.5" fill="none" />
      <path d="M4 24 Q14 36 24 44" stroke="currentColor" strokeWidth="2.5" fill="none" />
      <path d="M44 24 Q34 36 24 44" stroke="currentColor" strokeWidth="2.5" fill="none" />
    </svg>
  ),
  futbol: (
    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="3" fill="none" />
      <polygon points="24,10 28,18 36,18 30,24 33,33 24,28 15,33 18,24 12,18 20,18" fill="currentColor" opacity="0.5" />
    </svg>
  ),
  basquet: (
    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="3" fill="none" />
      <path d="M4 24 Q14 14 24 24 Q34 34 44 24" stroke="currentColor" strokeWidth="2.5" fill="none" />
      <line x1="24" y1="4" x2="24" y2="44" stroke="currentColor" strokeWidth="2.5" />
    </svg>
  ),
};

const COLORES = {
  paddle:  { color: '#1a73e8', label: 'Pádel' },
  voley:   { color: '#2e7d32', label: 'Vóley' },
  futbol:  { color: '#1565c0', label: 'Fútbol' },
  basquet: { color: '#e65100', label: 'Básquet' },
};

const getIcono = (d) => ICONOS[d]  || ICONOS['futbol'];
const getColor = (d) => COLORES[d]?.color || '#598849';
const getLabel = (d) => COLORES[d]?.label || (d.charAt(0).toUpperCase() + d.slice(1));

export default function MisCreditosPage() {
  const navigate = useNavigate();
  const [creditos, setCreditos]   = useState([]);
  const [cargando, setCargando]   = useState(true);

  useEffect(() => {
    // Primero verificamos la sesión, igual que en ListarTurnosPage
    fetch('/api/auth/status', { credentials: 'include' })
      .then(res => res.json())
      .then(session => {
        if (!session.loggedIn) {
          navigate('/login');
          return;
        }

        // Sesión confirmada, ahora pedimos los créditos
        return fetch('/api/creditos', { credentials: 'include' })
          .then(async (res) => {
            if (!res.ok) {
              toast.error('No se pudieron cargar los créditos.');
              return;
            }
            const data = await res.json();
            setCreditos(data.creditos || []);
          });
      })
      .catch(() => toast.error('Error de conexión con el servidor.'))
      .finally(() => setCargando(false));
  }, []);

  const handleSolicitarClase = (disciplina) => {
    navigate(`/reservar-credito/${disciplina}`);
  };


  if (cargando) {
    return (
      <div className="creditosContainer">
        <p className="creditosCargando">Cargando créditos...</p>
      </div>
    );
  }

  return (
    <div className="creditosContainer">
      <div className="creditosHeader">
        <div>
          <h1 className="creditosTitle">Mis Créditos</h1>
        </div>
      </div>

      {creditos.length === 0 ? (
        <p className="creditosVacio">No hay créditos para mostrar.</p>
      ) : (
        <div className="creditosGrid">
          {creditos.map(({ disciplina, cantidad }) => {
            const color   = getColor(disciplina);
            const label   = getLabel(disciplina);
            const agotado = cantidad === 0;

            return (
              <div key={disciplina} className="creditoCard">
                <div className="creditoCardIcon" style={{ color }}>
                  {getIcono(disciplina)}
                </div>

                <h2 className="creditoCardNombre">{label}</h2>
                <p className="creditoCardDesc">Créditos disponibles</p>
                <p className="creditoCardCantidad" style={{ color }}>
                  {cantidad} {cantidad === 1 ? 'clase' : 'clases'}
                </p>

                <button
                  className={`creditoCardBtn${agotado ? ' creditoCardBtnAgotado' : ''}`}
                  style={agotado ? {} : { borderColor: color, color }}
                  onClick={() => !agotado && handleSolicitarClase(disciplina)}
                  disabled={agotado}
                >
                  {agotado ? 'Sin créditos' : 'Solicitar clase con crédito'}
                  {!agotado && <span className="creditoCardBtnArrow">›</span>}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}