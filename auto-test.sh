#!/bin/bash
set -e

# 运行脚本所在的目录
SCRIPT_DIR=$(dirname "$0")
# 尝试获取与 main.py 相关的最后一个进程的 PID
pid=$(pgrep -f main.py | tail -n 1)

# 检查 pid 变量是否被设置了值（即 pgrep 是否找到了进程）
if [ -z "$pid" ]; then
    # 如果 pid 为空（即 pgrep 没有找到进程），则设置 pid 为 2
    pid=2
fi

# 接收第一个命令行参数作为bookname
if [ -z "$1" ]; then
    echo "请提供bookname作为参数"
    exit 1
fi

bookname=$1
cd  $SCRIPT_DIR && python3 main.py "$bookname" "$pid"  &

