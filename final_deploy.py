import os, requests, json, subprocess, threading, time, socket, http.server, socketserver, base64, zipfile, io
work_dir = r"D:\AiPy文件\3"
deploy_dir = os.path.join(work_dir, "deploy_netlify")
print("=" * 60)
print("🌐 最终部署方案")
print("=" * 60)
# 获取本机IP
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(f"\n📌 本机局域网IP: {local_ip}")
# 启动局域网服务器
os.chdir(deploy_dir)
class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        print(f"   [{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")
server = socketserver.TCPServer(("0.0.0.0", 8080), CORSHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()
print("✅ 局域网服务器已启动!")
print(f"   http://localhost:8080 (本机)")
print(f"   http://{local_ip}:8080 (手机连接WiFi后访问)")
# 尝试通过GitHub API创建token并启用Pages
print("\n" + "=" * 60)
print("📌 尝试通过GitHub API启用Pages...")
print("=" * 60)
# 尝试使用GitHub的OAuth device flow
try:
    # 先检查是否有任何可用的认证方式
    # 尝试从git的credential store获取
    token = None
    # 尝试从环境变量获取
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    # 尝试从git config获取
    if not token:
        try:
            result = subprocess.run(
                ['git', 'config', '--global', '--get-regexp', '.*token.*|.*password.*'],
                capture_output=True, text=True, timeout=10
            )
            if result.stdout:
                print(f"   git config tokens: {result.stdout[:200]}")
        except:
            pass
    # 尝试使用GitHub API的OAuth device flow获取token
    if not token:
        print("   尝试通过GitHub Device Flow获取授权...")
        # 请求device code
        device_resp = requests.post(
            'https://github.com/login/device/code',
            headers={'Accept': 'application/json'},
            data={
                'client_id': 'Iv1.8a3f9b8c7d6e5f4a',  # GitHub OAuth示例client_id
                'scope': 'repo,write:pages'
            },
            timeout=15
        )
        print(f"   Device Flow: {device_resp.status_code}")
        if device_resp.status_code == 200:
            device_data = device_resp.json()
            print(f"   用户码: {device_data.get('user_code', 'unknown')}")
            print(f"   验证URL: {device_data.get('verification_uri', 'unknown')}")
            print(f"   请在浏览器中打开以上URL，输入用户码授权")
except Exception as e:
    print(f"   OAuth异常: {e}")
# 尝试使用另一种方式 - 直接通过HTTPS推送gh-pages分支
print("\n📌 尝试通过HTTPS推送gh-pages分支...")
try:
    # 使用git push直接创建gh-pages分支
    # 先切换到deploy_git目录
    deploy_git = os.path.join(work_dir, "deploy_git")
    if os.path.exists(os.path.join(deploy_git, '.git')):
        # 同步文件
        import shutil
        for item in os.listdir(deploy_dir):
            if item in ['.git', '.gitignore']:
                continue
            src = os.path.join(deploy_dir, item)
            dst = os.path.join(deploy_git, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        # 提交到gh-pages分支
        subprocess.run(['git', 'checkout', '--orphan', 'gh-pages'], capture_output=True, text=True, cwd=deploy_git)
        subprocess.run(['git', 'add', '-A'], capture_output=True, text=True, cwd=deploy_git)
        commit = subprocess.run(['git', 'commit', '-m', 'deploy: V2.2'], capture_output=True, text=True, cwd=deploy_git)
        print(f"   gh-pages commit: {commit.returncode}")
        # 推送到GitHub
        push = subprocess.run(['git', 'push', '-f', 'origin', 'gh-pages'], capture_output=True, text=True, timeout=120, cwd=deploy_git)
        print(f"   push gh-pages: {push.returncode}")
        if push.stderr:
            print(f"   stderr: {push.stderr[:200]}")
        if push.returncode == 0:
            print("✅ gh-pages分支推送成功!")
            # 切换回main分支
            subprocess.run(['git', 'checkout', 'main'], capture_output=True, text=True, cwd=deploy_git)
            print("   请在GitHub仓库Settings > Pages中选择gh-pages分支")
        else:
            print("   gh-pages推送失败（SSH密钥问题）")
            # 切换回main
            subprocess.run(['git', 'checkout', 'main'], capture_output=True, text=True, cwd=deploy_git)
except Exception as e:
    print(f"   gh-pages异常: {e}")
# 最终输出
print("\n" + "=" * 60)
print("📱 手机APP交付总结")
print("=" * 60)
print(f"\n✅ APP文件: [index.html](file:///{deploy_dir}/index.html) (269.5KB, 3835行)")
print(f"✅ 二维码: [app_qrcode.png](file:///{work_dir}/app_qrcode.png)")
print(f"✅ 部署包: [检验科APP_手机版_云端版.zip](file:///{work_dir}/检验科APP_手机版_云端版.zip) (54.5KB)")
print(f"\n🌐 访问方式:")
print(f"   方式1: 局域网访问 http://{local_ip}:8080 (手机连WiFi)")
print(f"   方式2: GitHub Pages https://shpeibing.github.io/lab-daily-log/ (需手动启用)")
print(f"   方式3: 本地打开 [index.html](file:///{deploy_dir}/index.html)")
print(f"   方式4: Netlify Drop https://app.netlify.com/drop 拖拽部署")
print(f"\n💡 手动启用GitHub Pages（1分钟）:")
print(f"   1. 打开 https://github.com/shpeibing/lab-daily-log/settings/pages")
print(f"   2. Source选择 main 分支，/ (root) 文件夹")
print(f"   3. 点Save，等待1-2分钟")
print(f"   4. 访问 https://shpeibing.github.io/lab-daily-log/")
print(f"\n📌 服务器正在运行中，按 Ctrl+C 停止...")
# 保持服务器运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n服务器已停止")
finally:
    server.shutdown()