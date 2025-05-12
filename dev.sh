#!/bin/bash

# 确保脚本在出错时停止执行
set -e

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 检查必要的目录是否存在，如果不存在则创建
mkdir -p pdf png result

# 检查并安装必要的 Python 包
echo "正在检查并安装必要的 Python 包..."
pip3 install -r requirements.txt

# 启动 FastAPI 应用
echo "正在启动 FastAPI 应用..."
python3 app.py
