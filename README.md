# gemini_launcher.py

A lightweight, command-line tool designed to scan your project's local code files and safely send them to Cyrus (Gemini) for smart code analysis, automatic refactoring, and quick bug fixing.

## Features

- **Smart Code Scanning**: Automatically reads through your active project folders to look for web development files (like Python, JavaScript, HTML, CSS, and database files) so it can understand the exact structure of your application.
- **Built-In Waiting Guard**: Keeps track of how many requests you send and how many code words (tokens) you use every minute. If you get too close to the free limits, it automatically pauses your script and runs a countdown timer to prevent Google's servers from blocking you.
- **Saves Your Secret API Key**: You only have to type your Google AI Studio API key once on your first run. The script saves it securely in a hidden file in your folder, so you don't have to keep copying and pasting it every time you want to use it.
- **Easy Shortcuts**: Supports specialized command keywords like `expand-code` or `organize-code`. Typing these tells Cyrus to immediately change his behavior, such as rewriting an entire file cleanly or automatically hunting down redundant logic blocks.
- **Target Single Files**: Allows you to tell the script to focus purely on one single file instead of reading your whole repository, which saves processing speed and keeps your workspace clear.

## Requirements

- Python 3.10 or higher
- `google-genai` library package
  - *Installation*: Run `pip install google-genai` in your terminal environment before executing the utility.

## Setup

Place `gemini_launcher.py` and your structural `gemini-instructions.txt` configuration file side-by-side inside your target project directory.

## Quick Usage

### Ask a General Coding Question
Type your instruction as a sentence in quotes. The script automatically reads your current folder files and helps you work on them:
```bash
python3 ./gemini_launcher.py "Look through my variables and check for any typos or spelling mistakes"
```

### Focus on a Specific File
Use the `--targets` modifier to make the tool only scan and edit an individual asset, bypassing the rest of your background project files:
```bash
python3 ./gemini_launcher.py --targets src/utils/helpers.py "Clean up the string structures"
```

### Check Your Waiting Timers
To see how much space you have left in your rolling 60-second free bracket without actually sending a new question to the server, check your status dashboard:
```bash
python3 ./gemini_launcher.py --status
```

### Configuration Files
- `.gemignore`: Create this text file in your folder to explicitly hide heavy resource directories (like `node_modules`), layout images, or system logs from being read by the scanner.

- `gemini-instructions.txt`: A local settings file that explicitly holds your design rules, casing conventions, professional coding standards, and macro shorthand shortcuts.
