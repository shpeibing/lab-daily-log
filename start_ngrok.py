import os, subprocess, requests, time, json
work_dir = r"D:\AiPy文件\3"
print("=" * 60)
print("🚀 启动ngrok内网穿透")
print("=" * 60)
# 1. 确保本地服务器运行
git_dir = os.path.join(work_dir, 'deploy_git')
print("\n📌 检查本地服务器...")
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
    time.sleep(2)
# 2. 查找ngrok
print("\n📌 查找ngrok...")
ngrok_paths = [
    'ngrok',
    os.path.expanduser('~\\AppData\\Local\\ngrok\\ngrok.exe'),
    'C:\\Program Files\\ngrok\\ngrok.exe',
    'C:\\Users\\Administrator\\AppData\\Local\\ngrok\\ngrok.exe'
]
ngrok_path = None
for p in ngrok_paths:
    result = subprocess.run(['where', p], capture_output=True, text=True, timeout=10) if p == 'ngrok' else subprocess.run(['if', 'exist', p, 'echo', 'found'], shell=True, capture_output=True, text=True, timeout=10)
    if result.returncode == 0 or os.path.exists(p):
        ngrok_path = p if os.path.exists(p) else 'ngrok'
        break
if ngrok_path:
    print(f"✅ 找到ngrok: {ngrok_path}")
else:
    # 尝试直接查找
    result = subprocess.run(['where', 'ngrok'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        ngrok_path = 'ngrok'
        print(f"✅ 找到ngrok")
    else:
        print("❌ 未找到ngrok")
        # 尝试安装
        print("\n📌 尝试安装ngrok...")
        try:
            # 下载ngrok
            url = 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip'
            print(f"   下载中: {url}")
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                zip_path = os.path.join(work_dir, 'ngrok.zip')
                with open(zip_path, 'wb') as f:
                    f.write(resp.content)
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extract('ngrok.exe', work_dir)
                ngrok_path = os.path.join(work_dir, 'ngrok.exe')
                os.remove(zip_path)
                print(f"✅ ngrok已安装: {ngrok_path}")
            else:
                print(f"⚠️ 下载失败: {resp.status_code}")
        except Exception as e:
            print(f"⚠️ 安装失败: {e}")
# 3. 启动ngrok
if ngrok_path:
    print(f"\n📌 启动ngrok (端口8082)...")
    # 先停止旧ngrok
    try:
        result = subprocess.run(['taskkill', '/F', '/IM', 'ngrok.exe'], capture_output=True, timeout=5)
    except:
        pass
    time.sleep(1)
    # 启动ngrok
    ngrok_process = subprocess.Popen(
        [ngrok_path, 'http', '8082', '--log=stdout'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=work_dir
    )
    print(f"✅ ngrok已启动 (PID: {ngrok_process.pid})")
    time.sleep(5)
    # 获取ngrok地址
    print("\n📌 获取ngrok公网地址...")
    for i in range(3):
        try:
            resp = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
            if resp.status_code == 200:
                tunnels = resp.json().get('tunnels', [])
                for tunnel in tunnels:
                    if tunnel.get('public_url'):
                        print(f"   🌐 公网访问: {tunnel['public_url']}")
                        # 保存到文件
                        with open(os.path.join(work_dir, 'ngrok_url.txt'), 'w') as f:
                            f.write(tunnel['public_url'])
                break
        except:
            print(f"   ⏳ 等待ngrok启动... ({i+1}/3)")
            time.sleep(3)
# 4. 输出所有访问方式
print("\n" + "=" * 60)
print("🌐 访问方式汇总")
print("=" * 60)
print("📱 本机访问:")
print(f"   http://localhost:8082")
print(f"   http://127.0.0.1:8082")
print(f"\n📱 手机访问（同一WiFi）:")
print(f"   http://192.168.31.124:8082")
print(f"\n🌍 GitHub Pages:")
print(f"   https://shpeibing.github.io/lab-daily-log/")
print(f"\n📦 jsDelivr CDN:")
print(f"   https://cdn.jsdelivr.net/gh/shpeibing/lab-daily-log@main/index.html")
print(f"\n📁 部署包:")
print(f"   {os.path.join(work_dir, 'lab_app_v2.4.zip')}")
print("=" * 60)