import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import "../assets/styles/LoadingSpinner.css"

export default function RejectPage() {
    const navigate = useNavigate();

    const {
        idOfrecimiento,
        idTurno,
        clienteEmisor
    } = useParams();

    useEffect(() => {
        async function rechazar() {
            try {
                const response = await fetch(
                    `/api/ofrecer/rechazar/${idOfrecimiento}/${idTurno}/${clienteEmisor}`,
                    {
                        method: "POST",
                        credentials: "include",
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    toast.error(data.error || data.mensaje || "Error al rechazar el ofrecimiento");

                    setTimeout(() => {
                        navigate("/login");
                    }, 2500);

                    return;
                }

                toast.success(
                    data.mensaje ||
                    "Ofrecimiento rechazado correctamente"
                );

                setTimeout(() => {
                    navigate("/login");
                }, 2500);

            } catch (error) {
                toast.error("Ocurrió un error inesperado");

                setTimeout(() => {
                    navigate("/login");
                }, 2500);
            }
        }

        rechazar();
    }, [idOfrecimiento, idTurno, clienteEmisor, navigate]);

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
            <h2>Procesando rechazo...</h2>
        </div>
    );
}