import copy
import javaproperties
import os
import socket
import random
import init_server.data as data

from typing import Any, Callable
from mcdreforged.api.all import *



psi = ServerInterface.psi()
serverDir = psi.get_mcdr_config()["working_directory"]
eula_file_path = os.path.join(serverDir, "eula.txt")
server_prop_path = os.path.join(serverDir, "server.properties")

# Usage: @execute_if(lambda: bool | Callable -> bool)
# Ported from: https://github.com/Mooling0602/MoolingUtils-MCDR/blob/main/mutils/__init__.py
def execute_if(condition: bool | Callable[[], bool]):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            actual_condition = condition() if callable(condition) else condition
            if actual_condition:
                return func(*args, **kwargs)
            return None
        return wrapper
    return decorator

def load_server_prop():
    if data.server_first_time_start:
        psi.logger.info("服务端首次启动，解压一个含有Rcon默认配置的 server.properties 文件供服务端后续补全")
        extract_file(os.path.join('resources', 'server.properties'), server_prop_path)
    if os.path.exists(server_prop_path):
        with open(server_prop_path, "r") as f:
            cache = f.read()
            data.prop = javaproperties.loads(s=cache)
            psi.logger.info("成功读取 server.properties 文件")
        
def get_prop_copy():
    copied = copy.deepcopy(data.prop)
    return copied

def save_server_prop(dict: dict):
    if dict is None or dict == {}:
        raise ValueError("dict cannot be None or empty")
    with open(server_prop_path, "w") as f:
        javaproperties.dump(props=dict, fp=f)

def extract_file(file_path, target_path):
    '''
    快速的从插件内解压资源到外部（MCDR工作目录）。
    移植于: https://github.com/Mooling0602/MoolingUtils-MCDR/blob/main/mutils/extract_file.py

    参数:
        file_path (str): 插件内资源路径
        target_path (str): 目标路径
    '''
    with psi.open_bundled_file(file_path) as file_handler:
        with open(target_path, 'wb') as target_file:
            target_file.write(file_handler.read())

def get_tcp_port(port: int):
    '''
    根据给定的端口，返回一个可用的端口。
    如果给定的端口可用，则直接返回。
    如果给定的端口不可用，则随机生成一个新的端口，直到找到可用的端口为止。
    '''
    def is_port_available(p: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', p)) != 0
    if is_port_available(port):
        return port
    while True:
        new_port = port + random.randint(-100, 100)
        if is_port_available(new_port):
            psi.logger.warning(f"Rcon port: §c{port}§r -> §a{new_port}")
            return new_port