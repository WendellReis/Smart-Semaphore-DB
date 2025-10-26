class Location:
    """
        Objeto de Locations
    """
    def __init__(self,
                 location_id,
                 description,
                 city,
                 state,
                 coordinates,
                 intersection_type,
                 num_lanes,
                 traffic_volume_category):
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
        self.location_id = location_id
        self.description = description
        self.city = city
        self.state = state
        self.coordinates = coordinates
        self.intersection_type = intersection_type
        self.num_lanes = num_lanes
        self.traffic_volume_category = traffic_volume_category

    def to_mongo_document(self):
        return {
            "location_id": self.location_id,
            "description": self.description,
            "city": self.city,
            "state": self.state,
            "coordinates": self.coordinates,
            "intersection_type": self.intersection_type,
            "num_lanes": self.num_lanes,
            "traffic_volume_category": self.traffic_volume_category
        }