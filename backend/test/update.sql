UPDATE usuario
SET contrasena = 'scrypt:32768:8:1$agI0hkii26ueleUp$069706495ba859d7b860c47dddde13bcbfbb4154d76ba2690d6d421d0d4b64f08665b20b5e3153f4680659724c1dc98c4f1e5cc1c4c731357deadd89bbeab496'
WHERE id = 5;


UPDATE reserva
SET estado = 'Pendiente'
WHERE id = 1;

DELETE FROM empleado_registra_abono
WHERE id_abono = 1;