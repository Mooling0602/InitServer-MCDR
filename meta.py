#!/usr/bin/python
import json
import os

def generate_plugin_json(plugin_id, version, name, description_en, description_zh, author, link, dependencies, output_file):
    plugin_data = {
        "id": plugin_id,
        "version": version,
        "name": name,
        "description": {
            "en_us": description_en,
            "zh_cn": description_zh
        },
        "dependencies": dependencies,
        "author": author,
        "link": link
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plugin_data, f, ensure_ascii=False, indent=4)

def get_unique_filename(base_filename):
    base, ext = os.path.splitext(base_filename)
    count = 1
    # 查找现有的文件以确定副本数量
    while os.path.exists(base_filename):
        base_filename = f"{base} ({count}){ext}"
        count += 1
    return base_filename

if __name__ == "__main__":
    print("请填写以下插件信息：")

    plugin_id = input("插件 ID: ")
    version = input("版本号 (例如 0.0.1): ")
    name = input("插件名称: ")
    description_en = input("英文描述: ")
    description_zh = input("中文介绍: ")
    author = input("作者名称: ")
    link = input("插件链接: ")

    # 默认依赖项
    dependencies = {
        "mcdreforged": ">=2.1.0"
    }

    # 添加额外的依赖项
    while True:
        dependency_name = input("请输入额外的依赖名称（或按 Enter 键结束）：")
        if not dependency_name:
            break
        dependency_version = input(f"{dependency_name} 的版本号: ")
        dependencies[dependency_name] = dependency_version

    output_file = "mcdreforged.plugin.json"

    # 检查文件是否存在
    if os.path.exists(output_file):
        action = input(f"{output_file} 已存在。是否替换? (y/n): ")
        if action.lower() == 'y':
            generate_plugin_json(plugin_id, version, name, description_en, description_zh, author, link, dependencies, output_file)
            print(f"{output_file} 已成功生成。")
        else:
            output_file = get_unique_filename(output_file)
            generate_plugin_json(plugin_id, version, name, description_en, description_zh, author, link, dependencies, output_file)
            print(f"{output_file} 已成功生成。")
    else:
        generate_plugin_json(plugin_id, version, name, description_en, description_zh, author, link, dependencies, output_file)
        print(f"{output_file} 已成功生成。")
