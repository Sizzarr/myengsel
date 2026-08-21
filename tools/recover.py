import json

log_path = r"C:\Users\Administrator\.gemini\antigravity-ide\brain\46ab4c77-39c8-41e1-b6ea-c2fa6891f3f9\.system_generated\logs\transcript_full.jsonl"
apply_path = r"c:\Users\Administrator\Downloads\me-cli-sunset-web-ui\me-cli-sunset-main\apply_redesign_css.py"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'apply_redesign_css.py' in line and '"type":"VIEW_FILE"' in line:
            try:
                data = json.loads(line)
                content = data.get('content') or data.get('output')
                if content and 'Showing lines 1 to 252' in content:
                    # we got it
                    code = []
                    lines = content.split('\n')
                    for l in lines:
                        if ':' in l and l.split(':')[0].isdigit():
                            # The number must be from 1 to 252
                            num = int(l.split(':')[0])
                            if 1 <= num <= 252:
                                code.append(l.split(':', 1)[1][1:])
                    with open(apply_path, 'w', encoding='utf-8') as out:
                        out.write('\n'.join(code))
                    print("Extracted apply_redesign_css.py perfectly!")
                    exit(0)
            except Exception as e:
                print(e)
