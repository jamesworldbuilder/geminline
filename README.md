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

## Configuration Files

- `.gemignore`: A local configuration file intended to explicitly hide heavy resource directories (like `node_modules`), system files, or any other files and/or directories you want the AI assistant to ignore during its analysis are listed in this file.

- `gemini-instructions.txt`: A local configuration file that describes the design rules, professional coding standards, and identity configurations of which the AI assistant is specialized in.

## Setup & Persistent Alias

1. Place `gemini_launcher.py` and your structural `gemini-instructions.txt` configuration file side-by-side inside your chosen system directory.
2. Mark the script file as an executable binary asset so Linux can launch it cleanly:
```bash
    chmod +x /path/to/your/directory/gemini_launcher.py
```
3. Run the following command to append the persistent `geminline` alias to your bash runtime profile configuration and instantly refresh your terminal session environment:
```bash
    echo 'alias geminline="python3 /path/to/your/directory/gemini_launcher.py"' >> ~/.bashrc && source ~/.bashrc
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
    geminline --targets ./static/js/sidebar-ui.js "In the transforms-timeline-panel, each object (i.e., each transforms-list-item) needs to have unique set_id and style_id values, which are also unique to each other. less-talk"
```
```bash
    === FREE TIER RUNTIME TELEMETRY ===
    Requests (Last 60s): 0/15  (Headroom remaining: 15)
    Tokens Used (Last 60s): 0/1000000 (Headroom remaining: 1000000)
    Window State: Stable (Next token slot refresh calculation in: 0s)
    ===================================
    
    Loading ignore configuration fields...
    Loading external AI instructions configuration found...
    Scanning workspace in '.'...
    Cyrus is analyzing your workspace via gemini-2.5-flash-lite...
    
    RESPONSE:
    
    ========================================
    REVISION 1
    ========================================
    <target_file>./static/js/sidebar-ui.js</target_file>
    
    <original>
    // generates four random characters and four random integers to fulfill split format requirements
            const generateSplitId = () => {
                const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
                let letterPart = ''
                let numberPart = ''
                for (let j = 0; j < 4; j++) {
                    letterPart += chars[Math.floor(Math.random() * chars.length)]
                    numberPart += chars[Math.floor(Math.random() * chars.length)]
                }
                return letterPart + numberPart
            }
    
            // strictly enforces unique structural random suffixes if missing in state reference
            if (!markerConfig.set_id) markerConfig.set_id = `set_${generateSplitId()}`
            if (!markerConfig.style_id) markerConfig.style_id = `style_${generateSplitId()}`
    </original>
    
    <replacement>
    // generates four random characters and four random integers to fulfill split format requirements
            const generateSplitId = () => {
                const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
                let result = ''
                for (let i = 0; i < 8; i++) {
                    result += chars[Math.floor(Math.random() * chars.length)]
                }
                return result
            }
    
            // strictly enforces unique structural random suffixes if missing in state reference
            // ensures set_id and style_id are unique from each other and across all transform elements
            if (!markerConfig.set_id) {
                let setId = `set_${generateSplitId()}`
                let styleId = `style_${generateSplitId()}`
                // Ensure set_id and style_id are unique
                while (setId === styleId) {
                    styleId = `style_${generateSplitId()}`
                }
                markerConfig.set_id = setId
                markerConfig.style_id = styleId
            } else if (!markerConfig.style_id) {
                let styleId = `style_${generateSplitId()}`
                // Ensure style_id is unique from the existing set_id
                while (markerConfig.set_id === styleId) {
                    styleId = `style_${generateSplitId()}`
                }
                markerConfig.style_id = styleId
            }
    </replacement>
    
    
    ========================================
    Model Engine:     gemini-2.5-flash-lite
    Prompt Tokens:    136872
    Output Tokens:    604
    Total Session:    137476 tokens
    Remaining Window: 862524 tokens (Max: 1000000)
    ========================================

```
