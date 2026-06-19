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
import ResetPasswordPage from "../pages/ResetPasswordPage";
import OlvideContrasenaPage from "../pages/OlvideContraseñaPage";
import RegisterClientAsEmployee from "../pages/RegisterClientAsEmployeePage.jsx";
import RegisterCashPaymentPage from "../pages/RegisterCashPaymentPage.jsx";
import MisPagos from "../pages/MisPagosPage.jsx";
import PasarAsistenciaPage from "../pages/PasarAsistenciaPage.jsx";
import PasarAsistenciaManualPage from "../pages/PasarAsistenciaManualPage";
import AcceptPage from "../pages/AcceptPage.jsx";
import RejectPage from "../pages/RejectPage.jsx";
import MisCreditosPage from "../pages/MisCreditosPage.jsx";
import HistorialPagosPage from "../pages/HistorialPagosPage.jsx";
import CardEditPage from "../pages/CardEditPage.jsx";
import ListarClasesPage from "../pages/ListarClasesPage.jsx";


export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 1. RUTAS PÚBLICAS (Se ven sin estar logueado) */}
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/olvide-contrasena" element={<OlvideContrasenaPage />} />
        <Route path="/ofrecer/aceptar/:idOfrecimiento/:idClienteElegido" element={<AcceptPage />}/>
        <Route path="/ofrecer/rechazar/:idOfrecimiento/:idTurno/:clienteEmisor" element={<RejectPage />}/>


        {/* 2. RUTAS PROTEGIDAS (Usan el Layout con Navbar) */}
        <Route element={<ProtectedLayout />}>

          <Route path="/" element={<HomePage/>} />
          <Route path="/card-register" element={<CardRegisterPage/>}/>
          <Route path="/mis-Actividades" element={<MisActividaes/>}/>
          <Route path="/clases/crear" element={<CrearClasePage />} />
          <Route path="/turnos" element={<ListarTurnosPage/>} />
          <Route path="/profile" element={<ProfilePage/>}/>
          <Route path="register-client" element={<RegisterClientAsEmployee/>}/>
          <Route path="register-cash" element={<RegisterCashPaymentPage/>}/>
          <Route path="/mis-pagos" element={<MisPagos />} />
          <Route path="/asistencia-qr" element={<PasarAsistenciaPage />} />
          <Route path="/asistencia-manual" element={<PasarAsistenciaManualPage />} />
          <Route path="/mis-creditos" element={<MisCreditosPage />} />
          <Route path="/historial-pagos" element={<HistorialPagosPage/>} />
          {/* <Route path="/perfil" element={<ProfilePage />} /> */}
          <Route path="/edit-card/:id" element={<CardEditPage />} />
          <Route path="/clases" element={<ListarClasesPage />} />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

