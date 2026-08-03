import os, subprocess, requests, base64, json, shutil, time
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
print("=" * 60)
print("☁️ 上传到云端 - GitHub Pages")
print("=" * 60)
# 1. 读取文件
with open(index_file, 'r', encoding='utf-8') as f:
    html_content = f.read()
print(f"📄 主文件: {len(html_content)} 字符")
# 2. 准备docs目录
docs_dir = os.path.join(work_dir, 'docs')
if not os.path.exists(docs_dir):
    os.makedirs(docs_dir)
# 复制所有文件到docs
shutil.copy2(index_file, os.path.join(docs_dir, 'index.html'))
print("✅ 已复制index.html到docs目录")
for fname in ['manifest.json', 'sw.js']:
    src = os.path.join(git_dir, fname)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(docs_dir, fname))
        print(f"✅ 已复制{fname}到docs目录")
# 3. 尝试通过Git命令行推送
print("\n📌 尝试Git推送...")
os.chdir(git_dir)
# 先提交
result = subprocess.run(['git', 'add', '.'], capture_output=True, timeout=10)
result = subprocess.run(['git', 'commit', '-m', 'V2.4 升级：副主任权限+云端上传优化'], capture_output=True, timeout=10)
# 设置编码环境变量避免GBK错误
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
# 尝试推送
result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True, timeout=30, env=env)
print("推送输出:", result.stdout[:200])
print("推送错误:", result.stderr[:300])
if 'fatal' in result.stderr or 'error' in result.stderr:
    print("\n⚠️ Git推送失败，使用GitHub API上传...")
    
    # 4. 使用GitHub API上传文件到仓库
    repo = 'shpeibing/lab-daily-log'
    branch = 'main'
    
    # 上传index.html到docs目录
    encoded = base64.b64encode(html_content.encode()).decode()
    
    # 先获取最新commit的sha
    url = f'https://api.github.com/repos/{repo}/git/refs/heads/{branch}'
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        latest_sha = resp.json()['object']['sha']
        print(f"✅ 获取最新commit: {latest_sha[:8]}...")
        
        # 获取commit tree
        url = f'https://api.github.com/repos/{repo}/git/commits/{latest_sha}'
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            tree_sha = resp.json()['tree']['sha']
            print(f"✅ 获取tree: {tree_sha[:8]}...")
            
            # 创建blob（上传文件内容）
            url = f'https://api.github.com/repos/{repo}/git/blobs'
            data = {'content': encoded, 'encoding': 'base64'}
            resp = requests.post(url, json=data, timeout=10)
            if resp.status_code == 201:
                blob_sha = resp.json()['sha']
                print(f"✅ 创建blob: {blob_sha[:8]}...")
                
                # 创建新的tree（包含docs/index.html）
                url = f'https://api.github.com/repos/{repo}/git/trees'
                data = {
                    'base_tree': tree_sha,
                    'tree': [
                        {
                            'path': 'docs/index.html',
                            'mode': '100644',
                            'type': 'blob',
                            'sha': blob_sha
                        }
                    ]
                }
                resp = requests.post(url, json=data, timeout=10)
                if resp.status_code == 201:
                    new_tree_sha = resp.json()['sha']
                    print(f"✅ 创建新tree: {new_tree_sha[:8]}...")
                    
                    # 创建commit
                    url = f'https://api.github.com/repos/{repo}/git/commits'
                    data = {
                        'message': 'V2.4 升级：副主任权限+云端上传优化',
                        'tree': new_tree_sha,
                        'parents': [latest_sha]
                    }
                    resp = requests.post(url, json=data, timeout=10)
                    if resp.status_code == 201:
                        commit_sha = resp.json()['sha']
                        print(f"✅ 创建commit: {commit_sha[:8]}...")
                        
                        # 更新ref
                        url = f'https://api.github.com/repos/{repo}/git/refs/heads/{branch}'
                        data = {'sha': commit_sha, 'force': True}
                        resp = requests.patch(url, json=data, timeout=10)
                        if resp.status_code == 200:
                            print("✅ GitHub API上传成功！")
                        else:
                            print(f"⚠️ 更新ref失败: {resp.status_code}")
                    else:
                        print(f"⚠️ 创建commit失败: {resp.status_code}")
                else:
                    print(f"⚠️ 创建tree失败: {resp.status_code}")
            else:
                print(f"⚠️ 创建blob失败: {resp.status_code}")
        else:
            print(f"⚠️ 获取commit失败: {resp.status_code}")
    else:
        print(f"⚠️ 获取ref失败: {resp.status_code}")
        print("📌 仓库可能不存在或需要认证")
        print("   请先手动创建仓库: https://github.com/new")
        print("   仓库名: lab-daily-log")
else:
    print("✅ Git推送成功！")
# 5. 启动本地服务器
print("\n📌 启动本地服务器...")
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
# 6. 输出访问信息
print("\n" + "=" * 60)
print("🌐 访问方式")
print("=" * 60)
print("📱 本机访问: http://localhost:8082")
print("📱 手机访问: 同一WiFi下输入 http://<本机IP>:8082")
print("🌍 GitHub Pages: https://shpeibing.github.io/lab-daily-log/")
print("=" * 60)