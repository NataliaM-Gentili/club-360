from app import db
from app.models.db_structure import Cliente, TipoLista, ListaEspera, Turno, Clase


class ListaEsperaModel:
    @staticmethod
    def obtener_cliente(id_cliente):
        return Cliente.query.filter_by(id_usuario=id_cliente).first()

    @staticmethod
    def obtener_turno(id_turno):
        return Turno.query.get(id_turno)

    @staticmethod
    def obtener_clase(id_clase):
        return Clase.query.get(id_clase)

    @staticmethod
    def obtener_tipo_lista_por_nombre(nombre):
        return TipoLista.query.filter_by(nombre=nombre).first()

    @staticmethod
    def existe_en_lista(id_cliente, tipo_lista_id, turno_id=None, clase_id=None):
        query = ListaEspera.query.filter_by(
            id_cliente=id_cliente,
            tipo_lista_id=tipo_lista_id,
            turno_id=turno_id,
            clase_id=clase_id,
        )
        return query.first() is not None

    @staticmethod
    def crear_lista_espera_no_abonado(id_cliente, tipo_lista_id, id_turno):
        nueva_lista = ListaEspera(
            id_cliente=id_cliente,
            tipo_lista_id=tipo_lista_id,
            turno_id=id_turno,
            clase_id=None,
        )
        db.session.add(nueva_lista)
        db.session.commit()
        return nueva_lista

    @staticmethod
    def crear_lista_espera_abonado(id_cliente, tipo_lista_id, id_clase):
        nueva_lista = ListaEspera(
            id_cliente=id_cliente,
            tipo_lista_id=tipo_lista_id,
            clase_id=id_clase,
            turno_id=None,
        )
        db.session.add(nueva_lista)
        db.session.commit()
        return nueva_lista
