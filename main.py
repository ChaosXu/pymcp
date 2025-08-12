import sys
from pathlib import Path

# 将src/mcp_server目录添加到Python路径中
sys.path.insert(0, str(Path(__file__).parent / "src" / "mcp_server"))

from server import run


def main():
    print("Starting pymcp server...")
    run()


if __name__ == "__main__":
    main()