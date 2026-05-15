import { BrowserRouter, Routes, Route } from "react-router-dom";
import ProtectedLayout from "../layout/ProtectedLayout";
import CardRegisterPage from "../pages/CardRegisterPage";
import SignUpPage from "../pages/SignUpPage.jsx";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 1. RUTAS PÚBLICAS (Se ven sin estar logueado) */}
        <Route path="/signup" element={<SignUpPage />} />
        {/* <Route path="/login" element={<LoginPage />} /> */}

        {/* 2. RUTAS PROTEGIDAS (Usan el Layout con Navbar) */}
        <Route element={<ProtectedLayout />}>
          
          {/* cambiar por CardRegisterPage para visualizar esa y idem con lo demas */}
          <Route path="/" element={<SignUpPage />} /> 
          {/* <Route path="/perfil" element={<ProfilePage />} /> */}
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

