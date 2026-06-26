# -*- coding: utf-8 -*-
"""输出辅助：处理 --output-dir 统一写入逻辑。

所有引擎脚本共享此模块，实现：
  1. 从 sys.argv 提取 --output-dir 参数
  2. 将 JSON 写入 output_dir/<filename>.json
  3. 打印文件路径到 stdout（让 AI 知道文件在哪）
"""

import os, sys, json


def extract_output_dir():
    """从 sys.argv 中提取 --output-dir 参数值。

    返回 (output_dir, remaining_args)，其中 remaining_args
    是去掉 --output-dir 及其值后的参数列表。
    """
    args = sys.argv[1:]
    output_dir = None
    remaining = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            skip_next = True
            continue
        remaining.append(arg)
    return output_dir, remaining


def save_output(data, filename, output_dir):
    """将 data 写入 output_dir/filename.json，并打印路径到 stdout。

    如果 output_dir 为 None，回退到旧行为（直接打印 JSON 到 stdout）。
    """
    if output_dir is None:
        print(json.dumps(data, ensure_ascii=False))
        return

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(path)
