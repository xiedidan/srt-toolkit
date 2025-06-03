import subprocess
import argparse
import os
import glob

def combine_video_with_subtitles(args):
    # 将字典转换为 argparse.Namespace 对象
    args = argparse.Namespace(**args)
    
    # 根据 hwaccel 参数设置 FFmpeg 命令
    if args.hwaccel == "nvenc":
        ffmpeg_cmd = [
            "ffmpeg", "-y", 
            "-filter_complex_threads", "32",
            "-filter_threads", "32",
            "-hwaccel", "cuda",  # 启用 CUDA 硬件加速
            "-hwaccel_output_format", "cuda",
            "-c:v", "h264_cuvid",
            "-i", args.main_video,
            "-hwaccel", "cuda",  # 启用 CUDA 硬件加速
            "-hwaccel_output_format", "cuda",
            "-i", args.subtitle1,
            "-hwaccel", "cuda",  # 启用 CUDA 硬件加速
            "-hwaccel_output_format", "cuda",
            "-i", args.subtitle2,
            "-filter_complex",
            f"[0:v][1:v]overlay_cuda=x={args.sub1_x}:y={args.sub1_y}[v1];"
            f"[v1][2:v]overlay_cuda=x={args.sub2_x}:y={args.sub2_y}[final]",
            "-map", "[final]",
            "-map", "0:a?",
            "-c:v", "hevc_nvenc",  # 使用 NVIDIA HEVC 编码器
            "-preset", "fast",  # 设置编码预设为 fast
            "-tune", "hq",  # 调整编码参数以获得高质量输出
            "-rc-lookahead", "32",  # 启用码率控制前瞻
            args.output
        ]
    else:
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", args.main_video,
            "-i", args.subtitle1,
            "-i", args.subtitle2,
            "-filter_complex",
            f"[0:v][1:v]overlay=x={args.sub1_x}:y={args.sub1_y}[v1];"
            f"[v1][2:v]overlay=x={args.sub2_x}:y={args.sub2_y}[final]",
            "-map", "[final]",
            "-map", "0:a?",
            "-c:v", args.codec,
            "-rc-lookahead", "32",  # 启用码率控制前瞻
            args.output
        ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"\n✅ 合成成功 -> {args.output}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 合成失败: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="视频字幕合成工具")
    parser.add_argument("-m", "--main-video", required=False, help="主视频文件路径")
    parser.add_argument("-s1", "--subtitle1", default="_en.mp4", help="第一个字幕文件路径（默认: 主文件名_en.mp4）")
    parser.add_argument("-s2", "--subtitle2", default="_cn.mp4", help="第二个字幕文件路径（默认: 主文件名_cn.mp4）")
    parser.add_argument("--sub1-x", type=int, default=0, help="字幕1 X轴偏移 (默认: 0)")
    parser.add_argument("--sub1-y", type=int, default=-10, help="字幕1 Y轴偏移 (默认: -10)")
    parser.add_argument("--sub2-x", type=int, default=0, help="字幕2 X轴偏移 (默认: 0)")
    parser.add_argument("--sub2-y", type=int, default=-65, help="字幕2 Y轴偏移 (默认: -65)")
    parser.add_argument("-o", "--output", default=None, help="输出文件路径 (默认: 主文件名+_blended.mp4)")
    # 新增 --codec 参数
    parser.add_argument("--codec", default="libx264", help="输出视频编码器（默认: libx264）")
    # 新增 --list_dir 参数
    parser.add_argument("--list_dir", action='store_true', help="处理指定目录下的所有主视频文件")
    # 新增 --hwaccel 参数
    parser.add_argument("--hwaccel", default=None, choices=["None", "nvenc"], help="硬件加速选项，默认为None（CPU编码），可选nvenc（NVIDIA硬件加速）")
    # 新增 --main-suffix 参数
    parser.add_argument("--main-suffix", default="", help="主视频文件后缀（默认为空）")

    args = parser.parse_args()

    # 处理目录模式
    if args.list_dir:
        # 获取目录下所有主视频文件（排除以 _en.mp4 或 _cn.mp4 结尾的文件）
        video_files = [f for f in glob.glob(os.path.join(args.main_video, '*.mp4')) 
                       if not (f.endswith(args.subtitle1) or f.endswith(args.subtitle2))]
        
        if not video_files:
            print(f"目录中未找到符合条件的主视频文件: {args.main_video}")
            exit(1)

        total_files = len(video_files)
        processed_files = 0

        for video_file in video_files:
            # 创建一个新的字典来保存当前文件的处理参数
            local_args = args.__dict__.copy()
            
            # 修改主视频文件路径
            local_args['main_video'] = video_file
            
            # 构造字幕文件路径，去除主视频后缀
            main_base = os.path.splitext(os.path.basename(video_file))[0]
            if args.main_suffix:
                main_base = main_base.replace(args.main_suffix, "")
            main_dir = os.path.dirname(video_file)
            ext = os.path.splitext(video_file)[1]

            local_args['subtitle1'] = os.path.join(main_dir, f"{main_base}{args.subtitle1}")
            local_args['subtitle2'] = os.path.join(main_dir, f"{main_base}{args.subtitle2}")

            # 修改输出文件名构造逻辑，添加 _blended 后缀
            base_name = os.path.basename(video_file)
            base, ext = os.path.splitext(base_name)
            output_filename = f"{base}_blended{ext}"
            local_args['output'] = os.path.join(os.path.dirname(video_file), output_filename)

            # 检查输出文件是否已存在
            if os.path.exists(local_args['output']):
                print(f"跳过已存在的文件: {local_args['output']}")
                continue

            print(f"正在处理文件: {video_file}")
            combine_video_with_subtitles(local_args)  # 使用 local_args 调用函数
            processed_files += 1
            print(f"已处理 {processed_files}/{total_files} 个文件")

    else:
        # 自动生成字幕文件路径，去除主视频后缀
        main_base = os.path.splitext(os.path.basename(args.main_video))[0]
        if args.main_suffix:
            main_base = main_base.replace(args.main_suffix, "")
        main_dir = os.path.dirname(args.main_video)
        ext = os.path.splitext(args.main_video)[1]
        
        args.subtitle1 = os.path.join(main_dir, f"{main_base}{args.subtitle1}")
        args.subtitle2 = os.path.join(main_dir, f"{main_base}{args.subtitle2}")

        # 生成输出路径
        if args.output is None:
            output_dir = os.path.dirname(args.main_video)
            args.output = os.path.join(output_dir, f"{main_base}_blended.mp4")

        # 检查输出文件是否已存在
        if os.path.exists(args.output):
            print(f"跳过已存在的文件: {args.output}")
            exit(0)

        # 验证文件存在
        for f in [args.main_video, args.subtitle1, args.subtitle2]:
            if not os.path.exists(f):
                print(f"错误：文件不存在 - {f}")
                exit(1)

        combine_video_with_subtitles(args)
