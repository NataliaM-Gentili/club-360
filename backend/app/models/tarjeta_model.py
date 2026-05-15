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