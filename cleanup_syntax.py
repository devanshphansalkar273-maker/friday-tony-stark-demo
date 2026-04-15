import os
import re

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace escaped triple quotes \"\"\" with \"\"\"
    # Replace escaped single quotes \' with '
    # Replace escaped double quotes \" with "
    
    new_content = content.replace('\\"\\"\\"', '"""')
    new_content = new_content.replace("\\'", "'")
    # Be careful with \" as it might be legitimate inside a string, 
    # but the ones we are seeing are likely all illegitimate based on the corruption.
    # However, let's target the most problematic ones first.
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned: {filepath}")

def walk_and_clean(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                clean_file(os.path.join(root, file))

if __name__ == "__main__":
    target_dir = "friday"
    if os.path.exists(target_dir):
        walk_and_clean(target_dir)
    else:
        print(f"Directory {target_dir} not found.")
