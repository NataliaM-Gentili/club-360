import { useEffect, useRef } from "react";
import '../assets/styles/ModalDialog.css'

// Le agregamos mostrarCruz al final de las propiedades
export default function ModalDialog({ open, onClose, title, message, primaryText, secondaryText, onPrimary, onSecondary, mostrarCruz }) {
    const dialogRef = useRef(null);

    // Control de abrir/cerrar nativo del <dialog>
    useEffect(() => {
        if (open) {
            dialogRef.current?.showModal();
        } else {
            dialogRef.current?.close();
        }
    }, [open]);

    return (
        <dialog
            ref={dialogRef}
            className="cardDialog"
            onClose={onClose}
            onClick={(e) => {
                if (e.target === dialogRef.current) {
                    onClose?.();
                }
            }}
            style={{ position: 'relative' }} // Aseguramos que la cruz se posicione bien adentro
        >
            {/* LA CRUZ MÁGICA: Solo aparece si mandan mostrarCruz={true} */}
            {mostrarCruz && (
                <button
                    type="button"
                    onClick={() => onClose?.()}
                    style={{
                        position: 'absolute',
                        top: '15px',
                        right: '15px',
                        background: 'transparent',
                        border: 'none',
                        fontSize: '26px',
                        fontWeight: 'bold',
                        color: '#666',
                        cursor: 'pointer',
                        lineHeight: '1'
                    }}
                    title="Cerrar"
                >
                    &times;
                </button>
            )}

            <h2>{title}</h2>
            <p>{message}</p>

            <div className="dialogActions">
                <button
                    type="button"
                    className="primaryBtn"
                    onClick={() => {
                        onPrimary?.();
                        onClose?.();
                    }}
                >
                    {primaryText}
                </button>

                <button
                    type="button"
                    className="secondaryBtn"
                    onClick={() => {
                        onSecondary?.();
                        onClose?.();
                    }}
                >
                    {secondaryText}
                </button>
            </div>
        </dialog>
    );
}