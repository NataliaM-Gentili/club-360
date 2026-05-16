INSERT INTO usuario (
    id,
    email,
    dni,
    nombres,
    apellido,
    contrasena,
    rol_id
)
VALUES (
    5,
    'empleado@test.com',
    '99999999',
    'Empleado',
    'Test',
    '1234',
    3
);

INSERT INTO cliente (
    id_usuario
)
VALUES (
    5
);

INSERT INTO reserva (
    id,
    id_cliente,
    estado
)
VALUES (
    1,
    5,
    'Pendiente'
);

INSERT INTO abono (
    id_reserva,
    monto,
    efectivo
)
VALUES (
    1,
    500,
    0
);