// will be used for role access based restrictions, and only showing navbar once you're logged in.

import HeaderNavBar from "../components/HeaderNavBar";
import { Outlet } from "react-router-dom";

export default function ProtectedLayout() {
    return (
        <>
            <HeaderNavBar />
            <Outlet />
        </>
    );
}