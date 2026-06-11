import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import "../assets/styles/PasarAsistencia.css";

const API_BASE = "http://localhost:8080";

const ESTADO = {
  SCAN:    "scan",
  LOADING: "loading",
};

export default function PasarAsistenciaPage() {
  const [estado, setEstado]     = useState(ESTADO.SCAN);

  const scannerRef              = useRef(null);
  const procesandoRef           = useRef(false);
  const navigate                = useNavigate();

  const detenerScanner = useCallback(() => {
    if (scannerRef.current) {
      scannerRef.current.stop().catch(() => {});
      scannerRef.current = null;
    }
  }, []);

  // Arranca el scanner cuando el div #qr-reader ya está en el DOM
  useEffect(() => {
    if (estado !== ESTADO.SCAN) return;

    procesandoRef.current = false;

    let scanner;

    import("html5-qrcode").then(({ Html5Qrcode }) => {
      // Si ya hay uno corriendo, no crear otro (evita duplicado en StrictMode)
      if (scannerRef.current) return;

      scanner = new Html5Qrcode("qr-reader");
      scannerRef.current = scanner;

      scanner
        .start(
          { facingMode: "environment" },
          { fps: 10, qrbox: { width: 250, height: 250 } },
          (decodedText) => {
            if (procesandoRef.current) return;
            procesandoRef.current = true;
            detenerScanner();
            enviarQR(decodedText);
          },
          () => {}
        )
        .catch(() => {
          toast.error("No se pudo acceder a la cámara. Verificá los permisos del navegador.");
        });
    });

    return () => detenerScanner();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [estado]);

  // Limpieza al desmontar
  useEffect(() => () => detenerScanner(), [detenerScanner]);

  const enviarQR = async (qrData) => {
    setEstado(ESTADO.LOADING);
    try {
      const res  = await fetch(`${API_BASE}/asistencia/registrar`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ qr_data: qrData }),
      });
      const json = await res.json();

      if (json.ok) {
        toast.success(json.mensaje);
        setEstado(ESTADO.SCAN);
      } else if (json.codigo === "PAGO_INCOMPLETO") {
        toast.error(json.mensaje);
        setEstado(ESTADO.SCAN);
      } else {
        toast.error(json.mensaje || "Ocurrió un error inesperado.");
        setEstado(ESTADO.SCAN);
      }
    } catch {
      toast.error("No se pudo conectar con el servidor.");
      setEstado(ESTADO.SCAN);
    }
  };

  const volver = () => {
    detenerScanner();
    procesandoRef.current = false;
    setEstado(ESTADO.SCAN);
  };

  return (
    <div className="pa-page">
      <div className="pa-card">

        <div className="pa-header">
          <span className="pa-logo-tag">Club 360</span>
          <h1 className="pa-titulo">Pasar asistencia por QR</h1>
        </div>

        {estado === ESTADO.SCAN    && <PantallaScan    onCancelar={() => navigate(-1)} />}
        {estado === ESTADO.LOADING && <PantallaCargando />}

      </div>
    </div>
  );
}

function PantallaScan({ onCancelar }) {
  return (
    <div className="pa-pantalla pa-pantalla--center">
      <p className="pa-instruccion">Apuntá la cámara al código QR del cliente.</p>
      <div id="qr-reader" className="pa-qr-reader" />
      <button className="pa-btn pa-btn--secondary" onClick={onCancelar}>
        Cancelar
      </button>
    </div>
  );
}

function PantallaCargando() {
  return (
    <div className="pa-pantalla pa-pantalla--center">
      <div className="pa-spinner" />
      <p className="pa-instruccion">Registrando asistencia…</p>
    </div>
  );
}