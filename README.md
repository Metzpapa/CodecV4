# Claude Video Editing Agent

A creative assistant specializing in programmatic video and audio editing using the Claude Code SDK.

## Features

- **Video Processing**: Download videos with yt-dlp, edit with ffmpeg
- **Audio Editing**: Process audio files with ffmpeg
- **Transcription**: OpenAI Whisper for speech-to-text (supports 99 languages, outputs SRT/VTT/TXT)
- **Image Viewing**: Claude can directly view images using the Read tool
- **Full Filesystem Access**: Read, Write, Edit files with pattern matching (Glob, Grep)
- **Web Access**: WebFetch and WebSearch capabilities
- **Task Management**: Built-in todo lists and sub-agents

## Prerequisites

- Python 3.10+
- Node.js
- Claude Code: `npm install -g @anthropic-ai/claude-code`

## Installation

```bash
# Install all Python dependencies
pip install -r requirements.txt

# ffmpeg should be installed via system package manager
# macOS: brew install ffmpeg
# Ubuntu: apt install ffmpeg
```

## Usage

```bash
python main.py
```

### Example Requests

- "Download a video from YouTube using yt-dlp"
- "Extract the audio from video.mp4"
- "Transcribe this audio file and generate subtitles"
- "View the image file in the workspace and describe what you see"
- "Create a 10-second video with ffmpeg"
- "Search the web for the latest ffmpeg documentation"

## Available Tools

The agent has access to:
- **File Operations**: Read, Write, Edit, MultiEdit
- **Search**: Glob (file patterns), Grep (content search)
- **Execution**: Bash (for ffmpeg, yt-dlp, whisper, etc.)
- **Web**: WebFetch, WebSearch
- **Task Management**: Task (sub-agents), TodoWrite, SlashCommand

## Workspace

All work happens in the `./workspace/` directory, which is automatically created on startup.

## Notes

- Claude's Read tool supports viewing images natively - no custom tools needed!
- yt-dlp can download from YouTube, Vimeo, and 1000+ other sites
- ffmpeg is available for complex video/audio processing tasks
- Whisper supports 99 languages and can output text, SRT, VTT, TSV, and JSON formats
- Whisper model sizes: tiny, base, small, medium, large (larger = more accurate but slower)
