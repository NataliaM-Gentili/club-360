import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import "../assets/styles/LoadingSpinner.css"

export default function AcceptPage() {
    const navigate = useNavigate();

    const { idOfrecimiento, idClienteElegido } = useParams();

    useEffect(() => {
        async function aceptar() {
            try {
                const response = await fetch(
                    `/api/ofrecer/aceptar/${idOfrecimiento}/${idClienteElegido}`,
                    {
                        method: "POST",
                        credentials: "include",
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    toast.error(data.error || data.mensaje || "Error al aceptar el ofrecimiento");

                    setTimeout(() => {
                        navigate("/login");
                    }, 2500);

                    return;
                }

                toast.success(
                    data.mensaje ||
                    "¡Turno aceptado correctamente!"
                );

                setTimeout(() => {
                    navigate("/login");
                }, 2500);

            } catch (error) {
                print(error)
                toast.error("Ocurrió un error inesperado");

                setTimeout(() => {
                    navigate("/login");
                }, 2500);
            }
        }

        aceptar();
    }, [idOfrecimiento, idClienteElegido, navigate]);

    return (
        <div
            style={{
                minHeight: "100vh",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                gap: "1rem"
            }}
        >
            <div className="spinner" />
            <h2>Procesando aceptación...</h2>
        </div>
    );
}