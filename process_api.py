import json
from datetime import datetime
import csv
import sys
import glob
import re
import os
import shutil

def sanitize_text(text):
    """处理特殊字符和换行（保留Unicode字符）"""
    return text.replace('\n', ' ').replace('\r', ' ')

def parse_json_data(json_str):
    """增强型JSON解析，支持以下格式：
    1. 标准JSON对象
    2. 包含多个对象的JSON数组
    3. 多个独立JSON对象拼接
    """
    decoded_data = []
    
    # 尝试解析为JSON数组
    try:
        data_list = json.loads(json_str)
        if isinstance(data_list, list):
            return [item for item in data_list if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass
    
    # 尝试解析为多个独立JSON对象
    decoder = json.JSONDecoder()
    offset = 0
    while offset < len(json_str):
        try:
            obj, offset = decoder.raw_decode(json_str[offset:])
            if isinstance(obj, dict):
                decoded_data.append(obj)
            offset += 1
        except:
            offset += 1
    
    return decoded_data

def process_comments(json_obj):
    """处理单个JSON对象"""
    try:
        if json_obj.get('code', -1) != 0:
            return []
        if 'data' not in json_obj or 'replies' not in json_obj['data']:
            return []

        output = []
        for comment in json_obj['data']['replies']:
            try:
                ctime = datetime.fromtimestamp(comment['ctime']).strftime('%Y-%m-%d %H:%M:%S')
                uid = comment['member']['mid']
                uname = sanitize_text(comment['member']['uname'])
                content = sanitize_text(comment['content']['message'])
                
                output.append({
                    '时间': ctime,
                    '用户UID': uid,
                    '用户名': uname,
                    '评论内容': content
                })
            except KeyError as e:
                print(f"评论字段缺失：{e}", file=sys.stderr)
        
        return output
    
    except Exception as e:
        print(f"处理JSON对象时发生错误：{str(e)}", file=sys.stderr)
        return []

def save_to_csv(data, filename):
    """保存数据到CSV文件（自动处理特殊字符）"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['时间', '用户UID', '用户名', '评论内容'])
            writer.writeheader()
            writer.writerows(data)
        print(f"已保存 {len(data)} 条评论到 {filename}")
        return True
    except IOError as e:
        print(f"文件保存失败：{str(e)}", file=sys.stderr)
        return False

def confirm_directory():
    """交互式目录确认"""
    current_dir = os.getcwd()
    files = glob.glob(os.path.join(current_dir, 'main_*.json'))
    
    if not files:
        print(f"当前目录 {current_dir} 中未找到main_*.json文件")
        return False

    print(f"发现 {len(files)} 个数据文件：")
    for f in files:
        print(f"  - {os.path.basename(f)}")
    
    return input("\n是否处理这些文件？(y/n): ").lower() == 'y'

def cleanup_files():
    """安全清理原始文件"""
    files = glob.glob('main_*.json')
    if not files:
        return

    print("\n发现以下原始文件：")
    for f in files:
        print(f"  - {f}")
    
    if input("\n是否删除这些原始文件？(y/n): ").lower() == 'y':
        success = 0
        for f in files:
            try:
                os.remove(f)
                print(f"已删除：{f}")
                success += 1
            except Exception as e:
                print(f"删除失败 {f}: {str(e)}")
        print(f"成功删除 {success}/{len(files)} 个文件")

def main():
    # 配置控制台编码环境
    if sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        print("建议使用Python 3.7+ 以获得更好的编码支持")

    # 步骤1：交互确认
    if not confirm_directory():
        print("操作已取消")
        return

    # 步骤2：处理文件
    files = glob.glob('main_*.json')
    total_count = 0
    processed_files = 0

    for file in files:
        print(f"\n正在处理文件：{os.path.basename(file)}")
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                json_str = f.read()
        except Exception as e:
            print(f"文件读取失败：{str(e)}", file=sys.stderr)
            continue

        # 解析JSON数据
        json_objects = parse_json_data(json_str)
        if not json_objects:
            print("未找到有效JSON数据", file=sys.stderr)
            continue

        # 处理所有JSON对象
        all_comments = []
        for obj in json_objects:
            all_comments.extend(process_comments(obj))
        
        if not all_comments:
            print("未提取到有效评论", file=sys.stderr)
            continue

        # 生成输出文件名
        match = re.search(r'main_(.*?)\.json', file)
        suffix = match.group(1) if match else str(processed_files+1)
        output_file = f'bilibili_comments_{suffix}.csv'

        # 保存数据
        if save_to_csv(all_comments, output_file):
            total_count += len(all_comments)
            processed_files += 1

            # 数据预览
            print("\n数据预览：")
            print("="*80)
            for idx, item in enumerate(all_comments[:3], 1):
                preview = item['评论内容'][:100] + ("..." if len(item['评论内容']) > 100 else "")
                print(f"{idx}. [{item['时间']}] {item['用户名']}({item['用户UID']}):")
                print(preview)
                print("-"*80)

    # 结果统计
    print(f"\n转换完成！共处理 {processed_files}/{len(files)} 个文件")
    print(f"总计转换 {total_count} 条评论")

    # 步骤3：清理文件
    cleanup_files()

if __name__ == "__main__":
    main()