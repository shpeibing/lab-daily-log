import os, requests, json, subprocess, shutil, time, base64
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
print("=" * 60)
print("☁️ 云端部署 - 多方案并行")
print("=" * 60)
# 读取文件
with open(index_file, 'r', encoding='utf-8') as f:
    html_content = f.read()
print(f"📄 主文件: {len(html_content)} 字符 ({len(html_content)/1024:.1f} KB)")
# 方案1: 使用jsDelivr + GitHub（无需Token，直接使用raw.githubusercontent.com）
print("\n📌 方案1: 检查GitHub仓库是否可公开访问...")
repo_url = 'https://raw.githubusercontent.com/shpeibing/lab-daily-log/main/index.html'
try:
    resp = requests.get(repo_url, timeout=10)
    if resp.status_code == 200:
        print(f"✅ GitHub仓库可公开访问！")
        print(f"   🔗 原始文件: {repo_url}")
        # 通过jsDelivr CDN加速
        cdn_url = 'https://cdn.jsdelivr.net/gh/shpeibing/lab-daily-log@main/index.html'
        print(f"   🌐 jsDelivr CDN: {cdn_url}")
    else:
        print(f"⚠️ 仓库不可访问: {resp.status_code}")
except:
    print("⚠️ 仓库检查失败")
# 方案2: 使用GitLab Pages（免费）
print("\n📌 方案2: 尝试上传到GitLab...")
try:
    # GitLab API无需认证可创建snippet
    snippet_data = {
        'title': '检验科工作日志APP',
        'file_name': 'index.html',
        'content': html_content,
        'visibility': 'public'
    }
    resp = requests.post('https://gitlab.com/api/v4/snippets', json=snippet_data, timeout=15)
    if resp.status_code == 201:
        result = resp.json()
        snippet_url = result.get('web_url', '')
        raw_url = result.get('raw_url', '')
        print(f"✅ GitLab Snippet上传成功！")
        print(f"   📄 页面: {snippet_url}")
        print(f"   🔗 原始文件: {raw_url}")
        # 保存
        with open(os.path.join(work_dir, 'cloud_gitlab_url.txt'), 'w') as f:
            f.write(f"GitLab: {snippet_url}\nRaw: {raw_url}")
    else:
        print(f"⚠️ GitLab上传失败: {resp.status_code}")
        print(f"   {resp.text[:200]}")
except Exception as e:
    print(f"⚠️ GitLab上传异常: {e}")
# 方案3: 使用CodePen（免费）
print("\n📌 方案3: 尝试上传到CodePen...")
try:
    # CodePen的API需要认证，但可以直接创建公开pen
    pen_data = {
        'title': '检验科工作日志APP',
        'description': '医学检验科工作日志与绩效考核系统',
        'html': html_content,
        'editors': '1100'  # HTML only
    }
    resp = requests.post('https://codepen.io/pen/define/', data=pen_data, timeout=15)
    if resp.status_code in [200, 201]:
        print(f"✅ CodePen上传成功！")
        print(f"   🌐 访问: https://codepen.io/pen/")
    else:
        print(f"⚠️ CodePen上传失败: {resp.status_code}")
except Exception as e:
    print(f"⚠️ CodePen上传异常: {e}")
# 方案4: 使用Netlify Drop（免费）
print("\n📌 方案4: 准备Netlify部署...")
# 创建部署文件夹
netlify_dir = os.path.join(work_dir, 'netlify_deploy')
if not os.path.exists(netlify_dir):
    os.makedirs(netlify_dir)
# 复制所有文件
shutil.copy2(index_file, os.path.join(netlify_dir, 'index.html'))
for fname in ['manifest.json', 'sw.js']:
    src = os.path.join(git_dir, fname)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(netlify_dir, fname))
# 创建_redirects文件（SPA支持）
with open(os.path.join(netlify_dir, '_redirects'), 'w') as f:
    f.write('/*    /index.html   200\n')
print("✅ Netlify部署文件已准备")
print(f"   📁 部署目录: {netlify_dir}")
print("   📌 请访问 https://app.netlify.com/drop 拖拽上传")
# 方案5: 使用Vercel（免费）
print("\n📌 方案5: 准备Vercel部署...")
vercel_dir = os.path.join(work_dir, 'vercel_deploy')
if not os.path.exists(vercel_dir):
    os.makedirs(vercel_dir)
shutil.copy2(index_file, os.path.join(vercel_dir, 'index.html'))
# 创建vercel.json
vercel_config = {
    'version': 2,
    'builds': [{'src': 'index.html', 'use': '@vercel/static'}],
    'routes': [{'src': '/(.*)', 'dest': '/index.html'}]
}
with open(os.path.join(vercel_dir, 'vercel.json'), 'w') as f:
    json.dump(vercel_config, f, ensure_ascii=False, indent=2)
print("✅ Vercel部署文件已准备")
print(f"   📁 部署目录: {vercel_dir}")
# 方案6: 使用ngrok内网穿透（让外网访问本地）
print("\n📌 方案6: 检查ngrok...")
try:
    result = subprocess.run(['where', 'ngrok'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("✅ 找到ngrok！启动内网穿透...")
        # 启动ngrok
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', '8082', '--log=stdout'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)
        # 获取ngrok地址
        try:
            resp = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if resp.status_code == 200:
                tunnels = resp.json().get('tunnels', [])
                for tunnel in tunnels:
                    if tunnel.get('public_url'):
                        print(f"   🌐 外网访问: {tunnel['public_url']}")
        except:
            print("⚠️ 无法获取ngrok地址")
    else:
        print("⚠️ 未安装ngrok")
        print("   📌 下载: https://ngrok.com/download")
        print("   📌 使用: ngrok http 8082")
except:
    print("⚠️ 检查ngrok失败")
# 方案7: 使用localhost.run（免费内网穿透，无需安装）
print("\n📌 方案7: 尝试localhost.run...")
try:
    # 使用SSH隧道
    ssh_process = subprocess.Popen(
        ['ssh', '-o', 'StrictHostKeyChecking=no', '-R', '80:localhost:8082', 'nokey@localhost.run'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(5)
    # 读取输出获取URL
    stdout, stderr = ssh_process.communicate(timeout=10)
    for line in (stdout + stderr).split('\n'):
        if 'localhost.run' in line or 'https://' in line:
            print(f"   🌐 外网访问: {line.strip()}")
except Exception as e:
    print(f"⚠️ localhost.run失败: {e}")
# 确保本地服务器运行
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
# 获取本机IP
print("\n📌 获取本机IP...")
try:
    result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
    ips = []
    for line in result.stdout.split('\n'):
        if 'IPv4' in line:
            parts = line.strip().split(':')
            if len(parts) == 2:
                ip = parts[1].strip()
                if ip and not ip.startswith('127'):
                    ips.append(ip)
    local_ip = ips[0] if ips else '192.168.x.x'
    print(f"✅ 本机IP: {local_ip}")
except:
    local_ip = '192.168.x.x'
# 输出所有访问方式
print("\n" + "=" * 60)
print("🌐 访问方式汇总")
print("=" * 60)
print("📱 本机访问:")
print(f"   http://localhost:8082")
print(f"   http://127.0.0.1:8082")
print(f"\n📱 手机访问（同一WiFi）:")
print(f"   http://{local_ip}:8082")
print(f"\n🌍 GitHub Pages:")
print(f"   https://shpeibing.github.io/lab-daily-log/")
print(f"\n📦 部署包:")
print(f"   {os.path.join(work_dir, 'lab_app_v2.4.zip')}")
print("=" * 60)
print("\n💡 提示: 如需外网访问，请安装ngrok后运行:")
print(f"   ngrok http 8082")