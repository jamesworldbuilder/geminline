#!/usr/bin/env python3
import os
import sys
import fnmatch
import time
import json
from google import genai
from google.genai import types

# Model context limit mapping guidelines
MODEL_LIMITS = {
    'gemini-3.5-flash': 1000000,
    'gemini-3.1-pro': 2000000,
    'gemini-2.5-flash': 1000000,
    'gemini-2.5-pro': 2000000
}

# Free tier local baseline limits (RPM, TPM)
FREE_LIMITS = {
    'requests': 15,
    'tokens': 1000000
}

def get_tracker_path():
    """Returns the persistent hidden file path for localized limit metrics"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '.cyrus_quota_history.json')

def load_quota_logs():
    """Reads transaction records safely out of the local cache configuration asset"""
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
    """Saves updated call instances back down to disk storage targets"""
    try:
        with open(get_tracker_path(), 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception:
        pass

def pr_quota_metrics(display_only=False):
    """Parses local execution loops and displays a real-time sliding window telemetry dashboard"""
    now = time.time()
    cache = load_quota_logs()
    logs = cache.get("logs", [])
    
    # Filter for logs that fall inside the current active 60-second rolling window
    active_window_logs = [log for log in logs if now - log['timestamp'] < 60]
    
    if len(logs) != len(active_window_logs):
        cache["logs"] = active_window_logs
        save_quota_logs(cache)
        
    req_count = len(active_window_logs)
    
    # Filter out lock flags from numerical math aggregation
    token_count = sum(log['tokens'] for log in active_window_logs if isinstance(log['tokens'], (int, float)))
    server_locked = any(log['tokens'] == "429_LOCKED" for log in active_window_logs)
    
    req_left = max(0, FREE_LIMITS['requests'] - req_count)
    tokens_left = 0 if server_locked else max(0, FREE_LIMITS['tokens'] - token_count)
    
    # Calculate exactly when the oldest tracking transaction drops out of the sliding loop
    cooldown = 0
    if active_window_logs:
        oldest_ts = active_window_logs[0]['timestamp']
        cooldown = max(0, int(60 - (now - oldest_ts)))
        
    print("\n=== FREE TIER RUNTIME TELEMETRY ===")
    print(f"Requests (Last 60s): {req_count}/{FREE_LIMITS['requests']}  (Headroom remaining: {req_left})")
    
    if server_locked:
        print(f"Tokens Used (Last 60s): [429 RESOURCE_EXHAUSTED]")
        print(f"\n[ALERT] Quota ceiling breached - Cool-down lock active for another: {cooldown}s")
    else:
        print(f"Tokens Used (Last 60s): {token_count:,}/{FREE_LIMITS['tokens']:,} (Headroom remaining: {tokens_left:,})")
        if req_left == 0:
            print(f"\n[ALERT] Quota ceiling breached - Cool-down lock active for another: {cooldown}s")
        else:
            print(f"Window State: Stable (Next token slot refresh calculation in: {cooldown}s)")
    print("===================================\n")
    
    if display_only:
        sys.exit(0)
        
    if req_left == 0 or server_locked:
        print(f"Automatic protection block triggered - Halting call loop to prevent a remote 429 error...")
        try:
            for remaining in range(cooldown, 0, -1):
                sys.stdout.write(f"\r  Resuming terminal execution pipeline in: {remaining}s...")
                sys.stdout.flush()
                time.sleep(1)
            print("\n[Cleared] Proceeding with transaction scan...")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled (CTRL+C) during countdown loop phase")
            sys.exit(0)

def record_transaction(total_tokens):
    """Logs a successful transaction sequence with token weights directly into history files"""
    cache = load_quota_logs()
    cache["logs"].append({
        'timestamp': time.time(),
        'tokens': total_tokens
    })
    save_quota_logs(cache)

def load_gemignore(root_dir):
    """Parses and reads file filtering structures out of the local configuration file"""
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
            # Skip comments and empty tracking markers
            if not line or line.startswith('#'):
                continue
                
            # Detect category boundaries
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
    """Loads system instructions from a external text file located alongside the script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    instructions_path = os.path.join(script_dir, 'gemini-instructions.txt')
    
    if not os.path.exists(instructions_path):
        print(f"ERROR: Core AI instructions configuration not found at {instructions_path}")
        sys.exit(1)
        
    with open(instructions_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def parse_identity_profile(instructions_text):
    """Parses the customized identity moniker and background details out of the instruction text blocks"""
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
    """Evaluates workspace assets against the loaded parsing rules"""
    rel_path = os.path.relpath(path, root_dir)
    parts = rel_path.split(os.sep)
    filename = os.path.basename(path)
    
    # Process explicit directory matching
    if is_dir:
        for d_pattern in ignore_config['directories']:
            clean_pattern = d_pattern.rstrip('/')
            if clean_pattern in parts:
                return True
        return False
        
    # Process parent directories for target file paths
    for d_pattern in ignore_config['directories']:
        clean_pattern = d_pattern.rstrip('/')
        if clean_pattern in parts[:-1]:
            return True
            
    # Process explicit file name matching
    if filename in ignore_config['files'] or rel_path in ignore_config['files']:
        return True
        
    # Process wildcard extension and pattern filters
    for t_pattern in ignore_config['types']:
        if fnmatch.fnmatch(filename, t_pattern):
            return True
            
    return False

def build_workspace_context(root_dir, ignore_config, explicit_targets=None):
    """Walks the directory and aggregates files into a single context string"""
    context_parts = []
    target_list = [t.strip() for t in explicit_targets.split(",") if t.strip()] if explicit_targets else []
    
    # Generate structural workspace file tree layout map
    structure_map = []
    structure_map.append("=== REPOSITORY ARCHITECTURAL STRUCTURE & FILE SYSTEM MAP ===")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune ignored tracking targets dynamically in-place
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), True, ignore_config, root_dir)]
        
        rel_dir = os.path.relpath(dirpath, root_dir)
        depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1
        indent = "  " * depth
        
        if rel_dir != ".":
            structure_map.append(f"{indent}[DIR] {os.path.basename(dirpath)}/")
            
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if not should_ignore(full_path, False, ignore_config, root_dir):
                file_indent = "  " * (depth + 1)
                structure_map.append(f"{file_indent}[FILE] {filename}")
                
    structure_map.append("============================================================\n")
    context_parts.append("\n".join(structure_map))
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune ignored tracking targets dynamically in-place
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), True, ignore_config, root_dir)]
        
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root_dir)
            if should_ignore(full_path, False, ignore_config, root_dir):
                continue
                
            # Filter for common web development textual assets
            if filename.endswith((
                '.py', '.js', '.html', '.css', '.sh', '.json',
                '.ts', '.tsx', '.jsx', '.vue', '.svelte',
                '.php', '.rb', '.go', '.rs', '.java',
                '.sql', '.graphql',
                '.md', '.yml', '.yaml', '.toml', '.xml',
                '.svg', '.htaccess'
            )):
                try:
                    # Check physical file sizing metrics
                    file_size_mb = os.path.getsize(full_path) / (1048576)
                    
                    # Enforce processing safety cap protections
                    if file_size_mb > 5.1:
                        print(f"  [Hard Skipped] {full_path} exceeds maximum limit ({file_size_mb:.2f}MB)")
                        continue
                        
                    # Sequential interactive threshold evaluations
                    bypass = True
                    for limit in [1.0, 2.0, 3.0, 4.0, 5.0]:
                        if file_size_mb > limit:
                            print(f"\n[WARNING] {full_path} has exceeded the {limit}MB safeguard tier ({file_size_mb:.2f}MB)")
                            choice = input(f"Do you want to bypass the {limit}MB safeguard for this file? (y/n): ").strip().lower()
                            if choice != 'y':
                                bypass = False
                                break
                                
                    if not bypass:
                        print(f"  [Skipped by User Request] {full_path}")
                        continue
                        
                    # If specific targets are provided, compress unrequested giant files to reference headers only
                    if target_list and not any(fnmatch.fnmatch(rel_path, t) or fnmatch.fnmatch(filename, t) for t in target_list):
                        context_parts.append(f"--- REFERENCE FILE: {full_path} (Contents omitted to conserve token window) ---")
                        continue
                        
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Append clear layout tags for contextual isolation boundaries
                    context_parts.append(f"--- START FILE: {full_path} ---")
                    context_parts.append(content)
                    context_parts.append(f"--- END FILE: {full_path} ---\n")
                except Exception:
                    # Ignore unreadable files safely
                    pass
                    
    return "\n".join(context_parts)

def analyze_workspace(root_dir, prompt, selected_model, no_search, targets_raw=""):
    """Sends the entire workspace and the user task to Gemini"""
    # Evaluate client-side rolling limits before calling the remote server
    pr_quota_metrics(display_only=False)

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
            
    client = genai.Client(api_key=api_key)
    
    print("Loading ignore configuration fields...")
    ignore_config = load_gemignore(root_dir)
    
    print("Loading external AI instructions configuration found...")
    raw_system_instruction = load_ai_instructions()
    identity = parse_identity_profile(raw_system_instruction)
    prompt_name = identity["name"]
    
    # Inject configuration variables into placeholders if string brackets are present
    try:
        system_instruction = raw_system_instruction.format(
            AI_NAME=prompt_name,
            AI_BACKGROUND=identity["background"]
        )
    except KeyError:
        system_instruction = raw_system_instruction
    
    print(f"Scanning workspace in '{root_dir}'...")
    
    # Safely isolate scanning tasks against abrupt halts or disk failures
    try:
        workspace_context = build_workspace_context(root_dir, ignore_config, targets_raw)
    except KeyboardInterrupt:
        print("\nOperation cancelled (CTRL+C) during scanning phase")
        sys.exit(0)
    except Exception as e:
        print(f"\nCritical scanning failure occurred: {e}")
        sys.exit(1)
    
    # Check if context parsing output contents are present
    if not workspace_context:
        workspace_context = "No local source code files were found or included for this transaction"
        
    contents = [
        f"Current Workspace Files and Content:\n\n{workspace_context}",
        f"User Multi-Part Request: {prompt}"
    ]
    
    print(f"{prompt_name} is analyzing your workspace via {selected_model}...")
    
    # Configure the generation options layout utilizing maximum token ceilings
    gen_config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.1,
        max_output_tokens=8192
    )
    
    # Inject search tools only if explicitly requested via paid billing profiles
    if no_search:
        gen_config.tools = [types.Tool(google_search=types.GoogleSearch())]
    
    from google.genai import errors
    
    try:
        response = client.models.generate_content(
            model=selected_model,
            contents=contents,
            config=gen_config
        )
    except errors.ClientError as e:
        if "429" in str(e):
            print("\n[429 Quota Exhausted] Rate limit window breached on Free Tier")
            # Save failure marker to block sequential loops automatically
            record_transaction("429_LOCKED")
            try:
                for remaining in range(65, 0, -1):
                    sys.stdout.write(f"\r  Cool-down active - Remaining window time: {remaining}s...")
                    sys.stdout.flush()
                    time.sleep(1)
                print("\n\n[Reset Complete] Free Tier sliding window has cleared - Please re-run the command")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled (CTRL+C) during cooldown countdown")
            sys.exit(0)
        elif any(err in str(e) for err in ["400", "403"]):
            print(f"\nERROR: Authentication rejected by Google GenAI engine ({e})")
            print("Please clear your saved key metrics or export a validated API token string")
            sys.exit(1)
        else:
            raise e
    
    print("\nRESPONSE:\n")
    print(response.text)
    
    # Process and append verified search grounding landing pages if present
    try:
        metadata = response.candidates[0].grounding_metadata
        if metadata and metadata.grounding_chunks:
            print("\nSOURCE LINK:")
            seen_links = set()
            for chunk in metadata.grounding_chunks:
                if chunk.web and chunk.web.uri:
                    uri = chunk.web.uri
                    if uri not in seen_links:
                        print(f"- {uri}")
                        seen_links.add(uri)
    except Exception:
        pass
        
    print("\n" + "="*40)
    
    # Process and display tracking metrics using response metadata profiles
    usage = response.usage_metadata
    if usage:
        prompt_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count
        total_tokens = usage.total_token_count
        
        # Log token consumption right down into the local cache file
        record_transaction(total_tokens)
        
        # Calculate dynamic window headroom thresholds
        max_limit = MODEL_LIMITS.get(selected_model, 1000000)
        remaining = max(0, max_limit - total_tokens)
        
        print(f"Model Engine:     {selected_model}")
        print(f"Prompt Tokens:    {prompt_tokens}")
        print(f"Output Tokens:    {output_tokens}")
        print(f"Total Session:    {total_tokens} tokens")
        print(f"Remaining Window: {remaining} tokens (Max: {max_limit})")
    else:
        print(f"Model Engine:     {selected_model}")
        print("Token Metadata:   Unavailable for this transaction")
    print("="*40)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scan workspace code assets and submit revision requests to Gemini"
    )
    
    # Configuration positional and modification argument configurations
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display the calculated sliding token window limits and active cooldown trackers"
    )
    parser.add_argument(
        "--model", 
        default="gemini-3.5-flash", 
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
    
    # Intercept commands immediately if checking local quota metrics
    if parsed_args.status:
        pr_quota_metrics(display_only=True)
        
    if not parsed_args.raw_args:
        print("ERROR: The following arguments are required: instruction")
        sys.exit(1)
        
    # Isolate targets from text descriptions by checking path status
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
    
    explicit_targets = ""
    if parsed_args.targets:
        explicit_targets = f"\nCRITICAL: Focus your primary modifications on these specific files: {parsed_args.targets}\n"
        
    user_prompt = " ".join(instruction_list) + explicit_targets
    analyze_workspace(target_dir, user_prompt, selected_model, no_search_flag, parsed_args.targets)
    
