import subprocess
import argparse
import os

def combine_video_with_subtitles(args):
    # 动态选择硬件加速参数
    hwaccel = args.hwaccel  # 直接使用用户输入值（None表示使用CPU）
    ffmpeg_cmd = ["ffmpeg", "-y"]  # 默认不添加硬件加速参数
    
    # 仅当用户指定加速参数时才添加
    if hwaccel:
        ffmpeg_cmd.extend(["-hwaccel", hwaccel])
        
    # 仅当使用 amf 硬件加速时，添加硬件加速的 filter_complex
    if hwaccel == "amf":  # 如果使用 amf 硬件加速
        ffmpeg_cmd.extend([
            "-i", args.main_video,
            "-i", args.subtitle1,
            "-i", args.subtitle2,
            "-filter_complex",  # 使用硬件加速的 filter_complex
            f"[0:v]hwupload_amf[sub1];"  # 将视频流上传到AMF硬件
            f"[1:v]hwupload_amf[sub2];"  # 将字幕1上传到AMF硬件
            f"[2:v]hwupload_amf[sub3];"  # 将字幕2上传到AMF硬件
            f"[sub1][sub2]overlay=x={args.sub1_x}:y={args.sub1_y}[v1];"
            f"[v1][sub3]overlay=x={args.sub2_x}:y={args.sub2_y}[final]",
            "-map", "[final]",
            "-map", "0:a?",  # 复制音频流
            "-c:v", args.codec,
            args.output
        ])
    else:  # 其他情况（包括未启用硬件加速）
        ffmpeg_cmd.extend([
            "-i", args.main_video,
            "-i", args.subtitle1,
            "-i", args.subtitle2,
            "-filter_complex",
            f"[0:v][1:v]overlay=x={args.sub1_x}:y={args.sub1_y}[v1];"
            f"[v1][2:v]overlay=x={args.sub2_x}:y={args.sub2_y}[final]",
            "-map", "[final]",
            "-map", "0:a?",
            "-c:v", args.codec,
            args.output
        ])

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"\n✅ 合成成功 -> {args.output}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 合成失败: {e}")
        # 如果失败且用户未手动指定参数，尝试自动回退方案
        if not args.hwaccel:
            for fallback in ["amf", "qsv"]:
                try:
                    print(f"尝试回退方案: -hwaccel {fallback}")
                    ffmpeg_cmd[ffmpeg_cmd.index("-hwaccel")+1] = fallback
                    subprocess.run(ffmpeg_cmd, check=True)
                    print(f"✅ 使用 {fallback} 合成成功")
                    return True
                except subprocess.CalledProcessError:
                    continue
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="视频字幕合成工具")
    # 添加硬件加速参数（支持自动回退机制）
    parser.add_argument("--hwaccel", 
                   default=None, 
                   choices=["nvenc", "amf", "qsv"],
                   help="硬件加速选项（默认：使用CPU，不指定此参数）")  # 更新帮助信息
    parser.add_argument("-m", "--main-video", required=True, help="主视频文件路径")
    parser.add_argument("-s1", "--subtitle1", default="_en", help="第一个字幕文件路径（默认: 主文件名_en）")
    parser.add_argument("-s2", "--subtitle2", default="_cn", help="第二个字幕文件路径（默认: 主文件名_cn）")
    parser.add_argument("--sub1-x", type=int, default=0, help="字幕1 X轴偏移 (默认: 0)")
    parser.add_argument("--sub1-y", type=int, default=-10, help="字幕1 Y轴偏移 (默认: -10)")
    parser.add_argument("--sub2-x", type=int, default=0, help="字幕2 X轴偏移 (默认: 0)")
    parser.add_argument("--sub2-y", type=int, default=-65, help="字幕2 Y轴偏移 (默认: -65)")
    parser.add_argument("-o", "--output", default=None, help="输出文件路径 (默认: 主文件名+_blended.mp4)")
    # 新增 --codec 参数
    parser.add_argument("--codec", default="libx264", help="输出视频编码器（默认: libx264）")

    args = parser.parse_args()

    # 自动生成字幕文件路径
    main_base = os.path.splitext(os.path.basename(args.main_video))[0]
    main_dir = os.path.dirname(args.main_video)
    ext = os.path.splitext(args.main_video)[1]
    
    if args.subtitle1 == "_en":
        args.subtitle1 = os.path.join(main_dir, f"{main_base}_en{ext}")
    if args.subtitle2 == "_cn":
        args.subtitle2 = os.path.join(main_dir, f"{main_base}_cn{ext}")

    # 生成输出路径
    if args.output is None:
        output_dir = os.path.dirname(args.main_video)
        args.output = os.path.join(output_dir, f"{main_base}_blended.mp4")

    # 验证文件存在
    for f in [args.main_video, args.subtitle1, args.subtitle2]:
        if not os.path.exists(f):
            print(f"错误：文件不存在 - {f}")
            exit(1)

    combine_video_with_subtitles(args)