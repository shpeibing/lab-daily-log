import os, subprocess
repo = r'D:\AiPy文件\3\git_push'
os.chdir(repo)
print("=== git_push目录 ===")
for f in os.listdir(repo):
    print(f"  {f}")
r = subprocess.run('git remote -v', shell=True, capture_output=True, text=True, encoding='utf-8')
print(f"\n=== git remote ===\n{r.stdout}")
r = subprocess.run('git status', shell=True, capture_output=True, text=True, encoding='utf-8')
print(f"\n=== git status ===\n{r.stdout}")