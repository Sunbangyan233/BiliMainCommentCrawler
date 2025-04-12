import csv
import glob
import sys
import os


def merge_csv_files(pattern='bilibili_comment*.csv', output='comments_all.csv'):
    """合并多个 CSV 文件"""
    try:
        files = glob.glob(pattern)
        if not files:
            print("未找到需要合并的文件，请确认bilibili_comment*.csv在此目录下", file=sys.stderr)
            return

        # 读取并合并数据
        all_data = []
        seen = set()  # 基于(用户 UID, 时间)的去重
        for file in files:
            with open(file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    unique_key = (row['用户UID'], row['时间'])
                    if unique_key not in seen:
                        seen.add(unique_key)
                        all_data.append(row)

        # 写入合并文件
        with open(output, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(all_data)

        print(f"成功合并 {len(files)} 个文件 → {output} (共 {len(all_data)} 条去重数据)")
        return True
    except Exception as e:
        print(f"合并失败：{str(e)}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if merge_csv_files():
        print("合并完成")
    else:
        print("合并过程中出现问题")
    