import os, shutil
n = 0
for root, dirs, files in os.walk('.'):
    for d in list(dirs):
        if d == '__pycache__':
            shutil.rmtree(os.path.join(root, d), ignore_errors=True)
            dirs.remove(d)
            n += 1
print(f"Cleared {n} __pycache__ dirs")
