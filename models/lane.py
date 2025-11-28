class Lane:
    """
        Objeto de Lane
    """
    def __init__(self,
                 lane_id,
                 direction,
                 lane_type,
                 description,
                 location_ref):
        """
        :param location_id: Chave primária do cruzamento (ex: LOC-001).
        :param description: Nome ou descrição do cruzamento.
        :param city: Cidade onde o cruzamento está localizado.
        :param state: Estado onde o cruzamento está localizado.
        :param coordinates: Coordeandas geogŕaficas.
        :param intersection_type: Tipo de configuração viária (ex: T-junction).
        :param num_lanes: Número total de faixas de rodagem na intersecção.
        :param traffic_volume_category: Categoria de volume de tráfego (ex: high, medium, low).
        """
        self.lane_id = lane_id
        self.direction = direction
        self.lane_type = lane_type
        self.description = description
        self.localtion_ref = location_ref

    def to_mongo_document(self):
        return {
            "lane_id":self.lane_id,
            "direction":self.direction,
            "lane_type":self.lane_type,
            "description":self.description,
            "location_ref":self.localtion_ref
        }