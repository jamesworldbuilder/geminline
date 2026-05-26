# gemini_launcher.py

A lightweight, command-line tool designed to scan your project's local code files and safely send them to Gemini for smart code analysis, automatic refactoring, and quick bug fixing.

## Features

- **Smart Code Scanning**: Automatically reads through your active project folders to look for web development files (like Python, JavaScript, HTML, CSS, and database files) so it can understand the exact structure of your application.
- **Built-In Waiting Guard**: Keeps track of how many requests you send and how many code words (tokens) you use every minute. If you get too close to the free limits, it automatically pauses your script and runs a countdown timer to prevent Google's servers from blocking you.
- **Saves Your Secret API Key**: You only have to type your Google AI Studio API key once on your first run. The script saves it securely in a hidden file in your folder, so you don't have to keep copying and pasting it every time you want to use it.
- **Easy Shortcuts**: Supports specialized command keywords like `expand-code` or `organize-code`. Typing these tells the engine to immediately change its behavior, such as rewriting an entire file cleanly or automatically hunting down redundant logic blocks.
- **Target Single Files**: Allows you to tell the script to focus purely on one single file instead of reading your whole repository, which saves processing speed and keeps your workspace clear.

## Requirements

- **Python**: Version 3.10 or higher is required to support modern standard library components and async processing pipelines.
- **Pip Packages**: The official Google GenAI SDK library wrapper must be accessible within your runtime environment.
  - *Installation*: Run the following command in your terminal interface before executing the utility:
```bash
    pip install google-genai
```

## Setup & Persistent Alias

1. Place `gemini_launcher.py` and your structural `gemini-instructions.txt` configuration file side-by-side inside your chosen system directory.
2. Mark the script file as an executable binary asset so Linux can launch it cleanly:
```bash
    chmod +x /path/to/your/directory/gemini_launcher.py
```
3. Open your local bash runcom file (`~/.bashrc`) in a text editor:
```bash
    nano ~/.bashrc
```
4. Append a persistent command alias definition block to the bottom of the file to bind the executable to a clean global shorthand command:
```bash
    alias geminline="python3 /path/to/your/directory/gemini_launcher.py"
```
5. Save the configuration and force refresh your current shell terminal process memory to load the new mapping path instantly:
```bash
    source ~/.bashrc
```

## Usage

### Ask a General Coding Question
Type your instruction as a sentence in quotes. The script automatically reads your current folder files and helps you work on them:
```bash
    geminline "Look through my variables and check for any typos or spelling mistakes"
```

### Focus on a Specific File
Use the `--targets` modifier to make the tool only scan and edit an individual asset, bypassing the rest of your background project files:
```bash
    geminline --targets src/utils/helpers.py "Consolidate the functions"
```

### Check Your Waiting Timers
To see how much space you have left in your rolling 60-second free bracket without actually sending a new question to the server, check your status dashboard:
```bash
    geminline --status
```

## Example Output
```bash
    geminline "Hey, Cyrus. Can you tell me what's in this folder?"`
```
```bash
    === FREE TIER RUNTIME TELEMETRY ===
    Requests (Last 60s): 0/15   (Headroom remaining: 15)
    Tokens Used (Last 60s): 0/1,000,000 (Headroom remaining: 1,000,000)
    Window State: Stable (Next token slot refresh calculation in: 0s)
    ===================================

    Loading ignore configuration fields...
    Loading external AI instructions configuration found...
    Scanning workspace in '.'...
    Cyrus is analyzing your workspace via gemini-3.5-flash...
    
    RESPONSE:
    
    This workspace contains **clip-handler** (also referred to as **yt-factory**), a full-stack automated video editing, object tracking, and rendering pipeline. The system integrates a KonvaJS-based web editor, background rendering daemons, and computer vision APIs to track features, apply dynamic zoom filters, and compile final video renders.
    
    An architectural breakdown of the workspace directories and files:
    
    ### 1. Orchestration & Control
    *   **`manage-factory.sh`**: A robust Bash automation script (`set -euo pipefail`) to start, stop, restart, and query the status of the background consumer and producer daemons. It manages process IDs via local `.pid` files.
    
    ### 2. Backend Services & Daemons (`src/`)
    *   **`editor_server.py`**: A Flask web server serving the frontend editor interface. It handles browser heartbeat monitoring (auto-terminating if the browser disconnects), processes simulated tracking payloads, and appends assembly tasks to the local queue.
    *   **`producer.py`**: A daemonized background process that polls the task queue and executes localized FFmpeg pipelines on raw video clips.
    *   **`consumer.py`**: A background service that processes tasks from the queue and renders final high-quality video files using FFmpeg.
    *   **`shared_utils.py`**: Core utility library containing the mathematical logic to build dynamic FFmpeg `zoompan` filter chains based on object tracking coordinate maps.
    
    ### 3. CLI Tools & Authentication (`src/`)
    *   **`fetch_clip.py`**: CLI utility that downloads specific video sections using `yt-dlp` and automatically launches the web browser to open the editor interface.
    *   **`add_task.py`**: CLI utility to manually append video processing tasks to the queue.
    *   **`auth_setup.py`**: Script to run the local OAuth2 flow to generate YouTube upload tokens.
    
    ### 4. Frontend Editor Interface (`templates/` & `static/js/`)
    *   **`templates/editor-ui.html`**: Semantic HTML5 layout for the video editor. It features a dark-themed workspace, responsive video wrapper, timeline scrubber, multi-track lane visualization, and a tabbed sidebar control panel.
    *   **`static/js/main.js`**: Main frontend entry point. It coordinates event bindings, handles local file uploads, manages letterboxing/cropping UI states, and runs the main animation render loop.
    *   **`static/js/canvas-engine.js`**: Core KonvaJS rendering engine. It manages the canvas stage, interactive transformers, cropping masks, letterboxing overlays, and grid rendering.
    *   **`static/js/sidebar-ui.js`**: Complex UI controller managing layers, interactive timeline markers, caption groups, advanced transform configurations (exportable to JSON), and the tracking panel.
    *   **`static/js/transport-controls.js`**: Implements video playback controls, custom timeline scrubbing, and hover tooltips.
    *   **`static/js/state-manager.js`**: Centralized state container tracking active layers, selected nodes, and active layer IDs.
    *   **`static/js/dom-elements.js`**: Cached DOM element references.
    
    ### 5. Computer Vision APIs (`comp-vision-api/`)
    *   **`comp_vision_cpu.py`**: Flask API running YOLOv8 (ONNX) for object detection and Lucas-Kanade optical flow for tracking custom anchor features across extracted video frames.
    *   **`comp_vision_gpu.py`**: Flask API running PyTorch-accelerated YOLOv8 tracking, exposed via ngrok with token-based authentication and usage quotas.
    
    ### 6. Configuration (`config/`)
    *   **`client-secrets.json`**: Google API client credentials.
    *   **`token.json`**: Active Google OAuth2 refresh and access tokens for YouTube uploads.
    *   **`task-queue.json`**: Local JSON database storing the active queue of video rendering tasks.
    
    ========================================
    Model Engine:      gemini-3.5-flash
    Prompt Tokens:     181017
    Output Tokens:     872
    Total Session:     183059 tokens
    Remaining Window: 816941 tokens (Max: 1000000)
    ========================================
```
