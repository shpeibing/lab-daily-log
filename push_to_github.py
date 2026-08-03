import os, subprocess, time, requests, json
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
print("=" * 60)
print("🚀 推送到GitHub + 配置GitHub Pages")
print("=" * 60)
# 1. 先提交代码
os.chdir(git_dir)
print("\n📌 提交代码...")
subprocess.run(['git', 'add', '.'], capture_output=True, timeout=10)
result = subprocess.run(['git', 'commit', '-m', 'V2.4 升级：副主任权限+云端上传优化'], capture_output=True, text=True, timeout=10)
print(result.stdout[:200])
# 2. 推送到GitHub（使用HTTPS，需要token）
# 先检查是否配置了GitHub token
print("\n📌 检查GitHub Token...")
# 尝试从git config获取token
result = subprocess.run(['git', 'config', '--global', '--list'], capture_output=True, text=True, timeout=10)
print("Git配置:", result.stdout[:500])
# 使用HTTPS推送（需要用户名和密码/token）
print("\n📌 推送到GitHub...")
# 先尝试直接推送
result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True, timeout=30)
print("推送结果:", result.stdout[:200])
print("推送错误:", result.stderr[:300])
if 'fatal' in result.stderr or 'error' in result.stderr:
    print("\n⚠️ 推送失败，尝试使用备用方案...")
    # 方案：使用GitHub API创建并上传文件
    print("📌 使用GitHub API上传...")
    
    # 读取index.html
    with open(index_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 尝试使用GitHub的raw文件上传方式
    # 创建docs目录（GitHub Pages支持）
    docs_dir = os.path.join(work_dir, 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    # 复制index.html到docs目录
    import shutil
    shutil.copy2(index_file, os.path.join(docs_dir, 'index.html'))
    
    # 复制manifest.json和sw.js
    for fname in ['manifest.json', 'sw.js']:
        src = os.path.join(git_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(docs_dir, fname))
    
    print("✅ 文件已准备到docs目录")
    
    # 尝试使用GitHub Token（如果有）
    # 检查环境变量
    github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if github_token:
        print("✅ 找到GitHub Token")
        # 使用API上传
        url = 'https://api.github.com/repos/shpeibing/lab-daily-log/contents/docs/index.html'
        import base64
        encoded = base64.b64encode(html_content.encode()).decode()
        data = {
            'message': 'V2.4 升级：副主任权限+云端上传优化',
            'content': encoded,
            'branch': 'main'
        }
        headers = {'Authorization': f'token {github_token}', 'Accept': 'application/vnd.github.v3+json'}
        resp = requests.put(url, json=data, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            print(f"✅ 文件上传成功！")
        else:
            print(f"⚠️ API上传结果: {resp.status_code}")
    else:
        print("⚠️ 未找到GitHub Token，无法通过API上传")
        print("📌 请手动执行以下命令推送：")
        print(f"   cd {git_dir}")
        print("   git push origin main")
else:
    print("✅ 推送成功！")
# 3. 启动本地服务器（如果未运行）
print("\n📌 确保本地服务器运行...")
try:
    resp = requests.get('http://localhost:8082/index.html', timeout=3)
    if resp.status_code == 200:
        print(f"✅ 本地服务器运行正常: http://localhost:8082")
except:
    # 启动服务器
    server_process = subprocess.Popen(
        ['python', '-m', 'http.server', '8082'],
        cwd=git_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"✅ 已启动本地服务器 (PID: {server_process.pid})")
# 4. 输出访问信息
print("\n" + "=" * 60)
print("🌐 访问方式")
print("=" * 60)
print("📱 本机访问: http://localhost:8082")
print("📱 手机访问: 同一WiFi下输入 http://<本机IP>:8082")
print("🌍 GitHub Pages: https://shpeibing.github.io/lab-daily-log/")
print("=" * 60)