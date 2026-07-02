import { createRoot } from 'react-dom/client'
import './index.css'
import AppRoutes from './routes/AppRoutes'

// imports the toast container
import { ToastContainer, Slide } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { AuthProvider } from "./hooks/AuthContext";

createRoot(document.getElementById('root')).render(
  <AuthProvider>
    <AppRoutes />
    <ToastContainer 
      position="top-center" 
      autoClose={3000} 
      hideProgressBar={true}  
      pauseOnHover
      theme="colored"
      transition={Slide}/>
  </AuthProvider>,
)
