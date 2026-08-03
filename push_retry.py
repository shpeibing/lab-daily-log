import os, subprocess, sys
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
os.chdir(git_dir)
print("📌 尝试多种方式推送GitHub...")
# 方法1: 使用GitHub API上传
print("\n方法1: 使用GitHub API...")
import requests, base64, json
try:
    # 读取index.html
    with open(os.path.join(git_dir, 'index.html'), 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"  index.html: {len(content)} 字符")
    # 使用GitHub API上传文件
    # 首先检查仓库
    repo_url = 'https://api.github.com/repos/shpeibing/lab-daily-log'
    resp = requests.get(repo_url, timeout=10)
    if resp.status_code == 200:
        repo_info = resp.json()
        print(f"  ✅ 仓库存在: {repo_info.get('full_name')}")
        print(f"  🌐 默认分支: {repo_info.get('default_branch')}")
        print(f"  📦 公开: {repo_info.get('visibility', 'public')}")
        # 检查Pages状态
        pages_url = 'https://api.github.com/repos/shpeibing/lab-daily-log/pages'
        resp = requests.get(pages_url, timeout=10)
        if resp.status_code == 200:
            pages_info = resp.json()
            print(f"  ✅ GitHub Pages已启用!")
            print(f"  🌐 访问地址: {pages_info.get('html_url', 'https://shpeibing.github.io/lab-daily-log/')}")
        elif resp.status_code == 404:
            print(f"  ⚠️ GitHub Pages未启用 (404)")
        else:
            print(f"  ⚠️ Pages检查失败: {resp.status_code}")
    else:
        print(f"  ⚠️ 仓库检查失败: {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ API检查失败: {e}")
# 方法2: 尝试SSH推送
print("\n方法2: 尝试SSH推送...")
result = subprocess.run(['git', 'remote', '-v'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
print(f"  当前remote: {result.stdout}")
# 尝试使用SSH
result = subprocess.run(['git', 'push', 'git@github.com:shpeibing/lab-daily-log.git', 'main'], capture_output=True, encoding='utf-8', errors='replace', timeout=30)
if result.returncode == 0:
    print("  ✅ SSH推送成功!")
else:
    print(f"  ⚠️ SSH推送失败: {result.stderr[:200] if result.stderr else 'Unknown'}")
# 方法3: 尝试使用代理
print("\n方法3: 尝试使用代理推送...")
# 检查是否有代理配置
result = subprocess.run(['git', 'config', '--global', '--get', 'http.proxy'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
print(f"  HTTP代理: {result.stdout.strip() if result.stdout else '未配置'}")
# 尝试使用HTTPS直接推送（带重试）
print("\n方法4: HTTPS重试...")
for i in range(3):
    print(f"  尝试 {i+1}/3...")
    result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, encoding='utf-8', errors='replace', timeout=30)
    if result.returncode == 0:
        print("  ✅ 推送成功!")
        break
    else:
        err = result.stderr[:200] if result.stderr else 'Unknown'
        print(f"  ⚠️ 推送失败: {err}")
        if i < 2:
            import time
            time.sleep(3)
# 最终状态
print("\n📌 最终状态:")
result = subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
print(f"  最近提交: {result.stdout}")
# 检查GitHub Pages是否可访问
print("\n📌 检查GitHub Pages...")
try:
    resp = requests.get('https://shpeibing.github.io/lab-daily-log/', timeout=10)
    print(f"  HTTP状态: {resp.status_code}")
    if resp.status_code == 200:
        print("  ✅ GitHub Pages访问正常!")
        if 'showMonthlyReport' in resp.text:
            print("  ✅ 最新版本已部署!")
        else:
            print("  ⚠️ 页面可能不是最新版本")
    else:
        print(f"  ⚠️ 状态: {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ 访问失败: {e}")
print("\n✅ 完成!")