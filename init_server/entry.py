import time
import init_server.data as data
import os

from mcdreforged.api.all import *
from .eula import is_eula_agreed, set_eula
from .init import is_server_first_start
from .utils import eula_file_path, extract_file, server_prop_path, execute_if
from .commands import register_command
from .rcon import RconManager


default_config = {
    "auto_agree_eula": True,
    "auto_set_rcon": True,
    "quick_control": False
}

on_server_init = is_server_first_start()

def on_load(server: PluginServerInterface, prev_module):
    data.config = server.load_config_simple('config.yml', default_config)
    if on_server_init and data.config == default_config:
        server.logger.info(server.rtr("init_server.on_server_init"))
        server.logger.info(server.rtr("init_server.wait_for_init_plz"))
    if server.get_mcdr_language() != 'zh_cn':
        server.logger.warning("English is all translated from Chinese Simplified by Copilot in VSCode.")
    load_task(server) # 加载初始化/自动任务
    register_command(server) # 注册命令

def load_task(server: PluginServerInterface):
    if on_server_init:
        data.set_mcdr_alive = True # 设置MCDR不随服务端退出方便服务端首次启动后初始化服务器配置
    # EULA初始化任务
    if data.config["auto_agree_eula"]:
        extract_file(os.path.join('resources', 'eula.txt'), eula_file_path) if on_server_init else set_eula(server) # 自动同意EULA
    else:
        if not is_eula_agreed():
            server.logger.warning(server.rtr("init_server.config_not_enabled.auto_agree_eula"))
            data.need_agree_eula = True # 触发服务器关闭后的提示
    # RCON初始化任务
    if data.config["auto_set_rcon"]:
        if not is_server_first_start():
            if not server.is_rcon_running():
                server.logger.info(server.rtr("init_server.start_rcon_set_task"))
                rcon_maneger = RconManager(server, "mcdr")
                rcon_maneger.apply_set_auto(server)
            else:
                server.logger.info(server.rtr("init_server.no_need_to_init_rcon"))
        else:
            rcon_maneger = RconManager(server, "mcdr")
            rcon_maneger.init_set_auto(server)
    else:
        if not server.is_rcon_running():
            server.logger.warning(server.rtr("init_server.config_not_enabled.auto_set_rcon"))

@execute_if(lambda: data.set_mcdr_alive is True)
# 在需要时设置MCDR不随服务端退出
def on_server_start(server: PluginServerInterface):
    server.set_exit_after_stop_flag(False)

def on_server_startup(server: PluginServerInterface):
    if data.config["auto_set_rcon"]:
        if server.is_rcon_running():
            server.set_exit_after_stop_flag(True)
            if data.config["auto_agree_eula"]:
                server.logger.info(server.rtr("init_server.on_init_complete")) # 有人反馈这个提示太烦我再设计成可以关闭的，不然就这样了（插件的特色就是细致而周到的各种提示
                for k, v in data.init_tasks.items():
                    data.init_tasks[k] = True

@execute_if(lambda: data.server_first_time_start is True or data.need_agree_eula is True)
# 仅在服务端因拒绝EULA或首次启动还没初始化EULA而关闭时，执行初始化方面的配置任务
def on_server_stop(server: PluginServerInterface, code: int):
    if code == 0:
        if not all(data.init_tasks.values()):
            control_tips = [
                server.rtr("init_server.control_tips.a"),
                server.rtr("init_server.control_tips.b"),
                server.rtr("init_server.control_tips.c"),
                server.rtr("init_server.control_tips.d")
            ]
            for i in control_tips:
                server.logger.warning(i)
        if not data.config["auto_set_rcon"]:
            multi_line_message = [
                server.rtr("init_server.set_rcon_tips.a"),
                server.rtr("init_server.set_rcon_tips.b"),
                server.rtr("init_server.set_rcon_tips.c")
            ]
            for i in multi_line_message:
                server.logger.warning(i)
        else:
            set_eula(server) if data.need_agree_eula else None
        if not data.config["auto_agree_eula"]:
            multi_line_message = [
                server.rtr("init_server.agree_eula_tips.a"),
                server.rtr("init_server.agree_eula_tips.b"),
                server.rtr("init_server.agree_eula_tips.c")
            ]
            for i in multi_line_message:
                server.logger.warning(i)
        if not all(data.init_tasks.values()):
            check_init_tasks(server)
    else:
        server.logger.warning(server.rtr("init_server.on_server_crash"))
        server.stop_exit()

@new_thread("WaitForInitTasks")
def check_init_tasks(server: PluginServerInterface):
    if all(data.init_tasks.values()):
        server.logger.info(server.rtr("init_server.on_init_apply"))
        server.start()
        server.reload_plugin("init_server")
    else:
        time.sleep(1)
        check_init_tasks(server)