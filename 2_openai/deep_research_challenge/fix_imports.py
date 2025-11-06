"""Quick script to fix relative imports."""
import re

files_to_fix = [
    'agent_registry.py',
    'handoff_controller.py',
    'state_machine.py',
    'trail_manager.py',
    'clarification_engine.py',
    'progress_monitor.py',
    'evaluation_engine.py',
    'trail_execution.py',
    'trail_discovery.py'
]

for filename in files_to_fix:
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace relative imports with try/except for both styles
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        if line.startswith('from .'):
            # Found a relative import
            module = line.replace('from .', '').strip()
            new_lines.append(f'try:')
            new_lines.append(f'    from .{module}')
            new_lines.append(f'except ImportError:')
            new_lines.append(f'    from {module}')
        else:
            new_lines.append(line)
        i += 1
    
    with open(filename, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f'Fixed {filename}')

print('Done!')
