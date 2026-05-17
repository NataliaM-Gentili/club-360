import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export function useAuth() {
    const navigate = useNavigate();
    const [session, setSession] = useState(null);

    useEffect(() => {
        fetch("/api/auth/status", { credentials: "include" })
            .then((res) => res.json())
            .then((data) => {
                if (!data.loggedIn) {
                    navigate("/login");
                } else {
                    setSession(data);
                }
            })
            .catch(() => navigate("/login"));
    }, []);

    return session;
}