config = {} # 存储插件配置
server_first_time_start = False # 标记服务器是否首次启动
need_agree_eula = False # 标记是否需要同意EULA
prop_valid = False # 标记 server.properties 是否存在
prop = {} # 缓存加载的 server.properties 内容
set_mcdr_alive = False # 标记是否设置 MCDR 不随服务端退出
init_tasks = {
    "eula": False, # EULA 初始化任务
    "rcon": False # RCON 初始化任务
} # 存储初始化任务完成进度