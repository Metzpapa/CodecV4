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

    # Define the agent's options - no custom tools needed!
    system_prompt = (
        "You are a creative assistant specializing in programmatic video and audio editing. "
        "You have access to a file system (Read, Write) and a Bash terminal for running commands like ffmpeg. "
        "Your working directory is `/workspace`. Think step-by-step and use your tools to accomplish the user's goal. "
        "\n\nIMPORTANT: The Read tool can view images directly - just use it on any image file path to see the contents."
    )

    options = ClaudeAgentOptions(
        allowed_tools=[
            "Read",
            "Write",
            "Bash",
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