import subprocess
import sys
import os
import argparse

def extract_cover(video_path, output_path, map_param=None):
    """
    提取视频封面（优先用户指定流，否则尝试附件流 -> 第一帧回退）
    """
    # 优先使用用户指定的流
    if map_param:
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",  # 覆盖已存在文件
            "-i", video_path,
            "-map", map_param,
            "-c", "copy",
            "-vframes", "1",
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False

    # 未指定流时：先尝试附件流，再第一帧
    try:
        # 尝试附件流中的图像（如封面）
        cmd_attach = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", video_path,
            "-map", "0:t",  # 所有附件流
            "-c", "copy",
            "-f", "image2",
            "-vframes", "1",
            output_path
        ]
        subprocess.run(cmd_attach, check=True, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        pass

    try:
        # 提取视频第一帧作为回退
        cmd_frame = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", video_path,
            "-vf", "select=eq(n\,0)",
            "-vframes", "1",
            "-q:v", "2",
            output_path
        ]
        subprocess.run(cmd_frame, check=True, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def process_directory(input_dir, output_dir, map_param=None):
    """处理目录中的所有 MP4 文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".mp4"):
                video_path = os.path.join(root, file)
                base_name = os.path.splitext(file)[0]
                output_path = os.path.join(output_dir, f"{base_name}.jpg")

                # 提取封面
                success = extract_cover(video_path, output_path, map_param)
                status = "成功" if success else "失败"
                print(f"[{status}] {file} -> {os.path.basename(output_path)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量提取 MP4 文件封面")
    parser.add_argument("-i", "--input", required=True, help="输入目录路径")
    parser.add_argument("-o", "--output", default=None, help="输出目录路径（默认：与输入目录相同）")
    parser.add_argument("-m", "--map", help="指定封面流通道（例如：0:3）")
    args = parser.parse_args()
    if args.output is None:
        args.output = args.input

    if not os.path.isdir(args.input):
        print(f"错误：输入目录不存在 - {args.input}")
        sys.exit(1)

    process_directory(args.input, args.output, args.map)
