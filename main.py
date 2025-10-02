# main.py

import anyio
from pathlib import Path

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    UserMessage,
    TextBlock,
    ToolUseBlock,
)

# No custom tools needed - Claude's native Read tool can view images!

# --- ANSI Color Codes for clearer terminal output ---
COLOR_RESET = "\033[0m"
COLOR_USER = "\033[92m"  # Green
COLOR_CLAUDE = "\033[94m" # Blue
COLOR_TOOL = "\033[93m"   # Yellow
COLOR_ERROR = "\033[91m"  # Red

def display_message(msg):
    """Helper function to print messages in a structured and colored format."""
    if isinstance(msg, UserMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"{COLOR_USER}You: {block.text}{COLOR_RESET}")
    elif isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"{COLOR_CLAUDE}Claude: {block.text}{COLOR_RESET}")
            elif isinstance(block, ToolUseBlock):
                print(f"{COLOR_TOOL}Claude is using tool: {block.name}{COLOR_RESET}")
                if block.input:
                    print(f"{COLOR_TOOL}  Input: {block.input}{COLOR_RESET}")

async def main():
    """
    Main function to set up and run the video editing agent.
    """
    workspace_dir = Path("./workspace")
    workspace_dir.mkdir(exist_ok=True)
    
    print(f"{COLOR_CLAUDE}--- Claude Video Agent Initialized ---{COLOR_RESET}")
    print(f"Workspace is set to: {workspace_dir.resolve()}")
    print("Type your request to the agent. Type 'exit' or 'quit' to end the session.")
    print("-" * 40)

    # Define the agent's options with full toolset
    system_prompt = (
        "You are a creative assistant specializing in programmatic video and audio editing. "
        "You have access to a file system (Read, Write, Edit, MultiEdit), pattern matching (Glob, Grep), "
        "a Bash terminal for running commands like ffmpeg and yt-dlp, web access (WebFetch, WebSearch), "
        "and task management (Task, TodoWrite, SlashCommand). "
        "Your working directory is `/workspace`. Think step-by-step and use your tools to accomplish the user's goal. "
        "\n\nIMPORTANT: "
        "\n- The Read tool can view images directly - just use it on any image file path to see the contents."
        "\n- You can use yt-dlp in Bash to download videos from YouTube and other platforms."
        "\n- Use ffmpeg for video/audio processing and editing tasks."
        "\n- Use whisper for transcription: `whisper audio.mp3 --model medium --language en` outputs text/SRT/VTT formats."
        "\n- opencv-python (cv2) is available for video frame extraction and analysis."
        "\n- scenedetect is available for automatic scene detection: `scenedetect -i video.mp4 detect-adaptive`"
        "\n- For music identification, use chromaprint (fpcalc) with pyacoustid. Install chromaprint with: `brew install chromaprint` (macOS) or `apt install libchromaprint-tools` (Linux)."
        "\n- If you need any tool that isn't installed (Python libraries, CLI tools, etc.), feel free to install it using pip, npm, or the appropriate package manager. Be proactive about installing what you need to complete the task."
    )

    options = ClaudeAgentOptions(
        allowed_tools=[
            # File operations
            "Read",
            "Write",
            "Edit",
            "MultiEdit",
            # Search/pattern matching
            "Glob",
            "Grep",
            # Execution
            "Bash",
            # Web access
            "WebFetch",
            "WebSearch",
            # Task management
            "Task",
            "TodoWrite",
            "SlashCommand",
        ],
        cwd=str(workspace_dir.resolve()),
        system_prompt=system_prompt,
    )

    # 3. Run the main interaction loop
    try:
        async with ClaudeSDKClient(options=options) as client:
            while True:
                # Use anyio's thread helper for blocking input() call
                prompt = await anyio.to_thread.run_sync(input, f"{COLOR_USER}You: {COLOR_RESET}")

                if prompt.lower() in ["exit", "quit"]:
                    print(f"{COLOR_CLAUDE}Ending session. Goodbye!{COLOR_RESET}")
                    break

                if not prompt:
                    continue

                # Send the user's prompt to the agent
                await client.query(prompt)

                # Stream and display the agent's response and tool usage
                async for message in client.receive_response():
                    display_message(message)

    except Exception as e:
        print(f"{COLOR_ERROR}An unexpected error occurred: {e}{COLOR_RESET}")

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print(f"\n{COLOR_CLAUDE}Session interrupted by user. Goodbye!{COLOR_RESET}")