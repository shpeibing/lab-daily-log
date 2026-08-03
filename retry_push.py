import os, subprocess, time
repo = r'D:\AiPy文件\3\deploy_git'
os.chdir(repo)
# 重试推送
for attempt in range(3):
    r = subprocess.run('git push origin main', shell=True, capture_output=True, text=True, encoding='utf-8')
    print(f"尝试 {attempt+1}:")
    if r.stdout.strip(): print(r.stdout.strip())
    if r.stderr.strip(): print(r.stderr.strip())
    if r.returncode == 0:
        print("✅ 推送成功！")
        break
    else:
        print("⚠️ 网络问题，2秒后重试...")
        time.sleep(2)