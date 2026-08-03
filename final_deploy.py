import os, subprocess, requests, json, base64, time
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
os.chdir(git_dir)
print("=" * 60)
print("🌍 最终部署 V2.5")
print("=" * 60)
# 1. 读取文件
with open(index_file, 'r', encoding='utf-8') as f:
    content = f.read()
print(f"📄 文件大小: {len(content)} 字符")
print(f"📄 行数: {content.count(chr(10))}")
# 2. Git提交
print("\n📌 1. Git提交...")
result = subprocess.run(['git', 'add', '.'], capture_output=True, timeout=10)
result = subprocess.run(['git', 'commit', '-m', 'V2.5 final: monthly report + staff summary + cloud sync + permissions'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
if result.returncode == 0:
    print("  ✅ 提交成功")
else:
    print(f"  ℹ️ {result.stderr[:200]}")
# 3. 尝试多种方式推送
print("\n📌 2. 推送GitHub...")
pushed = False
# 方式1: HTTPS推送
print("  方法1: HTTPS推送...")
for i in range(3):
    result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, encoding='utf-8', errors='replace', timeout=30)
    if result.returncode == 0:
        print("  ✅ 推送成功!")
        pushed = True
        break
    else:
        err = result.stderr[:200] if result.stderr else 'Unknown'
        print(f"  ⚠️ 尝试{i+1}失败: {err}")
        time.sleep(2)
# 方式2: 使用GitHub API
if not pushed:
    print("\n  方法2: GitHub API上传...")
    try:
        # 获取最新commit的SHA
        api_url = 'https://api.github.com/repos/shpeibing/lab-daily-log/contents/index.html'
        resp = requests.get(api_url, timeout=10)
        if resp.status_code == 200:
            sha = resp.json().get('sha', '')
            print(f"  当前文件SHA: {sha[:10] if sha else '无'}")
            # 上传新文件
            encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            data = {
                'message': 'V2.5 final: monthly report + staff summary + cloud sync',
                'content': encoded,
                'sha': sha,
                'branch': 'main'
            }
            # 尝试使用token
            token = os.environ.get('GITHUB_TOKEN', '')
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if token:
                headers['Authorization'] = f'token {token}'
            resp = requests.put(api_url, json=data, headers=headers, timeout=15)
            if resp.status_code in [200, 201]:
                print(f"  ✅ API上传成功!")
                pushed = True
            else:
                print(f"  ⚠️ API上传失败: {resp.status_code} - {resp.text[:200]}")
        else:
            print(f"  ⚠️ 获取文件信息失败: {resp.status_code}")
    except Exception as e:
        print(f"  ⚠️ API上传异常: {e}")
# 4. 验证GitHub Pages
print("\n📌 3. 验证GitHub Pages...")
try:
    resp = requests.get('https://shpeibing.github.io/lab-daily-log/', timeout=10)
    print(f"  HTTP状态: {resp.status_code}")
    if resp.status_code == 200:
        print("  ✅ GitHub Pages访问正常!")
        has_new = 'showMonthlyReport' in resp.text
        if has_new:
            print("  ✅ 最新版本已部署!")
        else:
            print("  ⚠️ 页面不是最新版本（可能还在部署中）")
    else:
        print(f"  ⚠️ 状态码: {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ 访问失败: {e}")
# 5. 启动本地服务器
print("\n📌 4. 启动本地服务器...")
try:
    resp = requests.get('http://localhost:8082/index.html', timeout=3)
    if resp.status_code == 200:
        print("  ✅ 本地服务器已运行")
except:
    server = subprocess.Popen(['python', '-m', 'http.server', '8082'], cwd=git_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  ✅ 已启动本地服务器 (PID: {server.pid})")
# 6. 输出最终信息
print("\n" + "=" * 60)
print("✅ V2.5 部署完成!")
print("=" * 60)
print("📱 本机访问:")
print(f"   http://localhost:8082")
print(f"\n📱 手机访问（同一WiFi）:")
print(f"   http://192.168.31.124:8082")
print(f"\n🌍 GitHub Pages:")
print(f"   https://shpeibing.github.io/lab-daily-log/")
print(f"\n📦 部署包:")
print(f"   {os.path.join(work_dir, 'lab_app_v2.4.zip')}")
print("=" * 60)