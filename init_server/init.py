import os
import init_server.data as data

from .utils import serverDir


def is_server_first_start():
    '''
    通过检查服务端目录下是否存在 server.properties 文件来判断服务端是否第一次启动
    此方法在以后需要进一步改善，因为或许会需要更加准确的判断方法，但对目前的插件功能而言已经足够
    '''
    if os.path.exists(os.path.join(serverDir, "server.properties")):
        data.server_first_time_start = False
        data.prop_valid = True
        return False
    else:
        data.server_first_time_start = True
        return True