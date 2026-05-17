import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {

    const [auth, setAuth] = useState({
        loggedIn: false,
        user_id: null,
        rol_id: null
    });

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("/api/auth/status", {
            credentials: "include"
        })
        .then(res => res.json())
        .then(data => {
            setAuth({
                loggedIn: data.loggedIn,
                user_id: data.user_id || null,
                rol_id: data.rol_id || null
            });
        })
        .catch(() => {
            setAuth({
                loggedIn: false,
                user_id: null,
                rol_id: null
            });
        })
        .finally(() => {
            setLoading(false);
        });
    }, []);

    return (
        <AuthContext.Provider value={{ ...auth, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}