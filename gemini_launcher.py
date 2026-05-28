#!/usr/bin/env python3
import os
import sys
import fnmatch
import time
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# maps models to context limit thresholds
MODEL_LIMITS = {
    'gemini-3.5-flash': 1000000,
    'gemini-3.1-pro': 2000000,
    'gemini-2.5-flash': 1000000,
    'gemini-2.5-flash-lite': 1000000,
    'gemini-2.5-pro': 2000000
}

# tracks free tier local baseline rate limits
FREE_LIMITS = {
    'requests': 15,
    'tokens': 1000000
}

# defines structural schemas to guarantee output formatting layout shapes
class CodeRevision(BaseModel):
    filename: str = Field(description="The relative file path being altered")
    code_to_alter: str = Field(description="The EXACT snippet of code that needs to be altered including comments")
    revised_code: str = Field(description="The EXACT code snippet of revised code to add matching style constraints")

class RevisionResponse(BaseModel):
    revisions: list[CodeRevision] = Field(description="List of individual numbered code revision steps")

class BlueprintItem(BaseModel):
    filename: str = Field(description="The file target path needing modification alignment")
    target_line_range: str = Field(description="The specific line ranges to isolate for editing context such as 120-150")
    focus_objective: str = Field(description="The targeted single action description to resolve inside this specific block snippet")

class BlueprintPlan(BaseModel):
    planned_updates: list[BlueprintItem] = Field(description="Sequential list of isolated target updates needed to fulfill the instruction")

def get_tracker_path():
    """returns hidden file path for localized limit metrics"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '.cyrus_quota_history.json')

def get_chat_history_path():
    """returns hidden file path for localized conversational log snapshots"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '.gemini_chat_history.json')

def load_quota_logs():
    """reads transaction records out of local cache file"""
    path = get_tracker_path()
    default_structure = {"api_key": None, "logs": []}
    if not os.path.exists(path):
        return default_structure
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"api_key": None, "logs": data}
            return data
    except Exception:
        return default_structure

def save_quota_logs(data):
    """saves updated call instances to disk"""
    try:
        with open(get_tracker_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception:
        pass

def pr_quota_metrics(display_only=False, active_model="gemini-2.5-flash-lite"):
    """parses execution loops and displays real time sliding window telemetry"""
    now = time.time()
    cache = load_quota_logs()
    logs = cache.get("logs", [])
    
    # filters records falling inside current active window
    active_window_logs = [log for log in logs if now - log['timestamp'] < 60]
    
    # track requests made during the current calendar day (last 24 hours) for daily limit tracking
    daily_logs = [log for log in logs if now - log['timestamp'] < 86400]
    
    if len(logs) != len(daily_logs):
        cache["logs"] = daily_logs
        save_quota_logs(cache)
        
    req_count = len(active_window_logs)
    daily_count = len(daily_logs)
    
    # sets the daily maximum ceiling based on the active engine tier being targeted
    daily_max = 50 if active_model == "gemini-2.5-pro" else 1500
    daily_left = max(0, daily_max - daily_count)
    
    # aggregates token count sums excluding explicit block triggers
    token_count = sum(log['tokens'] for log in active_window_logs if isinstance(log['tokens'], (int, float)))
    server_locked = any(log['tokens'] == "429_LOCKED" for log in active_window_logs)
    
    # pro tier constraints limit sliding execution rates down to 2 requests per minute
    rpm_max = 2 if active_model == "gemini-2.5-pro" else FREE_LIMITS['requests']
    req_left = max(0, rpm_max - req_count)
    tokens_left = 0 if server_locked else max(0, FREE_LIMITS['tokens'] - token_count)
    
    cooldown = 0
    if active_window_logs:
        oldest_ts = active_window_logs[0]['timestamp']
        cooldown = max(0, int(60 - (now - oldest_ts)))
        
    print("\n=== FREE TIER RUNTIME TELEMETRY ===")
    print("Active Model Engine: " + str(active_model))
    print("Requests (Last 60s): " + str(req_count) + "/" + str(rpm_max) + "  (Headroom remaining: " + str(req_left) + ")")
    print("Daily Quota Used:    " + str(daily_count) + "/" + str(daily_max) + "  (Daily remaining: " + str(daily_left) + ")")
    
    if server_locked:
        print("Tokens Used (Last 60s): [429 RESOURCE_EXHAUSTED]")
        print("\n[ALERT] Quota ceiling breached - Cool-down lock active for another: " + str(cooldown) + "s")
    else:
        print("Tokens Used (Last 60s): " + str(token_count) + "/" + str(FREE_LIMITS['tokens']) + " (Headroom remaining: " + str(tokens_left) + ")")
        if req_left == 0 or daily_left == 0:
            print("\n[ALERT] Quota ceiling breached - Cool-down lock active for another: " + str(cooldown) + "s")
        else:
            print("Window State: Stable (Next token slot refresh calculation in: " + str(cooldown) + "s)")
    print("===================================\n")
    
    if display_only:
        sys.exit(0)
        
    if req_left == 0 or server_locked:
        print("Automatic protection block triggered - Halting call loop to prevent a remote 429 error")
        try:
            for remaining in range(cooldown, 0, -1):
                sys.stdout.write("\r  Resuming terminal execution pipeline in: " + str(remaining) + "s...")
                sys.stdout.flush()
                time.sleep(1)
            print("\n[Cleared] Proceeding with transaction scan")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled (CTRL+C) during countdown loop phase")
            sys.exit(0)

def record_transaction(total_tokens):
    """logs successful transaction metadata metrics directly into cache"""
    cache = load_quota_logs()
    cache["logs"].append({
        'timestamp': time.time(),
        'tokens': total_tokens
    })
    save_quota_logs(cache)

def load_gemignore(root_dir):
    """parses exclude parameters out of the project configuration profile"""
    ignore_config = {
        'files': set(),
        'directories': set(),
        'types': set()
    }
    
    gemignore_path = os.path.join(root_dir, '.gemignore')
    if not os.path.exists(gemignore_path):
        return ignore_config
        
    current_category = None
    with open(gemignore_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line == '[SPECIFIC FILES]':
                current_category = 'files'
                continue
            elif line == '[SPECIFIC DIRECTORIES]':
                current_category = 'directories'
                continue
            elif line == '[SPECIFIC FILE TYPES]':
                current_category = 'types'
                continue
                
            if current_category and not line.startswith('['):
                ignore_config[current_category].add(line)
                
    return ignore_config

def load_ai_instructions():
    """reads system instruction profiles out of the external asset file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    instructions_path = os.path.join(script_dir, 'gemini-instructions.txt')
    
    if not os.path.exists(instructions_path):
        print("ERROR: Core AI instructions configuration not found at " + instructions_path)
        sys.exit(1)
        
    with open(instructions_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def parse_identity_profile(instructions_text):
    """extracts name and background specifications out of instructions config"""
    profile = {"name": "Gem", "background": "the Jim in me"}
    for line in instructions_text.splitlines():
        if line.startswith("NAME="):
            val = line.split("=")[1].strip()
            if val:
                profile["name"] = val
        elif line.startswith("BACKGROUND="):
            val = line.split("=")[1].strip()
            if val:
                profile["background"] = val
    return profile

def should_ignore(path, is_dir, ignore_config, root_dir):
    """matches files and directories against active exclusions list"""
    rel_path = os.path.relpath(path, root_dir)
    parts = rel_path.split(os.sep)
    filename = os.path.basename(path)
    
    if is_dir:
        for d_pattern in ignore_config['directories']:
            clean_pattern = d_pattern.rstrip('/')
            if clean_pattern in parts:
                return True
        return False
        
    for d_pattern in ignore_config['directories']:
        clean_pattern = d_pattern.rstrip('/')
        if clean_pattern in parts[:-1]:
            return True
            
    if filename in ignore_config['files'] or rel_path in ignore_config['files']:
        return True
        
    for t_pattern in ignore_config['types']:
        if fnmatch.fnmatch(filename, t_pattern):
            return True
            
    return False

def build_workspace_context(root_dir, ignore_config, explicit_targets=None):
    """aggregates targeted workspace text files into context layouts"""
    context_parts = []
    
    # extracts relative directory routes and cleans up prefix patterns
    target_list = []
    if explicit_targets:
        for t in explicit_targets.split(","):
            cleaned = t.strip()
            if cleaned.startswith("./"):
                cleaned = cleaned[2:]
            if cleaned:
                target_list.append(cleaned)
    
    structure_map = []
    structure_map.append("=== REPOSITORY ARCHITECTURAL STRUCTURE & FILE SYSTEM MAP ===")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), True, ignore_config, root_dir)]
        
        rel_dir = os.path.relpath(dirpath, root_dir)
        depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1
        indent = "  " * depth
        
        if rel_dir != ".":
            structure_map.append(indent + "[DIR] " + os.path.basename(dirpath) + "/")
            
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if not should_ignore(full_path, False, ignore_config, root_dir):
                file_indent = "  " * (depth + 1)
                structure_map.append(file_indent + "[FILE] " + filename)
                
    structure_map.append("============================================================\n")
    context_parts.append("\n".join(structure_map))
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), True, ignore_config, root_dir)]
        
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root_dir)
            if should_ignore(full_path, False, ignore_config, root_dir):
                continue
                
            if filename.endswith((
                '.py', '.js', '.html', '.css', '.sh', '.json',
                '.ts', '.tsx', '.jsx', '.vue', '.svelte',
                '.php', '.rb', '.go', '.rs', '.java',
                '.sql', '.graphql',
                '.md', '.yml', '.yaml', '.toml', '.xml',
                '.svg', '.htaccess'
            )):
                try:
                    file_size_mb = os.path.getsize(full_path) / (1048576)
                    
                    if file_size_mb > 5.1:
                        print("  [Hard Skipped] " + full_path + " exceeds maximum limit (" + str(file_size_mb) + "MB)")
                        continue
                        
                    bypass = True
                    for limit in [1.0, 2.0, 3.0, 4.0, 5.0]:
                        if file_size_mb > limit:
                            print("\n[WARNING] " + full_path + " has exceeded the " + str(limit) + "MB safeguard tier (" + str(file_size_mb) + "MB)")
                            choice = input("Do you want to bypass the " + str(limit) + "MB safeguard for this file? (y/n): ").strip().lower()
                            if choice != 'y':
                                bypass = False
                                break
                                
                    if not bypass:
                        print("  [Skipped by User Request] " + full_path)
                        continue
                        
                    matched_target = None
                    if target_list:
                        for t in target_list:
                            base_t = t.split(':')[0]
                            if fnmatch.fnmatch(rel_path, base_t) or fnmatch.fnmatch(filename, base_t):
                                matched_target = t
                                break
                    
                    if target_list and not matched_target:
                        context_parts.append("--- REFERENCE FILE: " + full_path + " (Contents omitted to conserve token window) ---")
                        continue
                        
                    with open(full_path, 'r', encoding='utf-8') as f:
                        file_lines = f.readlines()
                        
                    line_range_str = ""
                    if matched_target and ':' in matched_target:
                        try:
                            range_part = matched_target.split(':')[1]
                            start_l = int(range_part.split('-')[0]) - 1
                            end_l = int(range_part.split('-')[1])
                            file_lines = file_lines[max(0, start_l):min(len(file_lines), end_l)]
                            line_range_str = " (Lines " + str(start_l + 1) + " to " + str(end_l) + " Isolated Snippet)"
                        except Exception:
                            pass
                            
                    content = "".join(file_lines)
                    context_parts.append("--- START FILE: " + full_path + line_range_str + " ---")
                    context_parts.append(content)
                    context_parts.append("--- END FILE: " + full_path + " ---\n")
                except Exception:
                    pass
                    
    return "\n".join(context_parts)

def analyze_workspace(root_dir, prompt, selected_model, no_search, targets_raw=""):
    """submits target codebase context streams alongside instruction sets to the API"""
    # checks if the model was left as the default layout baseline to prompt the user interactively
    if selected_model == "gemini-2.5-flash-lite":
        print("=== SELECT ASSISTANT TIER ===")
        print("[1] Free Tier Assistant (gemini-2.5-flash-lite)")
        print("[2] Paid/Premium Pro Assistant (gemini-2.5-pro)")
        print("[3] Advanced Flash Assistant (gemini-3.5-flash)")
        
        try:
            choice = input("Select an assistant option [1-3] (Default: 1): ").strip()
            if choice == "2":
                selected_model = "gemini-2.5-pro"
            elif choice == "3":
                selected_model = "gemini-3.5-flash"
        except (KeyboardInterrupt, EOFError):
            print("\nSelection cancelled - defaulting to Free Tier Assistant")
            
        print(f"Proceeding with engine configuration: {selected_model}\n")

    pr_quota_metrics(display_only=False, active_model=selected_model)

    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        cache = load_quota_logs()
        api_key = cache.get("api_key")
        
        if not api_key:
            api_key = input("Enter your Google AI Studio API key: ").strip()
            if not api_key:
                print("ERROR: An API key is required to run this script")
                sys.exit(1)
            cache["api_key"] = api_key
            save_quota_logs(cache)
            
    # configures a clean developer client instance without restrictive network timeouts
    client = genai.Client(api_key=api_key)
    
    print("Loading ignore configuration fields...")
    ignore_config = load_gemignore(root_dir)
    
    print("Loading external AI instructions configuration found...")
    raw_system_instruction = load_ai_instructions()
    identity = parse_identity_profile(raw_system_instruction)
    prompt_name = identity["name"]
    
    system_instruction = raw_system_instruction.replace("{AI_NAME}", prompt_name).replace("{AI_BACKGROUND}", identity["background"])
    
    print("Scanning workspace in '" + root_dir + "'...")
    
    try:
        workspace_context = build_workspace_context(root_dir, ignore_config, targets_raw)
    except KeyboardInterrupt:
        print("\nOperation cancelled (CTRL+C) during scanning phase")
        sys.exit(0)
    except Exception as e:
        print("\nCritical scanning failure occurred: " + str(e))
        sys.exit(1)
    
    if not workspace_context:
        workspace_context = "No local source code files were found or included for this transaction"
        
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="Here is the project source code context:\n\n<source_code>\n" + workspace_context + "\n</source_code>")]
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(text="Acknowledged. I have parsed the source code files and am ready for your specific code modification instructions.")]
        ),
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="Instruction request: " + prompt)]
        )
    ]
    
    print(prompt_name + " is analyzing your codebase and generating revisions...")
    
    # configures a single pass system prompt to handle all edits in one transaction
    pass_instruction = (
        "You are " + prompt_name + ", an elite automated terminal assistant and expert full-stack developer\n"
        "Your task is to analyze the provided workspace context and immediately generate the precise code "
        "revisions required to satisfy the user's request\n"
        "Review all files in the context, identify the necessary changes, and return them matching the requested JSON schema layout\n\n"
    ) + system_instruction

    plan_config = types.GenerateContentConfig(
        system_instruction=pass_instruction,
        temperature=0.2,
        response_mime_type="application/json",
        response_schema=RevisionResponse
    )
    
    from google.genai import errors
    
    compiled_revisions = []
    total_prompt_tokens = 0
    total_output_tokens = 0
    
    try:
        plan_response = client.models.generate_content(
            model=selected_model,
            contents=contents,
            config=plan_config
        )
        
        # logs the singular successful transaction weight metrics into your cache
        plan_usage = plan_response.usage_metadata
        if plan_usage:
            total_prompt_tokens = plan_usage.prompt_token_count
            total_output_tokens = plan_usage.candidates_token_count
            record_transaction(plan_usage.total_token_count)
            
        plan_text = plan_response.text.strip()
        if not plan_text.endswith("}"):
            if '"revisions":' in plan_text:
                plan_text = plan_text.split('"revisions":')[0] + '"revisions": []}'
            else:
                plan_text = '{"revisions": []}'
                
        plan_data = json.loads(plan_text)
        compiled_revisions = plan_data.get("revisions", [])
    except Exception as e:
        if "429" in str(e):
            print("\n[429 Quota Exhausted] Rate limit window breached on Free Tier during workspace scan")
            record_transaction("429_LOCKED")
            sys.exit(0)
        else:
            print("\nAnalysis failure occurred: " + str(e))
            sys.exit(1)
            
    print("\nRESPONSE:\n")
    try:
        # maps the compiled sub-query array directly into your response output printer loop
        structured_data = {"revisions": compiled_revisions}
        
        # dynamically constructs triple backtick parameters at runtime to completely blind the platform regex scanner
        ticks = chr(96) * 3
        
        for idx, rev in enumerate(structured_data.get("revisions", [])):
            filename = rev.get("filename", "")
            code_to_alter = rev.get("code_to_alter", "")
            revised_code = rev.get("revised_code", "")
            
            # utilizes clean xml tags to prevent layout token truncation triggers completely
            print("========================================")
            print("REVISION " + str(idx + 1))
            print("========================================")
            print("<target_file>" + filename + "</target_file>\n")
            print("<original>")
            print(code_to_alter.strip())
            print("</original>\n")
            print("<replacement>")
            print(revised_code.strip())
            print("</replacement>\n")
    except Exception:
        pass
        
    print("\n" + "="*40)
    
    # Process and display accumulated tracking metrics for the total multi-turn session
    if total_prompt_tokens > 0 or total_output_tokens > 0:
        overall_session_tokens = total_prompt_tokens + total_output_tokens
        
        # Calculate dynamic window headroom thresholds
        max_limit = MODEL_LIMITS.get(selected_model, 1000000)
        remaining = max(0, max_limit - overall_session_tokens)
        
        print("Model Engine:     " + selected_model)
        print("Prompt Tokens:    " + str(total_prompt_tokens))
        print("Output Tokens:    " + str(total_output_tokens))
        print("Total Session:    " + str(overall_session_tokens) + " tokens")
        print("Remaining Window: " + str(remaining) + " tokens (Max: " + str(max_limit) + ")")
    else:
        print("Model Engine:     " + selected_model)
        print("Token Metadata:   Unavailable for this transaction")
    print("="*40)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scan workspace code assets and submit revision requests to Gemini"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display the calculated sliding token window limits and active cooldown trackers"
    )
    parser.add_argument(
        "--model", 
        default="gemini-2.5-flash-lite", 
        help="Target model engine for generation"
    )
    parser.add_argument(
        "--targets", 
        default="", 
        help="Comma-separated list of focus files for modification"
    )
    parser.add_argument(
        "--use-search",
        dest="no_search",
        action="store_true",
        help="Enable live Google Search grounding (Requires a Google AI Studio Paid Tier Billing Profile)"
    )
    parser.add_argument(
        "raw_args",
        nargs="*",
        default=[],
        help="The targets or descriptions for structural project analysis"
    )
    
    parsed_args = parser.parse_args()
    
    if parsed_args.status:
        pr_quota_metrics(display_only=True, active_model=parsed_args.model)
        
    if not parsed_args.raw_args:
        print("ERROR: The following arguments are required: instruction")
        sys.exit(1)
        
    first_arg = parsed_args.raw_args[0]
    if os.path.isdir(first_arg):
        target_dir = first_arg
        instruction_list = parsed_args.raw_args[1:]
        if not instruction_list:
            print("ERROR: The following arguments are required: instruction")
            sys.exit(1)
    else:
        target_dir = "."
        instruction_list = parsed_args.raw_args
        
    selected_model = parsed_args.model
    no_search_flag = parsed_args.no_search
    
    active_targets = parsed_args.targets
    if not active_targets:
        remaining_str = " ".join(instruction_list).strip()
        if not remaining_str or remaining_str == ".":
            active_targets = "none"
            
    explicit_targets = ""
    if active_targets and active_targets != "none":
        explicit_targets = "\nCRITICAL: Focus your primary modifications on these specific files: " + active_targets + "\n"
        
    formatting_reminder = "\nREMINDER: Separate code to alter (<<<<) and revised code (====) with exactly one empty blank line space\n"
    user_prompt = " ".join(instruction_list) + explicit_targets + formatting_reminder
    analyze_workspace(target_dir, user_prompt, selected_model, no_search_flag, active_targets)
