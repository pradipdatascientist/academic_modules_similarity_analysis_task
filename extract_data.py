import re
import json
import sys
import argparse

def extract_modules(text):
    # Normalize whitespace and handle line breaks
    text = re.sub(r'\r\n', '\n', text)
    
    # Split by "Module Code:" but keep the delimiter
    parts = re.split(r'(Module Code:)', text)
    modules_raw = []
    for i in range(1, len(parts), 2):
        modules_raw.append(parts[i] + parts[i+1])
    
    modules = []
    for raw in modules_raw:
        module = {}
        
        # Extract Code
        code_match = re.search(r'Module Code:\s*(\w+)', raw)
        if code_match:
            module['code'] = code_match.group(1).strip()
        else:
            continue
            
        # Extract Title
        title_match = re.search(r'Title:\s*(.*?)(?:\n|Version:)', raw)
        if title_match:
            module['title'] = title_match.group(1).strip().replace(' APPROVED', '').replace(' NON-EVENT DEAN OF SCHOOL APPROVAL', '').replace(' QUALITY EVENT', '')
            
        # Extract Level
        level_match = re.search(r'SCQF Level:\s*Level\s*(\d+)', raw)
        if level_match:
            module['level'] = int(level_match.group(1))
            
        # Extract Aim - Improved regex to handle variations and ensure it stops at Learning Outcomes
        # We use a non-greedy match and look ahead for the start of the next section
        aim_match = re.search(r'Module Aim:\s*(.*?)(?=\n\s*Learning Outcomes|\n\s*Requisites|\n\s*Indicative Content|\n\s*Module Details|\n\s*--- PAGE|$)', raw, re.DOTALL)
        if aim_match:
            module['aim'] = re.sub(r'\s+', ' ', aim_match.group(1).strip())
        else:
            module['aim'] = ""
            
        # Extract Learning Outcomes
        lo_section = re.search(r'Learning Outcomes\s*On successful completion of this Module the learner will be able to:\s*# Learning Outcome Description\s*(.*?)(?=\n\s*Requisites|\n\s*Indicative Content|\n\s*Module Details|\n\s*--- PAGE|$)', raw, re.DOTALL)
        if lo_section:
            lo_text = lo_section.group(1).strip()
            los = re.findall(r'LO\d+\s+(.*?)(?=\n\s*LO\d+|\n\s*Requisites|\n\s*Indicative Content|\n\s*Module Details|\n\s*--- PAGE|$)', lo_text, re.DOTALL)
            module['learning_outcomes'] = [re.sub(r'\s+', ' ', lo.strip()) for lo in los]
        else:
            module['learning_outcomes'] = []
            
        # Extract Indicative Content
        content_match = re.search(r'Indicative Content\s*(.*?)(?=\n\s*Module Code:|\n\s*--- PAGE|\n\s*Module Details|$)', raw, re.DOTALL)
        if content_match:
            module['indicative_content'] = re.sub(r'\s+', ' ', content_match.group(1).strip())
        else:
            module['indicative_content'] = ""
            
        modules.append(module)
    
    # Deduplicate by code
    unique_modules = {}
    for m in modules:
        if m['code'] not in unique_modules:
            unique_modules[m['code']] = m
            
    return list(unique_modules.values())

def validate_data(modules):
    stats = {
        "total_modules": len(modules),
        "missing_aims": [],
        "missing_los": [],
        "total_los": 0
    }
    
    for m in modules:
        if not m['aim']:
            stats["missing_aims"].append(m['code'])
        if not m['learning_outcomes']:
            stats["missing_los"].append(m['code'])
        stats["total_los"] += len(m['learning_outcomes'])
    
    stats["avg_los"] = stats["total_los"] / len(modules) if modules else 0
    
    for code in stats["missing_aims"]:
        print(f"WARNING: {code} missing aim", file=sys.stderr)
    for code in stats["missing_los"]:
        print(f"WARNING: {code} missing learning outcomes", file=sys.stderr)
        
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract module data from text.')
    parser.add_argument('--input', type=str, help='Input text file path (default: stdin)')
    parser.add_argument('--output', type=str, default='modules.json', help='Output JSON file path')
    args = parser.parse_args()

    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    modules = extract_modules(content)
    stats = validate_data(modules)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(modules, f, indent=2)
    
    # Save stats for the explanation document
    with open('extraction_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Extracted {len(modules)} unique modules to {args.output}")
