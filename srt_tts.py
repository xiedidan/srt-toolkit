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
import datetime
import json
import argparse
import pysrt
import requests

from tqdm import tqdm  # 新增: 导入进度条库
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
    parser.add_argument("--verbose", action="store_true", help="启用详细输出")  # 新增: verbose 参数
    parser.add_argument("--speed_detection", action="store_true", default=True, help="是否开启语速探测，默认开启")
    parser.add_argument("--speed_adjust", action="store_true", help="启用语音时长调整以匹配字幕时间，默认关闭")
    parser.add_argument("--alternative", type=int, default=0, help="Number of alternative clone roles, default 0")  # Add new argument

    return parser.parse_args()

class SrtTTS:
    def __init__(self, input, output=None, subtitle_suffix="_cn", audio_suffix="", audio_codec="aac", audio_quality="-vbr 3", 
                 audio_format="m4a", speech_speed="moderate", speech_pitch="moderate", voice_role="male", clone_role="", 
                 verbose=False, speed_detection=True, speed_adjust=False, alternative=0):  # Add alternative parameter
        self.input = input
        self.output = output
        self.subtitle_suffix = subtitle_suffix
        self.audio_suffix = audio_suffix
        self.audio_codec = audio_codec  # 修改: 使用传入的 audio_codec 参数
        self.audio_quality = audio_quality.split()  # 修改: 存储为分割后的列表
        self.audio_format = audio_format
        self.speech_speed = speech_speed
        self.speech_pitch = speech_pitch
        self.voice_role = voice_role
        self.clone_role = clone_role
        self.verbose = verbose
        self.ffmpeg_path = "ffmpeg"
        self.speed_detection = speed_detection
        self.speed_adjust = speed_adjust  # 新增speed_adjust属性
        self.alternative = alternative  # Add alternative attribute

    def process_srt_files(self):
        """处理指定目录下的所有SRT文件"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.verbose:
            print(f"[{__name__}] [{current_time}] >> 开始处理目录: {self.input}")
        
        # 新增: 添加目录处理进度条
        srt_files = [f for f in os.listdir(self.input) if f.endswith(f"{self.subtitle_suffix}.srt")]
        for srt_file in tqdm(srt_files, desc="Processing SRT files"):
            self.process_single_srt(os.path.join(self.input, srt_file))

    def process_single_srt(self, srt_file_path):
        """处理单个SRT文件"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.verbose:
            print(f"[{__name__}] [{current_time}] >> 开始处理文件: {srt_file_path}")
        subtitles = self.parse_srt(srt_file_path)
        # 新增: 如果speed_detection为True，则进行语速探测
        if self.speed_detection:
            self.speech_speed = self.detect_optimal_speed(subtitles)
        audio_segments = []
        # 新增: 添加字幕处理进度条
        for subtitle in tqdm(subtitles, desc="Synthesizing subtitles", leave=False):
            audio_segment = self.synthesize_speech(subtitle)
            # 修改: 根据speed_adjust标志决定是否调整时长
            if self.speed_adjust:
                adjusted_audio = self.adjust_audio_duration(audio_segment, subtitle)
            else:
                adjusted_audio = audio_segment
            audio_segments.append(adjusted_audio)
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

    def calculate_speech_speed(self, subtitle):
        """计算字幕的语速（字/秒）"""
        duration = subtitle['end_time'] - subtitle['start_time']
        # 修正: 改用字符数统计（原split()方法不适用于中文）
        char_count = len(subtitle['text'])
        return char_count / duration

    def detect_optimal_speed(self, subtitles):
        """探测最优语速"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{__name__}] [{current_time}] >> 开始语速探测")

        # 阈值可根据实际需求在3.0-6.0字/秒之间调整
        valid_subtitles = [sub for sub in subtitles if self.calculate_speech_speed(sub) <= 6.0]
        
        if not valid_subtitles:
            print(f"[{__name__}] [{current_time}] >> 没有有效的字幕，使用默认语速: moderate")
            return "moderate"

        # 找到语速最快的有效字幕
        fastest_subtitle = max(valid_subtitles, key=self.calculate_speech_speed)
        if self.verbose:
            print(f"[{__name__}] [{current_time}] >> 有效的最快字幕: {fastest_subtitle} (语速: {self.calculate_speech_speed(fastest_subtitle):.3f} 字/秒)")
            
        # 定义语速范围
        speeds = ["very_low", "low", "moderate", "high", "very_high"]
        # 从慢到快尝试每种语速
        for speed in speeds:
            # 生成不同语速的语音
            audio_segment = self.synthesize_speech(fastest_subtitle, speed)
            # 检查是否可以完全播放
            if self.can_play_fully(audio_segment, fastest_subtitle):
                print(f"[{__name__}] [{current_time}] >> 探测到的最优语速: {speed}")
                return speed

        # 如果没有找到合适的语速，返回默认语速
        print(f"[{__name__}] [{current_time}] >> 未找到合适的语速，使用默认语速: very_high")
        return "very_high"

    # 修改: 添加speed参数
    def synthesize_speech(self, subtitle, speed=None):
        """调用语音合成API，获取合成后的音频文件"""
        speed = speed if speed else self.speech_speed
        if self.clone_role:
            max_attempts = self.alternative + 1
            for attempt in range(max_attempts):
                current_clone_role = f"{self.clone_role}{attempt + 1}"  # 修复: 总是添加数字后缀
                role_dir = os.path.join("flashtts_data", "roles", current_clone_role)

                if not os.path.exists(role_dir):
                    if attempt == max_attempts - 1:
                        print(f"[{__name__}] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >> 所有克隆角色尝试失败，切换回普通语音合成")
                        return self._fallback_to_normal_tts(subtitle, speed)
                    continue
                
                try:
                    return self._try_clone_synthesis(subtitle, speed, role_dir, current_clone_role)
                except requests.exceptions.HTTPError as e:
                    print(e)
                    if e.response.status_code == 500 and attempt < max_attempts - 1:
                        continue
                    print(f"[{__name__}] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >> 克隆语音合成失败，切换回普通语音合成")
                    return self._fallback_to_normal_tts(subtitle, speed)
            return self._fallback_to_normal_tts(subtitle, speed)
        else:
            return self._fallback_to_normal_tts(subtitle, speed)

    def _fallback_to_normal_tts(self, subtitle, speed):
        """回退到普通语音合成"""
        payload = {
            "name": self.voice_role,
            "text": subtitle['text'],
            "pitch": self.speech_pitch,
            "speed": speed,
            "temperature": 0.9,
            "top_k": 50,
            "top_p": 0.95,
            "max_tokens": 2048,
            "stream": False,
            "response_format": self.audio_codec
        }
        resp = requests.post(f"{TTS_BASE_URL}/speak", json=payload)
        return resp.content if resp.status_code == 200 else b""

    def _try_clone_synthesis(self, subtitle, speed, role_dir, clone_role):
        """尝试使用特定克隆角色进行语音合成"""
        ref_audio_path = os.path.join(role_dir, "reference_audio.wav")
        ref_text_path = os.path.join(role_dir, "reference_text.txt")
        
        if not os.path.exists(ref_audio_path):
            raise FileNotFoundError(f"Reference audio not found: {ref_audio_path}")
            
        payload = {
            "text": subtitle['text'],
            "temperature": 0.9,
            "response_format": self.audio_codec,
            "pitch": self.speech_pitch,
            "speed": speed,
            "top_k": 50,
            "top_p": 0.95,
            "max_tokens": 2048,
            "stream": False
        }
        
        if os.path.exists(ref_text_path):
            with open(ref_text_path, "r", encoding="utf-8") as text_file:
                payload["reference_text"] = text_file.read().strip()
        
        with open(ref_audio_path, "rb") as audio_file:
            files = {"reference_audio_file": audio_file}
            resp = requests.post(f"{TTS_BASE_URL}/clone_voice", data=payload, files=files)
            
        if resp.status_code == 500:
            raise requests.exceptions.HTTPError(response=resp)
        if resp.status_code != 200:
            raise Exception(f"API error: {resp.status_code} - {resp.text}")
            
        return resp.content

    def concatenate_audio(self, audio_segments, subtitles):
        """使用FFMPEG拼接音频片段，考虑字幕的时间位置"""
        temp_files = []
        valid_indices = []  # 新增: 记录有效音频片段对应的原字幕索引
        for i, segment in enumerate(audio_segments):
            temp_file = f"temp_{i}.{self.audio_format}"
            with open(temp_file, 'wb') as f:
                f.write(segment)
            
            # 新增音频文件验证
            if not self.validate_audio_file(temp_file):
                os.remove(temp_file)
                if self.verbose:
                    print(f"[{__name__}] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >> 跳过无效的音频片段: {temp_file}")
                continue
                
            temp_files.append(temp_file)
            valid_indices.append(i)  # 记录有效索引
        
        # 新增空文件检查
        if not temp_files:
            raise ValueError("没有有效的音频片段可供拼接")
        
        output_file = f"temp_final.{self.audio_format}"
        
        inputs = []
        # 修改: 根据有效索引构建输入参数
        for idx, temp_file in zip(valid_indices, temp_files):
            subtitle = subtitles[idx]
            inputs.append("-itsoffset")
            inputs.append(str(subtitle['start_time']))
            inputs.append("-i")
            inputs.append(temp_file)
        
        command = [
            self.ffmpeg_path, 
            *inputs, 
            '-filter_complex', 
            # 修改: 使用实际拼接数量替换原字幕数量
            f"concat=n={len(temp_files)}:v=0:a=1", 
            '-c:a', self.audio_codec,
            *self.audio_quality,
            output_file
        ]
        subprocess.run(command, check=True)
        
        with open(output_file, 'rb') as f:
            final_audio = f.read()
        
        for temp_file in temp_files:
            os.remove(temp_file)
        os.remove(output_file)
        
        return final_audio

    # 新增: 音频时长调整方法
    def adjust_audio_duration(self, audio_data, subtitle):
        """调整音频时长以匹配字幕时间"""
        current_duration = self.get_audio_duration(audio_data)
        target_duration = subtitle['end_time'] - subtitle['start_time']
        
        if current_duration <= target_duration or target_duration <= 0:
            return audio_data

        # 计算需要的速度因子并应用atempo滤镜
        speed_factor = current_duration / target_duration
        atempo_filters = []
        while speed_factor > 2.0:
            atempo_filters.append("atempo=2.0")
            speed_factor /= 2.0
        if speed_factor != 1.0:
            atempo_filters.append(f"atempo={speed_factor:.3f}")

        # 创建临时文件
        input_temp = f"temp_input_adjust.{self.audio_format}"
        output_temp = f"temp_output_adjust.{self.audio_format}"
        with open(input_temp, 'wb') as f:
            f.write(audio_data)

        # 构建FFmpeg命令
        filter_str = ",".join(atempo_filters) if atempo_filters else None
        command = [
            self.ffmpeg_path,
            '-y', '-hide_banner', '-loglevel', 'error',
            '-i', input_temp
        ]
        if filter_str:
            command += ['-filter:a', filter_str]
        command += ['-c:a', self.audio_codec, output_temp]

        try:
            subprocess.run(command, check=True)
            with open(output_temp, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"Audio adjustment failed: {str(e)}")
            return audio_data
        finally:
            for f in [input_temp, output_temp]:
                if os.path.exists(f):
                    os.remove(f)

    # 新增: 检查音频是否可以完全播放的方法
    def can_play_fully(self, audio_segment, subtitle):
        """检查音频是否可以完全播放"""
        # 这里可以根据实际需求实现具体的检查逻辑
        # 例如，检查音频长度是否与字幕时间戳匹配
        audio_duration = self.get_audio_duration(audio_segment)
        subtitle_duration = subtitle['end_time'] - subtitle['start_time']

        if self.verbose:
            print(f"[{__name__}] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >> 音频长度: {audio_duration:.3f}, 字幕长度: {subtitle_duration:.3f}")

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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.verbose:
            print(f"[{__name__}] [{current_time}] >> 保存最终音频文件: {output_path}")
        with open(output_path, 'wb') as f:
            f.write(audio_data)

    # 新增音频验证方法
    def validate_audio_file(self, file_path):
        """验证音频文件有效性"""
        try:
            # 检查文件基本属性
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                return False
                
            # 使用FFmpeg验证可播放性
            command = [
                self.ffmpeg_path,
                '-v', 'error',
                '-i', file_path,
                '-f', 'null',
                '-'
            ]
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
            return result.returncode == 0
            
        except Exception as e:
            if self.verbose:
                print(f"[{__name__}] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >> 文件验证失败: {str(e)}")
            return False

# 修改: 主函数部分
if __name__ == "__main__":
    args = parse_arguments()
    output_dir = args.output if args.output else args.input
    tts = SrtTTS(
        input=args.input,
        output=output_dir,
        subtitle_suffix=args.subtitle_suffix,
        audio_suffix=args.audio_suffix,
        audio_codec=args.audio_codec,  # 修改: 传递 audio_codec 参数
        audio_quality=args.audio_quality,
        audio_format=args.audio_format,
        speech_speed=args.speech_speed,
        speech_pitch=args.speech_pitch,
        voice_role=args.voice_role,
        clone_role=args.clone_role,
        verbose=args.verbose,
        speed_adjust=args.speed_adjust,  # 传递新的参数
        alternative=args.alternative  # Add new parameter
    )
    tts.process_srt_files()
