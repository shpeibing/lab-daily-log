import os, requests, json, base64, subprocess, shutil, time
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
print("=" * 60)
print("☁️ 上传到JSONBin云端 + 启动本地服务")
print("=" * 60)
# 1. 读取文件
with open(index_file, 'r', encoding='utf-8') as f:
    html_content = f.read()
print(f"📄 主文件: {len(html_content)} 字符 ({len(html_content)/1024:.1f} KB)")
# 2. 上传到JSONBin（免费云存储）
print("\n📌 上传到JSONBin...")
# 先尝试创建新Bin
data = {
    'html': html_content
}
# 将整个index.html作为JSONBin存储
payload = json.dumps(data)
headers = {
    'Content-Type': 'application/json',
    'X-Bin-Name': '检验科工作日志APP',
    'X-Bin-Private': 'false'
}
try:
    resp = requests.post('https://api.jsonbin.io/v3/b', json=data, headers=headers, timeout=15)
    if resp.status_code in [200, 201]:
        result = resp.json()
        bin_id = result.get('metadata', {}).get('id', '')
        print(f"✅ JSONBin上传成功！")
        print(f"   Bin ID: {bin_id}")
        # 保存bin_id到本地文件
        with open(os.path.join(work_dir, 'cloud_bin_id.txt'), 'w') as f:
            f.write(bin_id)
        # 生成访问链接
        # JSONBin提供直接访问的API
        direct_url = f'https://api.jsonbin.io/v3/b/{bin_id}/latest'
        print(f"   📦 数据API: {direct_url}")
    else:
        print(f"⚠️ JSONBin上传失败: {resp.status_code}")
        print(f"   {resp.text[:200]}")
except Exception as e:
    print(f"⚠️ JSONBin上传异常: {e}")
# 3. 使用另一种方式 - 上传到免费托管平台
print("\n📌 尝试上传到GitHub Gist...")
# 使用GitHub Gist API（无需认证，可创建匿名Gist）
gist_data = {
    'description': '检验科工作日志APP - 在线版',
    'public': True,
    'files': {
        'index.html': {
            'content': html_content
        }
    }
}
try:
    resp = requests.post('https://api.github.com/gists', json=gist_data, timeout=15)
    if resp.status_code == 201:
        result = resp.json()
        gist_url = result.get('html_url', '')
        raw_url = result.get('files', {}).get('index.html', {}).get('raw_url', '')
        print(f"✅ GitHub Gist上传成功！")
        print(f"   📄 Gist页面: {gist_url}")
        print(f"   🔗 原始文件: {raw_url}")
        # 保存到文件
        with open(os.path.join(work_dir, 'cloud_gist_url.txt'), 'w') as f:
            f.write(f"Gist: {gist_url}\nRaw: {raw_url}")
    else:
        print(f"⚠️ Gist上传失败: {resp.status_code}")
        print(f"   {resp.text[:200]}")
except Exception as e:
    print(f"⚠️ Gist上传异常: {e}")
# 4. 使用第三方免费托管 - Tiiny.host
print("\n📌 尝试上传到Tiiny.host...")
try:
    # Tiiny.host API
    files = {'file': ('index.html', html_content, 'text/html')}
    resp = requests.post('https://tiiny.host/api/upload', files=files, timeout=30)
    if resp.status_code == 200:
        result = resp.json()
        url = result.get('url', '')
        print(f"✅ Tiiny.host上传成功！")
        print(f"   🌐 访问地址: {url}")
    else:
        print(f"⚠️ Tiiny.host上传失败: {resp.status_code}")
except Exception as e:
    print(f"⚠️ Tiiny.host上传异常: {e}")
# 5. 使用surge.sh（如果安装了surge）
print("\n📌 检查是否可部署到Surge...")
try:
    result = subprocess.run(['where', 'surge'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("✅ 找到Surge CLI")
        # 部署到surge
        result = subprocess.run(
            ['surge', '--project', git_dir, '--domain', 'lab-daily-log.surge.sh'],
            capture_output=True, text=True, timeout=60
        )
        print(result.stdout[:300])
        print(result.stderr[:300])
    else:
        print("⚠️ 未安装Surge CLI")
except:
    print("⚠️ 检查Surge失败")
# 6. 启动本地服务器（确保运行）
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
# 7. 获取本机IP
print("\n📌 获取本机IP...")
try:
    result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
    ips = []
    for line in result.stdout.split('\n'):
        if 'IPv4' in line or 'IP Address' in line:
            parts = line.strip().split(':')
            if len(parts) == 2:
                ip = parts[1].strip()
                if ip and ip != '0.0.0.0' and not ip.startswith('127'):
                    ips.append(ip)
    if ips:
        local_ip = ips[0]
        print(f"✅ 本机IP: {local_ip}")
    else:
        local_ip = '192.168.x.x'
        print("⚠️ 未找到IP，请手动查看")
except:
    local_ip = '192.168.x.x'
    print("⚠️ 获取IP失败")
# 8. 输出所有访问方式
print("\n" + "=" * 60)
print("🌐 访问方式汇总")
print("=" * 60)
print("📱 本机访问:")
print(f"   http://localhost:8082")
print(f"   http://127.0.0.1:8082")
print(f"\n📱 手机访问（同一WiFi）:")
print(f"   http://{local_ip}:8082")
print(f"\n🌍 云端访问:")
print(f"   https://shpeibing.github.io/lab-daily-log/")
print("=" * 60)