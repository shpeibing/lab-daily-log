import os, subprocess, time
repo = r'D:\AiPy文件\3\deploy_git'
os.chdir(repo)
# 先pull再push
r = subprocess.run('git pull origin main --allow-unrelated-histories', shell=True, capture_output=True, text=True, encoding='utf-8')
print(f"pull: {r.stdout.strip()[:200]}")
print(f"pull err: {r.stderr.strip()[:200]}")
# 如果有冲突，强制覆盖
if 'conflict' in r.stderr.lower() or 'conflict' in r.stdout.lower():
    print("⚠️ 有冲突，强制推送")
    r = subprocess.run('git push origin main --force', shell=True, capture_output=True, text=True, encoding='utf-8')
else:
    r = subprocess.run('git push origin main', shell=True, capture_output=True, text=True, encoding='utf-8')
print(f"push: {r.stdout.strip()[:200]}")
print(f"push err: {r.stderr.strip()[:200]}")
if r.returncode == 0:
    print("✅ 推送成功！")
else:
    print("⚠️ 仍然失败，尝试强制推送")
    r = subprocess.run('git push origin main --force', shell=True, capture_output=True, text=True, encoding='utf-8')
    if r.returncode == 0:
        print("✅ 强制推送成功！")
    else:
        print(f"❌ 推送失败: {r.stderr.strip()[:100]}")