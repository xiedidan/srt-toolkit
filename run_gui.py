#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT字幕语音合成工具 - 专业酷黑风格GUI启动脚本
"""

import sys
import os
import subprocess

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import tkinter
        import pysrt
        import requests
        import tqdm
        
        # 检查PIL库
        try:
            from PIL import Image, ImageTk
            print("✓ 所有依赖已正确安装")
            return True
        except ImportError:
            print("! 缺少PIL库，图标将不会显示")
            print("  可以通过以下命令安装: pip install Pillow")
            return True  # 仍然可以运行，只是没有图标
            
    except ImportError as e:
        print(f"✗ 依赖检查失败: {e}")
        print("请安装所有必要的依赖:")
        print("pip install -r requirements-srt-tts-gui.txt")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("  SRT字幕语音合成工具 - 专业酷黑风格")
    print("  版本: 1.0.0")
    print("=" * 60)
    
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    try:
        from srt_tts_gui import main
        print("启动GUI界面...")
        main()
        
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main() 