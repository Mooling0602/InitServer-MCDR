import init_server.data as data

from ..eula import set_eula
from ..utils import execute_if, get_prop_copy, save_server_prop
from mcdreforged.api.all import *


psi = ServerInterface.psi()
builder = SimpleCommandBuilder()

def register_command(server: PluginServerInterface):
    builder.arg('port', Text)
    builder.arg('password', Text)
    builder.register(server)

@builder.command('!!eula auto-set enable')
@builder.command('!set-eula')
def on_auto_set_eula_enable(src: CommandSource):
    if src.is_console:
        psi.save_config_simple({"auto_agree_eula": True, "auto_set_rcon": data.config["auto_set_rcon"]}, 'config.yml')
        data.config["auto_agree_eula"] = True
        data.init_tasks["eula"] = True
        if psi.is_server_running():
            src.reply(psi.rtr("init_server.do_restart_server"))
        else:
            tasks_count_ok = sum(data.init_tasks.values())
            sum_tasks = len(data.init_tasks)
            process=f"{tasks_count_ok}/{sum_tasks}"
            src.reply(psi.rtr("init_server.init_process", process=process))
            if tasks_count_ok < sum_tasks:
                src.reply(psi.rtr("init_server.init_tip"))
    else:
        src.reply(psi.rtr("init_server.execute_in_console_please"))

@builder.command('!!eula agree')
def on_agree_eula(src: CommandSource):
    src.reply(psi.rtr("init_server.agree_eula"))
    if src.is_console:
        set_eula(psi)
    else:
        src.reply(psi.rtr("init_server.execute_in_console_please"))

@builder.command('!!eula disagree')
def on_disagree_eula(src: CommandSource):
    '''
    由于拒绝EULA时可能导致服务端无法启动，因此自动关闭在线模式
    如果后面发现会造成问题，将进行改善
    '''
    src.reply(psi.rtr("init_server.disagree_eula"))
    if src.is_console:
        set_eula(psi, False)
        prop_copy = get_prop_copy()
        prop_copy["online-mode"] = False
        save_server_prop()
    else:
        src.reply(psi.rtr("init_server.execute_in_console_please"))

@execute_if(lambda: data.set_mcdr_alive is True or data.config["quick_control"] is True)
@builder.command('!stop')
def stop_exit_mcdr(src: CommandSource):
    if src.is_console:
        psi.set_exit_after_stop_flag(True)
        psi.stop_exit()
    else:
        src.reply(psi.rtr("init_server.execute_in_console_please"))

@execute_if(lambda: data.config["quick_control"] is True)
@builder.command('stop')
def stop_server():
    psi.execute('stop')

@execute_if(lambda: data.set_mcdr_alive is True or data.config["quick_control"] is True)
@builder.command('!start')
def start_exit_mcdr(src: CommandSource):
    if src.is_console:
        psi.set_exit_after_stop_flag(True)
        psi.start()
    else:
        src.reply(psi.rtr("init_server.execute_in_console_please"))

@execute_if(lambda: data.set_mcdr_alive is True or data.config["quick_control"] is True)
@builder.command('!restart')
def restart_exit_mcdr(src: CommandSource):
    if src.is_console:
        psi.set_exit_after_stop_flag(True)
        psi.restart()
    else:
        src.reply(psi.rtr("init_server.execute_in_console_please"))

@execute_if(lambda: psi.is_rcon_running() is False)
@builder.command('!!rcon auto-set enable')
@builder.command('!set-rcon')
def on_auto_set_rcon_enable(src: CommandSource):
    if src.is_console:
        psi.save_config_simple({"auto_agree_eula": data.config["auto_agree_eula"],"auto_set_rcon": True}, 'config.yml')
        data.config["auto_set_rcon"] = True
        data.init_tasks["rcon"] = True
        if psi.is_server_running():
            src.reply(psi.rtr("init_server.do_restart_server"))
        else:
            tasks_count_ok = sum(data.init_tasks.values())
            sum_tasks = len(data.init_tasks)
            process=f"{tasks_count_ok}/{sum_tasks}"
            src.reply(psi.rtr("init_server.init_process", process=process))
            if tasks_count_ok < sum_tasks:
                src.reply(psi.rtr("init_server.init_tip"))
    else:
        src.reply(psi.rtr("init_server.execute_in_console_please"))