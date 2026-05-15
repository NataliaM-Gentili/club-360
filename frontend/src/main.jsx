import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import AppRoutes from './routes/AppRoutes'

// imports the toast container
import { ToastContainer, Slide } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
  <>
    <AppRoutes />
    <ToastContainer 
    	position="top-center" 
    	autoClose={3000} 
    	hideProgressBar={true}  
    	pauseOnHover
    	theme="colored"
      transition={Slide}/>
  </>
  </StrictMode>,
)
