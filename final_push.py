import os, subprocess, time
repo = r'D:\AiPy文件\3\deploy_git'
os.chdir(repo)
# 尝试推送，最多5次
for attempt in range(5):
    r = subprocess.run('git push origin main', shell=True, capture_output=True, text=True, encoding='utf-8')
    if r.returncode == 0:
        print(f"✅ 推送成功！(第{attempt+1}次尝试)")
        print(r.stdout.strip())
        break
    print(f"⚠️ 第{attempt+1}次失败: {r.stderr.strip()[:100]}")
    if attempt < 4:
        print("   等待5秒后重试...")
        time.sleep(5)
else:
    print("❌ 多次尝试失败，网络可能暂时不可用")
    print("本地文件已更新，网络恢复后可重新推送")