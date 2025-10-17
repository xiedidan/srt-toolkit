# SRT Translator - 字幕翻译与语音合成工具

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

一个功能强大的SRT字幕处理工具集，集成了字幕翻译、语音合成、视频处理等多种功能，支持批量处理和自动化工作流程。

## 功能特点

### 🌐 字幕翻译 (srt_translator.py)
- 支持多种AI翻译服务（DeepSeek、SiliconFlow、百炼等）
- 批量处理SRT文件
- 智能重试机制，确保翻译完整性
- 定时任务功能，可设置开始/停止时间
- 自动生成视频描述（标题、简介、标签）
- 支持自定义翻译参数（温度、批次大小等）

### 🗣️ 语音合成 (srt_tts.py)
- 文本转语音功能，支持多种音频格式
- 角色克隆技术，可模拟特定人物声音
- 智能语速探测，自动调整语音参数
- 音频时长调整，匹配字幕时间轴
- 批量处理多个SRT文件
- 支持多种语音角色和音调设置

### 🎬 视频处理
- **视频混合** (video_blender.py)：将视频与多字幕轨道合并
- **视频缩放** (video_resize.py)：调整视频分辨率，支持硬件加速
- **封面提取** (cover_extractor.py)：批量提取视频封面图片

### 🖥️ 图形界面
- 现代化深色主题GUI (srt_tts_gui.py)
- 直观的参数配置界面
- 实时处理进度显示
- 详细日志输出

## 项目结构

```
srt-translator/
├── srt_translator.py      # 字幕翻译核心模块
├── srt_tts.py            # 语音合成模块
├── srt_tts_gui.py        # 图形界面
├── run_gui.py            # GUI启动脚本
├── video_blender.py      # 视频与字幕合成
├── video_resize.py       # 视频分辨率调整
├── cover_extractor.py    # 视频封面提取
├── consts.py             # 配置常量（不提交到git）
├── consts.py.template    # 配置模板文件
├── requirements.txt      # 基础依赖
├── requirements-srt-tts-gui.txt  # GUI依赖
├── requirements.md       # 功能需求文档
├── technical_design.md   # 技术设计文档
├── start-translator.sh   # 示例启动脚本
├── flashtts_data/        # 语音角色数据
│   ├── roles/            # 角色克隆数据
│   └── mega-roles/       # 高级角色数据
└── doc/                  # 文档目录
    └── flashtts-client.md
```

## 安装说明

### 环境要求

- Python 3.6 或更高版本
- FFmpeg（用于视频/音频处理）
- 可选：NVIDIA GPU（用于硬件加速）

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/srt-translator.git
cd srt-translator
```

2. 安装基础依赖
```bash
pip install -r requirements.txt
```

3. 安装GUI依赖（可选）
```bash
pip install -r requirements-srt-tts-gui.txt
```

4. 配置API密钥
创建配置文件并填入您的API密钥：
```bash
cp consts.py.template consts.py
```
然后编辑 `consts.py` 文件，填入您的实际API密钥和配置。

**注意**：
- `consts.py` 文件已在 `.gitignore` 中排除，不会被提交到版本控制系统
- 请勿分享或提交包含API密钥的 `consts.py` 文件
- 如需添加新的API配置，请参考 `consts.py.template` 中的格式

## 使用指南

### 字幕翻译

#### 基本用法
```bash
python srt_translator.py -i input.srt -o output_cn.srt
```

#### 批量处理目录
```bash
python srt_translator.py -i /path/to/srt/files/ --list_dir
```

#### 高级选项
```bash
python srt_translator.py \
    -i input.srt \
    -o output_cn.srt \
    --api_vendor deepseek \
    --model_type deepseek-r1:671b \
    --batch 30 \
    --temperature 1.0 \
    --timer 00:30:00 \
    --stop_timer 08:00:00 \
    --desc
```

### 语音合成

#### 基本用法
```bash
python srt_tts.py -i /path/to/srt/files/ -o /path/to/output/
```

#### 使用角色克隆
```bash
python srt_tts.py \
    -i /path/to/srt/files/ \
    -o /path/to/output/ \
    --clone_role "角色名称" \
    --speech_speed moderate \
    --speech_pitch moderate \
    --speed_detection
```

### 视频处理

#### 视频与字幕合成
```bash
python video_blender.py \
    -m main_video.mp4 \
    -s1 subtitle_en.mp4 \
    -s2 subtitle_cn.mp4 \
    -o output_blended.mp4
```

#### 调整视频分辨率
```bash
python video_resize.py \
    -d /path/to/videos/ \
    --width 1920 \
    --height 1080 \
    --device nvenc
```

#### 提取视频封面
```bash
python cover_extractor.py \
    -i /path/to/videos/ \
    -o /path/to/output/ \
    --resize \
    --min_size 1920x1080
```

### 图形界面

启动GUI应用：
```bash
python run_gui.py
```

或直接运行：
```bash
python srt_tts_gui.py
```

## 配置说明

### 语音角色配置

在 `flashtts_data/roles/` 目录下添加新角色：
```
flashtts_data/roles/新角色名/
├── reference_audio.wav    # 参考音频文件
└── reference_text.txt     # 参考文本（可选）
```

### API配置

项目支持多种翻译服务提供商，在 `consts.py` 中配置：
- `ollama` - 本地部署模型
- `siliconflow` - SiliconFlow云服务
- `bailian` - 阿里云百炼
- `deepseek` - DeepSeek官方API

## 工作流程示例

### 完整的字幕本地化流程

1. **翻译字幕**
```bash
python srt_translator.py -i video.srt -o video_cn.srt --api_vendor deepseek
```

2. **生成语音**
```bash
python srt_tts.py -i ./ -o ./audio/ --clone_role "角色名"
```

3. **合成视频**
```bash
python video_blender.py -m video.mp4 -s1 video_en.mp4 -s2 video_cn.mp4
```

## 常见问题

### Q: 如何添加新的翻译服务？
A: 在 `consts.py` 中的 `API_CONFIG` 字典添加新的供应商配置。

### Q: 语音合成失败怎么办？
A: 检查TTS服务是否正常运行，确认 `consts.py` 中的 `TTS_BASE_URL` 配置正确。

### Q: 视频处理速度慢？
A: 使用 `--device nvenc` 参数启用NVIDIA硬件加速（需要支持的GPU）。

### Q: 如何批量处理大量文件？
A: 使用 `--list_dir` 参数处理整个目录，脚本会自动跳过已处理的文件。

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 GPL v3 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [FFmpeg](https://ffmpeg.org/) - 多媒体处理框架
- [pysrt](https://github.com/byroot/pysrt) - SRT字幕解析库
- [FlashTTS](https://github.com/jianchang512/FlashTTS) - 语音合成引擎

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue: [GitHub Issues](https://github.com/yourusername/srt-translator/issues)
- 邮箱: your.email@example.com

---

## 开发计划

详细的功能需求和技术实现方案请参考：
- [需求文档](requirements.md) - 包含所有待实现功能的详细描述
- [技术设计文档](technical_design.md) - 包含技术实现方案和架构设计

### 即将实现的功能

1. **Ollama Cloud 模型支持** - 扩展模型调用能力，支持更多AI模型
2. **改进的TTS语速处理** - 解决字幕语速过快时的语音合成问题
3. **Whisper语音转字幕** - 添加基于Whisper的语音/视频转字幕功能
4. **统一Web界面** - 整合所有工具的Web UI，支持项目管理和批量处理

### 贡献指南

如果您想参与开发，请：
1. 查看 [需求文档](requirements.md) 了解当前计划
2. 参考 [技术设计文档](technical_design.md) 了解实现方案
3. 创建 Issue 讨论您想开发的功能
4. 提交 Pull Request 之前请确保代码已通过测试

## 版本历史

- v2.0.0 (计划中) - 添加Ollama Cloud支持、改进TTS处理、语音转字幕、WebUI
- v1.x.x - 当前版本，包含基础的字幕翻译、语音合成和视频处理功能

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！