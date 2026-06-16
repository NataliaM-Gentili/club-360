from app import db
from app.models.db_structure import Credito


class CreditoModel:
    @staticmethod
    def get_creditos_activos_by_usuario(id_usuario):
        """
        Retorna los créditos activos agrupados por disciplina para un usuario.
        Devuelve una lista de dicts: [{ disciplina, cantidad }]
        """
        creditos = Credito.query.filter_by(id_usuario=id_usuario, activo=True).all()

        agrupados = {}
        for credito in creditos:
            disciplina = credito.disciplina.lower()
            agrupados[disciplina] = agrupados.get(disciplina, 0) + 1

        return [
            {"disciplina": disciplina, "cantidad": cantidad}
            for disciplina, cantidad in agrupados.items()
        ]

    @staticmethod
    def usar_credito(id_usuario, disciplina):
        """
        Marca un crédito activo de la disciplina indicada como inactivo.
        Retorna True si se pudo usar, False si no había créditos disponibles.
        """
        credito = Credito.query.filter_by(
            id_usuario=id_usuario, disciplina=disciplina.lower(), activo=True
        ).first()

        if not credito:
            return False

        credito.activo = False
        db.session.commit()
        return True
