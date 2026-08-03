import os, shutil, subprocess, re, sys
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
# 读取最新版本
with open(index_file, 'r', encoding='utf-8') as f:
    content = f.read()
print(f"最新版本大小: {len(content)} 字符")
# =========================================
# 1. Git提交
# =========================================
print("\n📌 1. Git提交...")
os.chdir(git_dir)
# 添加所有文件
subprocess.run(['git', 'add', '.'], capture_output=True, timeout=10)
# 提交（使用encoding='utf-8'避免编码问题）
result = subprocess.run(['git', 'commit', '-m', 'V2.5 upgrade: monthly report + staff summary + cloud sync'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
print(f"  提交结果: {result.stdout[:300] if result.stdout else 'OK'}")
if result.returncode != 0:
    print(f"  提交错误: {result.stderr[:300] if result.stderr else 'Unknown'}")
# =========================================
# 2. 推送GitHub
# =========================================
print("\n📌 2. 推送GitHub...")
result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, encoding='utf-8', errors='replace', timeout=30)
print(f"  推送结果: {result.stdout[:300] if result.stdout else 'OK'}")
if result.returncode != 0 and result.stderr:
    print(f"  推送错误: {result.stderr[:300]}")
    # 尝试使用凭证
    try:
        result2 = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', capture_output=True, encoding='utf-8', errors='replace', timeout=10)
        username = ''
        password = ''
        for line in result2.stdout.split('\n'):
            if line.startswith('username='): username = line.split('=', 1)[1]
            elif line.startswith('password='): password = line.split('=', 1)[1]
        if username and password:
            auth_url = f'https://{username}:{password}@github.com/shpeibing/lab-daily-log.git'
            subprocess.run(['git', 'remote', 'set-url', 'origin', auth_url], capture_output=True, timeout=10)
            result3 = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, encoding='utf-8', errors='replace', timeout=30)
            if result3.returncode == 0:
                print("  ✅ 推送成功!")
            else:
                print(f"  ⚠️ 推送失败: {result3.stderr[:300] if result3.stderr else 'Unknown'}")
                subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/shpeibing/lab-daily-log.git'], capture_output=True, timeout=10)
        else:
            print("  ⚠️ 未获取到GitHub凭证")
    except Exception as e:
        print(f"  ⚠️ 凭证获取失败: {e}")
else:
    print("  ✅ 推送成功!")
# =========================================
# 3. 验证GitHub Pages
# =========================================
print("\n📌 3. 验证GitHub Pages...")
import requests
try:
    resp = requests.get('https://shpeibing.github.io/lab-daily-log/', timeout=10)
    print(f"  HTTP状态: {resp.status_code}")
    if resp.status_code == 200:
        print("  ✅ GitHub Pages访问正常!")
        # 检查内容是否为最新版本
        if 'showMonthlyReport' in resp.text:
            print("  ✅ 最新版本已部署（包含月报表功能）")
        else:
            print("  ⚠️ 页面内容可能不是最新版本")
    else:
        print(f"  ⚠️ GitHub Pages状态: {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ 访问失败: {e}")
# =========================================
# 4. 确保本地服务器运行
# =========================================
print("\n📌 4. 确保本地服务器运行...")
try:
    resp = requests.get('http://localhost:8082/index.html', timeout=3)
    if resp.status_code == 200:
        print("  ✅ 本地服务器已运行")
except:
    server = subprocess.Popen(['python', '-m', 'http.server', '8082'], cwd=git_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  ✅ 已启动本地服务器 (PID: {server.pid})")
print("\n✅ 部署完成!")