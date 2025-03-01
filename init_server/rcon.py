import init_server.data as data

from enum import Enum
from mcdreforged.api.all import *
from .utils import get_prop_copy, get_tcp_port, load_server_prop, save_server_prop


def is_server_rcon_enabled() -> bool:
    return data.prop.get("enable-rcon", False)

def load_server_rcon_prop() -> dict:
    result = {}
    enabled = data.prop.get("enable-rcon", False)
    if enabled == "true":
        result["rcon.enable"] = True
    else:
        result["rcon.enable"] = False
    result["rcon.port"] = data.prop.get("rcon.port", None)
    result["rcon.password"] = data.prop.get("rcon.password", None)
    return result

def load_mcdr_rcon_config(server: PluginServerInterface) -> dict:
    result = {}
    MCDRConfig = server.get_mcdr_config()
    result["rcon.enable"] = MCDRConfig["rcon"]["enable"]
    result["rcon.port"] = MCDRConfig["rcon"]["port"]
    result["rcon.password"] = MCDRConfig["rcon"]["password"]
    return result

class RconSource(Enum):
    MCDR = "mcdr"
    Server = "server"
    MOD = "modify"

class RconManager:
    def __init__(self, server: PluginServerInterface, config_source: RconSource|str):
        if isinstance(config_source, str):
            config_source = RconSource(config_source)
        self.config_source = config_source
        server.logger.info(server.rtr("init_server.rcon_manager.on_init", config_source=config_source))
        load_server_prop()

    def enable(self, server: PluginServerInterface, apply_target: RconSource|str):
        if isinstance(apply_target, str):
            apply_target = RconSource(apply_target)
        if apply_target == RconSource.MCDR:
            server.modify_mcdr_config({'rcon.enable': True}) # 理论上会即刻生效
        if apply_target == RconSource.Server:
            prop_copy = get_prop_copy()
            prop_copy["enable-rcon"] = True
            save_server_prop(prop_copy) # 无法直接刷新，需要重启服务器，在命令中会做好提示

    def disable(self, server: PluginServerInterface, apply_target: RconSource|str):
        if isinstance(apply_target, str):
            apply_target = RconSource(apply_target)
        if apply_target == RconSource.MCDR:
            server.modify_mcdr_config({'rcon.enable': False})
        if apply_target == RconSource.Server:
            prop_copy = get_prop_copy()
            prop_copy["enable-rcon"] = "false"
            save_server_prop(prop_copy)

    def apply_set_auto(self, server: PluginServerInterface):
        prop_copy = get_prop_copy()
        server.modify_mcdr_config({'rcon.enable': True})
        if self.config_source == RconSource.MCDR:
            server.logger.info(server.rtr("init_server.apply_mcdr_rcon_config"))
            new_rcon_config = load_mcdr_rcon_config(server)
            valid_port = get_tcp_port(new_rcon_config["rcon.port"])
            if valid_port != new_rcon_config["rcon.port"]:
                server.modify_mcdr_config({"rcon.port": valid_port})
            prop_copy["enable-rcon"] = "true"
            prop_copy["rcon.port"] = str(valid_port)
            prop_copy["rcon.password"] = str(new_rcon_config["rcon.password"])
            save_server_prop(prop_copy)
        if self.config_source == RconSource.Server:
            prop_copy["enable-rcon"] = "true"
            valid_port = get_tcp_port(int(prop_copy["rcon.port"]))
            if valid_port != int(prop_copy["rcon.port"]):
                prop_copy["rcon.port"] = str(valid_port)
            save_server_prop(prop_copy)
            new_rcon_config = load_server_rcon_prop()
            server.modify_mcdr_config(new_rcon_config)

    def init_set_auto(self, server: PluginServerInterface):
        # 由于服务器的 server.properties 不存在，所以强制将配置源定位为MCDR，不设计其他情况
        server.modify_mcdr_config({'rcon.enable': True})
        mcdr_rcon_config = load_mcdr_rcon_config(server)
        valid_port = get_tcp_port(mcdr_rcon_config["rcon.port"])
        if valid_port != mcdr_rcon_config["rcon.port"]:
            server.modify_mcdr_config({"rcon.port": valid_port})
        prop = {}
        prop["enable-rcon"] = "true"
        prop["rcon.port"] = str(valid_port)
        prop["rcon.password"] = str(mcdr_rcon_config["rcon.password"])
        save_server_prop(prop)
    
    def apply_set_modify(self, server: PluginServerInterface, rcon_config: dict):
        valid_port = get_tcp_port(rcon_config["port"])
        rcon_mcdr_config = {
            "rcon.enable": True,
            "rcon.port": valid_port,
            "rcon.password": rcon_config["password"]
        }
        prop_copy = get_prop_copy()
        prop_copy["enable-rcon"] = "true"
        prop_copy["rcon.port"] = str(valid_port)
        prop_copy["rcon.password"] = str(rcon_config["password"])
        save_server_prop(prop_copy)
        server.modify_mcdr_config(rcon_mcdr_config)