from app import db
from app.models.db_structure import ClienteTarjeta, Cliente, Tarjeta
from datetime import datetime
class TarjetaModel:

    @staticmethod
    def registrar_tarjeta_a_cliente(id_cliente, data):
        tarjeta = Tarjeta.query.filter_by(numero=data['numero']).first()
        
        if not tarjeta:
            tarjeta = Tarjeta(
                numero=data["numero"],
                titular=data["titular"],
                fecha_vencimiento=data["fecha_vencimiento"],
                cvv=data["cvv"]
            )
            db.session.add(tarjeta)
            db.session.flush()  # Para obtener el id_tarjeta generado

        relacion_existente = ClienteTarjeta.query.filter_by(
            id_cliente=id_cliente, 
            id_tarjeta=tarjeta.id
        ).first()

        if relacion_existente:
            return {"status": "exists", "mensaje": "La tarjeta ya está asociada a este cliente"}

        # Crear manualmente el registro en la tabla intermedia
        nueva_relacion = ClienteTarjeta(
            id_cliente=id_cliente,
            id_tarjeta=tarjeta.id
        )
        
        db.session.add(nueva_relacion)
        db.session.commit()
        
        return {"status": "success", "mensaje": "Tarjeta registrada y vinculada con éxito"}


    # recupera todas las tarjetas del usuario segun su id
    @staticmethod
    def get_by_user(user_id):

        cliente = Cliente.query.filter_by(id_usuario=user_id).first()

        if not cliente:
            return []

        return (
            db.session.query(Tarjeta)
            .join(ClienteTarjeta, ClienteTarjeta.id_tarjeta == Tarjeta.id)
            .filter(ClienteTarjeta.id_cliente == cliente.id_usuario)
            .all()
        )

    