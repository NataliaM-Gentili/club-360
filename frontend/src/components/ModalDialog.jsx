import { useEffect, useRef } from "react";
import '../assets/styles/ModalDialog.css'

export default function ModalDialog({
    open,
    onClose,
    title,
    message,
    primaryText,
    secondaryText,
    onPrimary,
    onSecondary
}) {
    const dialogRef = useRef(null);

    // open / close control
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
        >
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