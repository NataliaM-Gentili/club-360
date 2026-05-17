// will be used for role access based restrictions, and only showing navbar once you're logged in.

import HeaderNavBar from "../components/HeaderNavBar";
import { Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function ProtectedLayout() {
    const session = useAuth();

    if (session === null) return null;

    return (
        <>
            <HeaderNavBar />
            <Outlet context={{ rol_id: session.rol_id }} />
        </>
    );
}