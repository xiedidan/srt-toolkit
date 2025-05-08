# 字幕语音合成工具总体功能描述：
# 1. 根据指定的目录，读取符合命名规则的srt字幕文件
# 2. 对于每一条字幕，调用语音合成API，获取合成后的音频文件
# 3. 根据SRT时间戳将每句对应的音频文件拼接，生成一个完整的音频文件
# 4. 按命名规则将最终的完整语音文件保存到指定目录

# 智能语速探查：
# 1. 根据SRT字幕文件中的时间戳和字数，计算每条字幕的语速（字/秒）
# 2. 对于语速最快的字幕，反复用不同合成语速，调用语音合成API，直到合成的语音能够完整播放

# API参考：
# 参考本目录下flashtts-client.md

# 角色音频目录：
# 本目录下flashtts_data

import os
import re
import subprocess
import json
import argparse
import pysrt
from consts import TTS_BASE_URL

def parse_arguments():
    parser = argparse.ArgumentParser(description="SRT字幕语音合成工具")
    parser.add_argument("-i", "--input", help="SRT字幕文件所在目录")
    parser.add_argument("-o", "--output", help="输出音频文件的目录，默认与--input相同")
    parser.add_argument("--subtitle_suffix", default="_cn", help="字幕文件的后缀，默认为'_cn'")
    parser.add_argument("--audio_suffix", default="", help="音频文件的后缀，默认为空")
    parser.add_argument("--audio_codec", default="aac", help="音频编码格式，默认为'aac'")
    parser.add_argument("--audio_quality", default="-vbr 3", help="音频质量，默认为'-vbr 3'")
    parser.add_argument("--audio_format", default="m4a", help="音频文件格式，默认为'm4a'")
    parser.add_argument("-s", "--speech_speed", default="moderate", 
                        choices=["very_low", "low", "moderate", "high", "very_high"],
                        help="合成语速（very_low, low, moderate, high, very_high），默认为'moderate'")
    parser.add_argument("-p", "--speech_pitch", default="moderate", 
                        choices=["very_low", "low", "moderate", "high", "very_high"],
                        help="音高（very_low, low, moderate, high, very_high），默认为'moderate'")
    parser.add_argument("-r", "--voice_role", default="male", help="合成角色，默认为'male'")
    parser.add_argument("--clone_role", default="", help="克隆角色，默认为空")
    parser.add_argument("--verbose", action="store_true", help="启用详细输出")
    parser.add_argument("--speed_detection", action="store_true", default=True, help="是否开启语速探测，默认开启")
    return parser.parse_args()

import requests

class SrtTTS:
    def __init__(self, input, output=None, subtitle_suffix="_cn", audio_suffix="", audio_codec="aac", audio_quality="-vbr 3", audio_format="m4a", speech_speed="moderate", speech_pitch="moderate", voice_role="male", clone_role="", verbose=False, speed_detection=True):
        self.input = input
        self.output = output
        self.subtitle_suffix = subtitle_suffix
        self.audio_suffix = audio_suffix
        self.audio_codec = audio_codec
        self.audio_quality = audio_quality
        self.audio_format = audio_format
        self.speech_speed = speech_speed
        self.speech_pitch = speech_pitch
        self.voice_role = voice_role
        self.clone_role = clone_role
        self.verbose = verbose
        self.ffmpeg_path = "ffmpeg"  # 假设FFMPEG已安装并可直接调用
        # 新增属性：speed_detection
        self.speed_detection = speed_detection

    def process_srt_files(self):
        """处理指定目录下的所有SRT文件"""
        for srt_file in os.listdir(self.input):
            if srt_file.endswith(f"{self.subtitle_suffix}.srt"):
                self.process_single_srt(os.path.join(self.input, srt_file))

    def process_single_srt(self, srt_file_path):
        """处理单个SRT文件"""
        subtitles = self.parse_srt(srt_file_path)
        # 新增: 如果speed_detection为True，则进行语速探测
        if self.speed_detection:
            self.speech_speed = self.detect_optimal_speed(subtitles)
        audio_segments = []
        for subtitle in subtitles:
            audio_segment = self.synthesize_speech(subtitle)
            audio_segments.append(audio_segment)
        final_audio = self.concatenate_audio(audio_segments, subtitles)
        self.save_final_audio(final_audio, srt_file_path)

    def parse_srt(self, srt_file_path):
        """解析SRT文件，返回字幕列表"""
        subs = pysrt.open(srt_file_path, encoding='utf-8')
        subtitles = []
        for sub in subs:
            subtitles.append({
                'index': sub.index,
                'start_time': sub.start.ordinal / 1000,  # 转换为秒
                'end_time': sub.end.ordinal / 1000,  # 转换为秒
                'text': sub.text
            })
        return subtitles

    def time_to_seconds(self, timecode):
        """将SRT时间码转换为秒数"""
        h, m, s, ms = map(int, re.match(r'(\d+):(\d+):(\d+),(\d+)', timecode).groups())
        return h * 3600 + m * 60 + s + ms / 1000

    # 新增: 语速探测方法
    def detect_optimal_speed(self, subtitles):
        """探测最优语速"""
        # 找到语速最快的字幕
        fastest_subtitle = max(subtitles, key=self.calculate_speech_speed)
        # 定义语速范围
        speeds = ["very_low", "low", "moderate", "high", "very_high"]
        # 从慢到快尝试每种语速
        for speed in reversed(speeds):
            # 生成不同语速的语音
            audio_segment = self.synthesize_speech(fastest_subtitle, speed)
            # 检查是否可以完全播放
            if self.can_play_fully(audio_segment, fastest_subtitle):
                # 新增: 打印探测到的语速
                print(f"探测到的最优语速: {speed}")
                return speed
        # 如果没有找到合适的语速，返回默认语速
        print("未找到合适的语速，使用默认语速: moderate")
        return "moderate"

    # 修改: 添加speed参数
    def synthesize_speech(self, subtitle, speed=None):
        """调用语音合成API，获取合成后的音频文件"""
        speed = speed if speed else self.speech_speed
        payload = {
            "name": self.voice_role if not self.clone_role else self.clone_role,
            "text": subtitle['text'],
            "pitch": self.speech_pitch,
            "speed": speed,
            "temperature": 0.9,
            "top_k": 50,
            "top_p": 0.95,
            "max_tokens": 2048,
            "stream": False,
            "response_format": self.audio_format
        }
        resp = requests.post(f"{TTS_BASE_URL}/speak", json=payload)  # 修改：使用TTS_BASE_URL
        if resp.status_code == 200:
            return resp.content
        else:
            print(f"Error: {resp.status_code}, {resp.text}")
            return b""

    def calculate_speech_speed(self, subtitle):
        """计算字幕的语速（字/秒）"""
        duration = subtitle['end_time'] - subtitle['start_time']
        word_count = len(subtitle['text'].split())
        return word_count / duration

    def concatenate_audio(self, audio_segments, subtitles):
        """使用FFMPEG拼接音频片段，考虑字幕的时间位置"""
        temp_files = []
        for i, segment in enumerate(audio_segments):
            temp_file = f"temp_{i}.{self.audio_format}"
            with open(temp_file, 'wb') as f:
                f.write(segment)
            temp_files.append(temp_file)
        
        output_file = f"temp_final.{self.audio_format}"
        
        # 创建输入文件列表，包含时间偏移量
        inputs = []
        for i, subtitle in enumerate(subtitles):
            inputs.append(f"-itsoffset {subtitle['start_time']}")
            inputs.append(f"-i {temp_files[i]}")
        
        command = [
            self.ffmpeg_path, 
            *inputs, 
            '-filter_complex', 
            f"concat=n={len(subtitles)}:v=0:a=1", 
            '-c', 'copy', 
            output_file
        ]
        subprocess.run(command, check=True)
        
        with open(output_file, 'rb') as f:
            final_audio = f.read()
        
        # 清理临时文件
        for temp_file in temp_files:
            os.remove(temp_file)
        os.remove(output_file)
        
        return final_audio

    # 新增: 检查音频是否可以完全播放的方法
    def can_play_fully(self, audio_segment, subtitle):
        """检查音频是否可以完全播放"""
        # 这里可以根据实际需求实现具体的检查逻辑
        # 例如，检查音频长度是否与字幕时间戳匹配
        audio_duration = self.get_audio_duration(audio_segment)
        subtitle_duration = subtitle['end_time'] - subtitle['start_time']
        return audio_duration <= subtitle_duration

    # 新增: 获取音频长度的方法
    def get_audio_duration(self, audio_data):
        """获取音频文件的长度"""
        # 使用FFMPEG计算音频长度
        temp_file = "temp_audio_for_duration.m4a"
        with open(temp_file, 'wb') as f:
            f.write(audio_data)
        
        command = [
            self.ffmpeg_path, 
            "-i", temp_file, 
            "-f", "null", 
            "-"
        ]
        
        result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
        os.remove(temp_file)
        
        for line in result.stderr.splitlines():
            if "Duration" in line:
                duration_str = line.split(',')[0].split(': ')[1]
                hours, minutes, seconds = map(float, duration_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds
        
        return 0.0  # 如果无法获取时长，返回0

    def save_final_audio(self, audio_data, srt_file_path):
        """保存最终的完整语音文件"""
        output_file = os.path.splitext(os.path.basename(srt_file_path))[0] + f"{self.audio_suffix}.{self.audio_format}"
        output_path = os.path.join(self.output, output_file)
        with open(output_path, 'wb') as f:
            f.write(audio_data)

# 修改: 主函数部分
if __name__ == "__main__":
    args = parse_arguments()
    output_dir = args.output if args.output else args.input
    tts = SrtTTS(
        input=args.input,
        output=output_dir,
        subtitle_suffix=args.subtitle_suffix,
        audio_suffix=args.audio_suffix,
        audio_codec=args.audio_codec,
        audio_quality=args.audio_quality,
        audio_format=args.audio_format,
        speech_speed=args.speech_speed,
        speech_pitch=args.speech_pitch,
        voice_role=args.voice_role,
        clone_role=args.clone_role,
        verbose=args.verbose
    )
    tts.process_srt_files()
