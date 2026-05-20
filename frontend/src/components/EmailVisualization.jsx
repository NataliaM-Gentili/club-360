import "./EmailRecuperarPassword.css";

function EmailRecuperarPassword({ nombreUsuario = "Juan García", resetLink = "#" }) {
  return (
    <div className="emailWrapper">
      <div className="emailCard">

        {/* HEADER */}
        <div className="emailHeader">
          <div className="emailLogo">Club 360</div>

          <div className="emailIconCircle">
            {/* lock icon */}
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>

          <h1>Restablecer contraseña</h1>
          <p>Recibimos una solicitud para restablecer tu acceso.</p>
        </div>

        {/* BODY */}
        <div className="emailBody">

          <p className="emailGreeting">
            Hola, <strong>{nombreUsuario}</strong>.<br />
            Recibimos una solicitud para restablecer la contraseña de tu cuenta en Club 360.
            Si fuiste vos, hacé clic en el botón de abajo para continuar.
          </p>

          {/* Aviso expiración */}
          <div className="expiryNotice">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>Este enlace es válido por <strong>30 minutos</strong> y solo puede usarse una vez.</span>
          </div>

          {/* CTA */}
          <div className="ctaBlock">
            <a href={resetLink} className="ctaBtn">
              Restablecer contraseña
            </a>
          </div>

          {/* Separador */}
          <div className="orDivider">
            <span>o copiá el enlace manualmente</span>
          </div>

          {/* Link alternativo */}
          <div className="linkBlock">
            <p>Si el botón no funciona, pegá este enlace en tu navegador:</p>
            <a href={resetLink}>{resetLink}</a>
          </div>

          {/* Nota de seguridad */}
          <p className="securityNote">
            <strong>¿No solicitaste esto?</strong> Podés ignorar este correo con seguridad.
            Tu contraseña no cambiará a menos que hagas clic en el enlace de arriba.
          </p>

        </div>


      </div>
    </div>
  );
}

export default EmailRecuperarPassword;
