import os

# Define the directory structure
folder_structure = {
    'tasc': [
        'data/raw',
        'data/processed',
        'docs',
        'models/image_recognition',
        'models/nlp',
        'models/color_matching',
        'notebooks',
        'src/clothing',
        'src/engine',
        'src/utils',
        'src/user',
        'tests',
        'web/static',
        'web/templates',
    ],
}

# Base path where you want to create the project structure
base_path = os.path.join(os.getcwd(), 'tasc')

# Create the directories
for key, paths in folder_structure.items():
    for path in paths:
        dir_path = os.path.join(base_path, path)
        os.makedirs(dir_path, exist_ok=True)
        # Create __init__.py in each subdirectory to make them Python packages
        with open(os.path.join(dir_path, '__init__.py'), 'a') as init_file:
            pass

# Create additional files at the base of the project
additional_files = [
    'README.md',
    'requirements.txt',
    'setup.py',
    'web/app.py',
]

for file_name in additional_files:
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'a') as file:
        pass

print(f"Project structure created at {base_path}")
