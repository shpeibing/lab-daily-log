import os, subprocess, requests, base64, json, shutil, time
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
print("=" * 60)
print("☁️ 使用Token上传到GitHub")
print("=" * 60)
# 读取文件
with open(index_file, 'r', encoding='utf-8') as f:
    html_content = f.read()
print(f"📄 主文件: {len(html_content)} 字符")
# 检查各种可能的Token来源
print("\n📌 查找GitHub Token...")
token = None
# 1. 环境变量
token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
if token:
    print("✅ 从环境变量找到Token")
# 2. Git配置
if not token:
    result = subprocess.run(['git', 'config', '--global', '--list'], capture_output=True, text=True, timeout=10)
    for line in result.stdout.split('\n'):
        if 'token' in line.lower() or 'password' in line.lower():
            parts = line.split('=')
            if len(parts) == 2:
                token = parts[1].strip()
                print(f"✅ 从Git配置找到Token")
                break
# 3. 检查git credential helper
if not token:
    result = subprocess.run(['git', 'config', '--global', 'credential.helper'], capture_output=True, text=True, timeout=10)
    if result.stdout.strip():
        print(f"📌 Git凭证管理器: {result.stdout.strip()}")
        # 尝试从Windows凭证管理器获取
        try:
            result = subprocess.run(['cmd', '/c', 'git credential-manager get'], 
                                   input='protocol=https\nhost=github.com\n\n', 
                                   capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n'):
                if 'password' in line.lower():
                    parts = line.split('=')
                    if len(parts) == 2:
                        token = parts[1].strip()
                        print("✅ 从Windows凭证管理器找到Token")
                        break
        except:
            pass
# 4. 检查~/.git-credentials
if not token:
    cred_file = os.path.expanduser('~/.git-credentials')
    if os.path.exists(cred_file):
        with open(cred_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'github.com' in content:
                # 提取token
                import re
                match = re.search(r'https://([^:]+):([^@]+)@github\.com', content)
                if match:
                    token = match.group(2)
                    print("✅ 从.git-credentials找到Token")
if not token:
    print("⚠️ 未找到GitHub Token")
    print("📌 请手动设置Token后重试")
    print("   1. 访问: https://github.com/settings/tokens")
    print("   2. 生成新Token（勾选repo权限）")
    print("   3. 设置环境变量: set GITHUB_TOKEN=你的token")
    print("   或运行: git remote set-url origin https://用户名:token@github.com/shpeibing/lab-daily-log.git")
else:
    print(f"\n📌 使用Token上传文件...")
    repo = 'shpeibing/lab-daily-log'
    branch = 'main'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # 上传index.html到仓库根目录（GitHub Pages默认从根目录或docs目录发布）
    encoded = base64.b64encode(html_content.encode()).decode()
    # 检查文件是否已存在
    url = f'https://api.github.com/repos/{repo}/contents/index.html'
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        # 文件已存在，获取sha并更新
        sha = resp.json()['sha']
        data = {
            'message': 'V2.4 升级：副主任权限+云端上传优化',
            'content': encoded,
            'sha': sha,
            'branch': branch
        }
        resp = requests.put(url, json=data, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            print("✅ index.html更新成功！")
        else:
            print(f"⚠️ 更新失败: {resp.status_code}")
            print(resp.text[:200])
    elif resp.status_code == 404:
        # 文件不存在，创建新文件
        data = {
            'message': 'V2.4 升级：副主任权限+云端上传优化',
            'content': encoded,
            'branch': branch
        }
        resp = requests.put(url, json=data, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            print("✅ index.html创建成功！")
        else:
            print(f"⚠️ 创建失败: {resp.status_code}")
            print(resp.text[:200])
    else:
        print(f"⚠️ 检查文件失败: {resp.status_code}")
        print(resp.text[:200])
    # 上传manifest.json和sw.js
    for fname in ['manifest.json', 'sw.js']:
        src = os.path.join(git_dir, fname)
        if os.path.exists(src):
            with open(src, 'r', encoding='utf-8') as f:
                content = f.read()
            encoded = base64.b64encode(content.encode()).decode()
            url = f'https://api.github.com/repos/{repo}/contents/{fname}'
            # 检查是否存在
            resp = requests.get(url, headers=headers, timeout=10)
            sha = resp.json()['sha'] if resp.status_code == 200 else None
            data = {
                'message': f'上传{fname}',
                'content': encoded,
                'branch': branch
            }
            if sha:
                data['sha'] = sha
            resp = requests.put(url, json=data, headers=headers, timeout=10)
            if resp.status_code in [200, 201]:
                print(f"✅ {fname}上传成功！")
            else:
                print(f"⚠️ {fname}上传失败: {resp.status_code}")
    # 检查GitHub Pages是否已启用
    print("\n📌 检查GitHub Pages状态...")
    url = f'https://api.github.com/repos/{repo}/pages'
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        pages_info = resp.json()
        print(f"✅ GitHub Pages已启用!")
        print(f"   🌐 访问地址: {pages_info.get('html_url', 'https://shpeibing.github.io/lab-daily-log/')}")
        print(f"   📂 发布源: {pages_info.get('source', {}).get('branch', 'main')}/{pages_info.get('source', {}).get('path', '/')}")
    elif resp.status_code == 404:
        print("⚠️ GitHub Pages未启用，正在启用...")
        # 启用GitHub Pages（从main分支根目录）
        url = f'https://api.github.com/repos/{repo}/pages'
        data = {
            'source': {
                'branch': 'main',
                'path': '/'
            }
        }
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            print("✅ GitHub Pages启用成功！")
            print(f"   🌐 访问地址: https://shpeibing.github.io/lab-daily-log/")
        else:
            print(f"⚠️ 启用失败: {resp.status_code}")
            print(resp.text[:200])
    else:
        print(f"⚠️ 检查Pages失败: {resp.status_code}")
        print(resp.text[:200])
# 启动本地服务器
print("\n📌 确保本地服务器运行...")
try:
    resp = requests.get('http://localhost:8082/index.html', timeout=3)
    if resp.status_code == 200:
        print("✅ 本地服务器已运行")
except:
    server_process = subprocess.Popen(
        ['python', '-m', 'http.server', '8082'],
        cwd=git_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"✅ 已启动本地服务器 (PID: {server_process.pid})")
print("\n" + "=" * 60)
print("🌐 访问方式汇总")
print("=" * 60)
print("📱 本机访问: http://localhost:8082")
print("📱 手机访问: 同一WiFi下输入 http://<本机IP>:8082")
print("🌍 GitHub Pages: https://shpeibing.github.io/lab-daily-log/")
print("=" * 60)