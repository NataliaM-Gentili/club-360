import { BrowserRouter, Routes, Route } from "react-router-dom";
import ProtectedLayout from "../layout/ProtectedLayout";
import CardRegisterPage from "../pages/CardRegisterPage";
import SignUpPage from "../pages/SignUpPage.jsx";
import LoginPage from "../pages/LoginPage.jsx";
import HomePage from "../pages/HomePage";
import MisActividaes from "../pages/MisActividades.jsx"
import CrearClasePage from "../pages/CrearClasePage";
import ListarTurnosPage from "../pages/ListarTurnosPage";
import ProfilePage from "../pages/ProfilePage.jsx";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 1. RUTAS PÚBLICAS (Se ven sin estar logueado) */}
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* 2. RUTAS PROTEGIDAS (Usan el Layout con Navbar) */}
        <Route element={<ProtectedLayout />}>
          
          <Route path="/" element={<HomePage/>} />
          <Route path="/card-register" element={<CardRegisterPage/>}/>
          <Route path="/mis-Actividades" element={<MisActividaes/>}/>
          <Route path="/clases/crear" element={<CrearClasePage />} />
          <Route path="/turnos" element={<ListarTurnosPage/>} />
          <Route path="/profile" element={<ProfilePage/>}/>
          {/* <Route path="/perfil" element={<ProfilePage />} /> */}
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

