class Device:
    """
    Classe base para todos os dispositivos IoT na rede.
    """

    def __init__(self,
                 device_id,
                 device_type,
                 model,
                 firmware_version,
                 status,
                 last_check_in,
                 config):

        self.document["device_id"] = device_id
        self.document["device_type"] = device_type
        self.document["model"] = model
        self.document["firmware_version"] = firmware_version
        self.document["status"] = status
        self.document["last_check_in"] = last_check_in
        self.document["config"] = config # O config será preenchido nas classes filhas


    def to_mongo_document(self):
        return self.document

class Camera(Device):
    """
    Representa a Câmera, responsável pela filmagem e análise de imagem.
    """
    def __init__(self,
                 device_id,
                 location_ref,
                 model,
                 firmware_version,
                 status,
                 last_check_in,
                 resolution,
                 framerate,
                 view_angle_degrees,
                 ml_detection_enabled,
                 image_storage_policy,
                 lane_ref):
        
        self.document = {}
        self.document["location_ref"] =  location_ref
        self.document["lane_ref"] = lane_ref
        config_data = {
            "resolution": resolution,
            "framerate": framerate,
            "view_angle_degrees": view_angle_degrees,
            "ml_detection_enabled": ml_detection_enabled,
            "image_storage_policy": image_storage_policy,
        }
        
        super().__init__(
            device_id=device_id,
            device_type="camera",
            model=model,
            firmware_version=firmware_version,
            status=status,
            last_check_in=last_check_in,
            config=config_data
        )

    def to_mongo_document(self):
        return super().to_mongo_document()

class TrafficLight(Device):
    """
    Representa o Semáforo, responsável pela atuação das fases.
    """
    def __init__(self,
                 device_id,
                 location_ref,
                 model,
                 firmware_version,
                 status,
                 last_check_in,
                 phase_id,
                 lane_ref,
                 default_green_s,
                 default_yellow_s,
                 default_red_s,
                 min_red_s,
                 min_green_s,
                 pedestrian_button_active):
        
        self.document = {}
        self.document["location_ref"] =  location_ref
        self.document["phase_id"] = phase_id
        self.document["lane_ref"] = lane_ref
        config_data = {
            "default_green_s": default_green_s,
            "default_yellow_s": default_yellow_s,
            "default_red_s": default_red_s,
            "min_green_s": min_green_s,
            "min_red_s": min_red_s,
            "pedestrian_button_active": pedestrian_button_active
        }
        
        super().__init__(
            device_id=device_id,
            device_type="traffic_light",
            model=model,
            firmware_version=firmware_version,
            status=status,
            last_check_in=last_check_in,
            config=config_data
        )

    def to_mongo_document(self):
        return super().to_mongo_document()
        
class TrafficSensor(Device):
    """
    Representa o Sensor de Tráfego, responsável pela medição de fluxo.
    """
    def __init__(self,
                 device_id,
                 location_ref,
                 model,
                 firmware_version,
                 status,
                 last_check_in,
                 sampling_rate_s,
                 lane_ref,
                 detection_method,
                 velocity_threshold_kph):
        
        self.document = {}
        self.document["location_ref"] = location_ref
        self.document["lane_ref"] = lane_ref
        config_data = {
            "sampling_rate_s": sampling_rate_s,
            "detection_method": detection_method,
            "velocity_threshold_kph": velocity_threshold_kph
        }
        
        super().__init__(
            device_id=device_id,
            device_type="traffic_sensor",
            model=model,
            firmware_version=firmware_version,
            status=status,
            last_check_in=last_check_in,
            config=config_data
        )

    def to_mongo_document(self):
        return super().to_mongo_document()
