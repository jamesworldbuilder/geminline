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
    geminline --targets ./static/js/sidebar-ui.js "In transforms-timeline-panel, let's make the following adjustments: 1.) If the set-transform-interval-btn is selected, then the parent transform-row should be automatically selected. 2.) When a transform-row is selected, the first transform-config-element in the transformations-matrix, within the selected transform-row, should be automatically selected/highlighted. Currently, selecting the transform-config-element auto-selects transform-row-1, instead of the current parent transform-row."
```
```bash
    === SELECT ASSISTANT TIER ===
    [1] Free Tier Assistant (gemini-2.5-flash-lite)
    [2] Paid/Premium Pro Assistant (gemini-2.5-pro)
    [3] Advanced Flash Assistant (gemini-3.5-flash)
    Select an assistant option [1-3] (Default: 1): 3
    Proceeding with engine configuration: gemini-3.5-flash
    
    
    === FREE TIER RUNTIME TELEMETRY ===
    Active Model Engine: gemini-3.5-flash
    Requests (Last 60s): 0/15  (Headroom remaining: 15)
    Daily Quota Used:    2/1500  (Daily remaining: 1498)
    Tokens Used (Last 60s): 0/1000000 (Headroom remaining: 1000000)
    Window State: Stable (Next token slot refresh calculation in: 0s)
    ===================================
    
    Loading ignore configuration fields...
    Loading external AI instructions configuration found...
    Scanning workspace in '.'...
    Cyrus is analyzing your codebase and generating revisions...
    
    RESPONSE:
    
    ========================================
    REVISION 1
    ========================================
    <target_file>./static/js/sidebar-ui.js</target_file>
    
    <original>
    // dynamically sets active node and refreshes properties UI panels on single click
            row.addEventListener('click', (e) => {
                if (e.target.tagName === 'BUTTON' || e.target.closest('button') || e.target.tagName === 'INPUT' || e.target.closest('.transform-interval-timing')) return
                
                const rowsContainer = document.getElementById('transforms-rows')
                if (rowsContainer) {
                    Array.from(rowsContainer.children).forEach(r => r.style.borderLeftColor = 'transparent')
                }
                row.style.borderLeftColor = '#00a8ff'
    </original>
    
    <replacement>
    // dynamically sets active node and refreshes properties UI panels on single click
            row.addEventListener('click', (e) => {
                if (e.target.tagName === 'BUTTON' || e.target.closest('button') || e.target.tagName === 'INPUT' || e.target.closest('.transform-interval-timing')) return
                
                const rowsContainer = document.getElementById('transforms-rows')
                if (rowsContainer) {
                    Array.from(rowsContainer.children).forEach(r => r.style.borderLeftColor = 'transparent')
                }
                row.style.borderLeftColor = '#00a8ff'
                
                // Automatically select/highlight the first transform-config-element (index 0)
                configData.activeTransformEditIndex = 0
                row.dataset.transformConfig = JSON.stringify(configData)
                renderMatrixGrid()
    </replacement>
    
    ========================================
    REVISION 2
    ========================================
    <target_file>./static/js/sidebar-ui.js</target_file>
    
    <original>
    matrixBtn.onclick = (e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        configData.activeTransformEditIndex = i
                        const tRow = matrixDiv.closest('.transforms-list-item')
                        if (tRow) tRow.dataset.transformConfig = JSON.stringify(configData)
                        renderMatrixGrid()
                        if (rowsContainer && rowsContainer.children[i]) {
                            rowsContainer.children[i].click()
                        }
                    }
    </original>
    
    <replacement>
    matrixBtn.onclick = (e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        configData.activeTransformEditIndex = i
                        const tRow = matrixDiv.closest('.transforms-list-item')
                        if (tRow) tRow.dataset.transformConfig = JSON.stringify(configData)
                        renderMatrixGrid()
                        if (tRow) {
                            tRow.click()
                        }
                    }
    </replacement>
    
    ========================================
    REVISION 3
    ========================================
    <target_file>./static/js/sidebar-ui.js</target_file>
    
    <original>
    timeBtn.onclick = (e) => {
                e.preventDefault()
                e.stopPropagation()
                const isHidden = timingDiv.style.display === 'none'
                timingDiv.style.display = isHidden ? 'flex' : 'none'
                // toggles outer block layout for the matrix wrapper
                matrixDiv.style.display = isHidden ? 'block' : 'none'
                timeBtn.style.color = isHidden ? configData.markerColor : '#aaa'
                timeBtn.style.opacity = isHidden ? '1' : '0.6'
                
                const cfg = JSON.parse(row.dataset.transformConfig)
                cfg.isTimingOpen = isHidden
                row.dataset.transformConfig = JSON.stringify(cfg)
                
                if (typeof activeNode !== 'undefined' && activeNode) {
                    let existingData = activeNode.getAttr('transformGroupData')
                    const tKey = tRow.dataset.transformKey
                    if (existingData && existingData[tKey]) {
                        existingData[tKey].isTimingOpen = isHidden
                        activeNode.setAttr('transformGroupData', existingData)
                    }
                }
    </original>
    
    <replacement>
    timeBtn.onclick = (e) => {
                e.preventDefault()
                e.stopPropagation()
                
                // Automatically select the parent transform-row
                row.click()
    
                const isHidden = timingDiv.style.display === 'none'
                timingDiv.style.display = isHidden ? 'flex' : 'none'
                // toggles outer block layout for the matrix wrapper
                matrixDiv.style.display = isHidden ? 'block' : 'none'
                timeBtn.style.color = isHidden ? configData.markerColor : '#aaa'
                timeBtn.style.opacity = isHidden ? '1' : '0.6'
                
                const cfg = JSON.parse(row.dataset.transformConfig)
                cfg.isTimingOpen = isHidden
                row.dataset.transformConfig = JSON.stringify(cfg)
                
                if (typeof activeNode !== 'undefined' && activeNode) {
                    let existingData = activeNode.getAttr('transformGroupData')
                    const tKey = row.dataset.transformKey
                    if (existingData && existingData[tKey]) {
                        existingData[tKey].isTimingOpen = isHidden
                        activeNode.setAttr('transformGroupData', existingData)
                    }
                }
    </replacement>
    
    
    ========================================
    Model Engine:     gemini-3.5-flash
    Prompt Tokens:    137329
    Output Tokens:    1281
    Total Session:    138610 tokens
    Remaining Window: 861390 tokens (Max: 1000000)
    ========================================

```
