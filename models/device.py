class Device:
    """
    Classe base para todos os dispositivos IoT na rede.
    """

    def __init__(self,
                 device_id,
                 location_ref,
                 device_type,
                 model,
                 firmware_version,
                 status,
                 last_check_in,
                 config):

        self.device_id = device_id
        self.location_ref = location_ref
        self.device_type = device_type
        self.model = model
        self.firmware_version = firmware_version
        self.status = status
        self.last_check_in = last_check_in
        self.config = config # Objeto específico de configuração (será definido nas classes filhas)

    def to_mongo_document(self):
        document = {
            "device_id": self.device_id,
            "location_ref": self.location_ref,
            "device_type": self.device_type,
            "model": self.model,
            "firmware_version": self.firmware_version,
            "status": self.status,
            "last_check_in": self.last_check_in, 
            "config": self.config
        }
        return document

class EdgeGateway(Device):
    """
    Representa o Controlador de Tráfego Local (CTL).
    """
    def __init__(self,
                 device_id,
                 location_ref,
                 model,
                 firmware_version,
                 status,
                 last_check_in,
                 control_mode,
                 max_cycle_time_s,
                 ml_model_version):
        
        config_data = {
            "control_mode": control_mode,
            "max_cycle_time_s": max_cycle_time_s,
            "ml_model_version": ml_model_version
        }
        
        super().__init__(
            device_id=device_id,
            location_ref=location_ref,
            device_type="edge_gateway",
            model=model,
            firmware_version=firmware_version,
            status=status,
            last_check_in=last_check_in,
            config=config_data
        )

    def to_mongo_document(self):
        return super().to_mongo_document()

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
                 lane_description):
        
        config_data = {
            "resolution": resolution,
            "framerate": framerate,
            "view_angle_degrees": view_angle_degrees,
            "ml_detection_enabled": ml_detection_enabled,
            "image_storage_policy": image_storage_policy,
            "lane_description":lane_description
        }
        
        super().__init__(
            device_id=device_id,
            location_ref=location_ref,
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
                 lane_description,
                 default_green_s,
                 default_yellow_s,
                 default_red_s,
                 min_red_s,
                 min_green_s,
                 pedestrian_button_active):
        

        config_data = {
            "phase_id": phase_id,
            "lane_description": lane_description,
            "default_green_s": default_green_s,
            "fefault_yellow_s": default_yellow_s,
            "fefault_red_s": default_red_s,
            "min_green_s": min_green_s,
            "min_red_s": min_red_s,
            "pedestrian_button_active": pedestrian_button_active
        }
        
        super().__init__(
            device_id=device_id,
            location_ref=location_ref,
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
    Representa o Sensor de Tráfego (Ex: loop indutivo), responsável pela medição de fluxo.
    """
    def __init__(self,
                 device_id,
                 location_ref,
                 model,
                 firmware_version,
                 status,
                 last_check_in,
                 sampling_rate_s,
                 lane_description,
                 detection_method,
                 velocity_threshold_kph):
        
        config_data = {
            "sampling_rate_s": sampling_rate_s,
            "lane_description": lane_description,
            "detection_method": detection_method,
            "velocity_threshold_kph": velocity_threshold_kph
        }
        
        super().__init__(
            device_id=device_id,
            location_ref=location_ref,
            device_type="traffic_sensor",
            model=model,
            firmware_version=firmware_version,
            status=status,
            last_check_in=last_check_in,
            config=config_data
        )

    def to_mongo_document(self):
        return super().to_mongo_document()
