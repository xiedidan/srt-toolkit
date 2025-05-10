import os
import subprocess
import argparse

def resize_video(input_file, output_file, width, height, device='cpu'):
    """使用FFMPEG调整视频尺寸，并支持指定设备加速"""
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vf', f'scale={width}:{height}'
    ]
    # 根据设备选择编码器
    if device == 'nvenc':
        command.extend(['-c:v', 'h264_nvenc'])
    elif device == 'qsv':
        command.extend(['-c:v', 'h264_qsv'])
    elif device == 'amf':
        command.extend(['-c:v', 'h264_amf'])
    elif device == 'cpu':
        command.extend(['-c:v', 'libx264'])
    else:
        raise ValueError(f"Unsupported device: {device}")
    
    # 添加-map 0 参数，确保所有附件流（如字幕、音频轨道等）都被复制到输出文件中
    command.extend(['-map', '0'])
    
    command.extend([
        '-c:a', 'copy',
        output_file
    ])
    subprocess.run(command, check=True)

def process_directory(directory, width, height, replace=False, suffix='_resized', device='cpu'):
    """遍历目录，调整所有MP4文件的尺寸"""
    for filename in os.listdir(directory):
        if filename.endswith('.mp4'):
            input_file = os.path.join(directory, filename)
            if replace:
                output_file = input_file  # 直接覆盖原始文件
            else:
                # 使用可配置的后缀
                base_name, ext = os.path.splitext(filename)
                output_file = os.path.join(directory, f'{base_name}{suffix}{ext}')
            try:
                resize_video(input_file, output_file, width, height, device)
                print(f'Processed: {filename}')
            except subprocess.CalledProcessError as e:
                print(f'Error processing {filename}: {e}')

if __name__ == '__main__':
    # 使用argparse设置命令行参数
    parser = argparse.ArgumentParser(description='调整目录中MP4视频的尺寸')
    parser.add_argument('-d', '--directory', help='包含MP4文件的目录路径', required=True)
    parser.add_argument('-w', '--width', type=int, help='视频的目标宽度', required=True)
    # 修改: 移除 -H 简写形式，直接使用 --height
    parser.add_argument('--height', type=int, help='视频的目标高度', required=True)
    parser.add_argument('-r', '--replace', action='store_true', default=False, help='替换原始文件而不是创建新文件')
    parser.add_argument('-s', '--suffix', default='_resized', help='新文件的自定义后缀（默认: _resized）')
    # 更新--device参数，增加对Intel和AMD加速的支持
    parser.add_argument('--device', choices=['cpu', 'nvenc', 'qsv', 'amf'], default='cpu', help='指定加速设备（cpu/nvenc/qsv/amf，默认: cpu）')
    
    args = parser.parse_args()
    
    # 检查必填参数是否缺失
    if not args.directory or not args.width or not args.height:
        parser.error("Missing required arguments. Please provide --directory, --width, and --height.")
    
    process_directory(args.directory, args.width, args.height, args.replace, args.suffix, args.device)  # 传递device参数