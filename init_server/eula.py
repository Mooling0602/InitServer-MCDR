import os

from mcdreforged.api.all import *
from .utils import extract_file, eula_file_path

def eula_agree(agree: bool=True) -> bool:
    try:
        # 读取并修改文件内容
        modified = False
        lines = []
        with open(eula_file_path, 'r') as f:
            for line in f:
                stripped = line.strip()

                # 处理eula配置项
                if stripped.startswith('eula='):
                    lines.append('eula=true\n') if agree else lines.append('eula=false\n')
                    modified = True
                else:
                    lines.append(line)

        # 如果未找到eula配置项则追加
        if not modified:
            lines.append('eula=true\n') if agree else lines.append('eula=false\n')

        # 写回文件
        with open(eula_file_path, 'w') as f:
            f.writelines(lines)

        return True

    except Exception:
        return False

def set_eula(server: PluginServerInterface, agree: bool=True):
    if os.path.exists(eula_file_path):
        set_eula = eula_agree() if agree else eula_agree(False)
        if set_eula:
            server.logger.info(server.rtr("init_server.set_eula_success"))
        else:
            server.logger.error(server.rtr("init_server.set_eula_error"))
    else:
        extract_file(os.path.join('resources', 'eula.txt'), eula_file_path)

def is_eula_agreed() -> bool:
    """
    读取 eula.txt 中的 EULA 同意状态，
    如果解析到 'eula=true' 则返回 True，否则返回 False
    """
    try:
        with open(eula_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('eula='):
                    value = line.split('=', 1)[1].strip().lower()
                    return value == 'true'
        return False
    except Exception:
        return False