# AUTOGENERATED! DO NOT EDIT! File to edit: ../../src/models/config_model.ipynb.

# %% auto 0
__all__ = ['Config_Model']

# %% ../../src/models/config_model.ipynb 3
from ..imports import *
from ..config_loader import *
from ..util import *
from datetime import datetime

# %% ../../src/models/config_model.ipynb 5
class Config_Model(nn.Module):
    """A basic `nn.Module` with IO functionality."""
    def __init__(self): super().__init__()
    
    #---------------------
    
    def get_config(self, save_path=None, without_metadata=False):
        if not without_metadata:       
            config = {}
            config["target"]         = class_to_str(type(self)) 
            config["save_path"]      = save_path
            config["save_datetime"]  = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            config["params"]         = self.params_config  
        else:
            config = self.params_config  
        
        self.config = config        
        return config
    
    def store_model(self, config_path: str=None, save_path: str=None, without_metadata=False):        
    
        config = self.get_config(save_path, without_metadata)
    
        if exists(config_path):
            if without_metadata: save_dataclass_yaml(config, config_path)
            else               : save_dict_yaml(config, config_path)            
                       
        if exists(save_path):
            torch.save(self.state_dict(), save_path)     
    
    #---------------------
    
    @staticmethod
    def from_config(config, device: torch.device, save_path: str=None):  
        """Use this if we have a loaded config. Maybe within other classes (e.g. pipeline and nested models)"""
        
        model = instantiate_from_config(config)
        model = model.to(device) 
        print(f"[INFO]: `{class_to_str(type(model))}` instantiated from given config on {device}.")
        
        #--------------------------------        
        if not exists(save_path):            
            if "save_path" in config:
                save_path = config["save_path"]
            else:
                print("[INFO]: Found no key `save_path` path in config.")
                                  
        if exists(save_path):
            model.load_state_dict(torch.load(save_path, map_location=torch.device(device).type, weights_only=True), strict=True)
        else:
            print(f"[INFO]: `{class_to_str(type(model))}`. No save_path` provided. No state dict loaded.")

        return model
    
    @staticmethod
    def from_config_file(config_path, device: torch.device, save_path: str=None):    
        config = load_config(config_path)
        return Config_Model.from_config(config, device, save_path)       
