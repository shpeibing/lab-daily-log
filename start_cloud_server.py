import os, subprocess, time, threading, socket, json, requests
import http.server
import socketserver
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
PORT = 8082
print("=" * 60)
print("☁️ 启动云端服务器")
print("=" * 60)
# 1. 检查端口
try:
    test_sock = socketserver.TCPServer(("", PORT), None)
    test_sock.server_close()
    port_free = True
except OSError:
    port_free = False
if not port_free:
    print(f"  ⚠️ 端口 {PORT} 已被占用，尝试其他端口...")
    for p in range(8083, 8100):
        try:
            test_sock = socketserver.TCPServer(("", p), None)
            test_sock.server_close()
            PORT = p
            port_free = True
            break
        except:
            continue
if port_free:
    # 2. 启动HTTP服务器（后台线程）
    os.chdir(git_dir)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("0.0.0.0", PORT), handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(1)
    # 3. 获取本机IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"  ✅ 服务器已启动!")
    print(f"  📍 本机: http://localhost:{PORT}")
    print(f"  📍 局域网: http://{local_ip}:{PORT}")
    # 4. 尝试内网穿透 - 使用localtunnel
    print("\n📌 尝试内网穿透（让外网也能访问）...")
    # 方法1: 使用Python的localtunnel库
    try:
        import urllib.request
        # 使用localtunnel.me的API
        tunnel_url = f"https://localtunnel.me/api/tunnels"
        resp = requests.post(tunnel_url, json={"port": PORT}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            public_url = data.get('url', '')
            if public_url:
                print(f"  ✅ 内网穿透成功！")
                print(f"  🌐 公网访问: {public_url}")
                print(f"  ⚠️ 注意：首次访问需要输入隧道密码")
        else:
            print(f"  ⚠️ localtunnel API: {resp.status_code}")
    except Exception as e:
        print(f"  ⚠️ localtunnel失败: {e}")
    # 方法2: 使用serveo.net (SSH隧道)
    print("\n📌 尝试serveo.net SSH隧道...")
    try:
        # 检查是否有ssh
        result = subprocess.run(['where', 'ssh'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  🔄 正在建立SSH隧道到 serveo.net...")
            # 启动SSH隧道（后台进程）
            ssh_process = subprocess.Popen(
                ['ssh', '-o', 'StrictHostKeyChecking=no', '-R', f'80:localhost:{PORT}', 'serveo.net'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            time.sleep(5)
            # 读取输出获取URL
            stdout_data = ""
            try:
                stdout_data, _ = ssh_process.communicate(timeout=3)
            except:
                pass
            for line in (stdout_data + '\n').split('\n'):
                if 'https://' in line and 'serveo.net' in line:
                    print(f"  ✅ SSH隧道成功！")
                    print(f"  🌐 {line.strip()}")
                elif 'http://' in line and 'serveo.net' in line:
                    print(f"  ✅ SSH隧道成功！")
                    print(f"  🌐 {line.strip()}")
            if not any('serveo.net' in l for l in (stdout_data + '\n').split('\n')):
                print(f"  ⚠️ SSH隧道可能已建立，但URL未捕获")
                print(f"  📝 请查看终端输出获取URL")
        else:
            print(f"  ❌ SSH不可用")
    except Exception as e:
        print(f"  ⚠️ SSH隧道失败: {e}")
    # 方法3: 使用ngrok
    print("\n📌 尝试ngrok...")
    try:
        result = subprocess.run(['where', 'ngrok'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  🔄 正在启动ngrok...")
            ngrok_process = subprocess.Popen(
                ['ngrok', 'http', str(PORT), '--log=stdout'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            time.sleep(3)
            # 查询ngrok API获取URL
            try:
                resp = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    for tunnel in data.get('tunnels', []):
                        public_url = tunnel.get('public_url', '')
                        if public_url:
                            print(f"  ✅ ngrok成功！")
                            print(f"  🌐 {public_url}")
            except:
                print(f"  ⚠️ ngrok API查询失败")
        else:
            print(f"  ❌ ngrok未安装")
    except Exception as e:
        print(f"  ⚠️ ngrok失败: {e}")
    # 5. 验证服务器是否正常运行
    print("\n📌 验证服务器状态:")
    try:
        resp = requests.get(f'http://127.0.0.1:{PORT}/', timeout=5)
        if resp.status_code == 200:
            file_size = len(resp.text)
            print(f"  ✅ 服务器响应正常 (200 OK, {file_size} 字符)")
            if 'loginPage' in resp.text:
                print(f"  ✅ 登录页面正常加载")
            if 'uploadToCloud' in resp.text:
                print(f"  ✅ 云端上传功能已部署")
        else:
            print(f"  ❌ 服务器返回: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  ❌ 服务器异常: {e}")
    print("\n" + "=" * 60)
    print("📋 访问方式汇总")
    print("=" * 60)
    print(f"""
📱 访问方式:
  1. 本机访问: http://localhost:{PORT}
  2. 局域网访问: http://{local_ip}:{PORT}
  3. 手机访问（同一WiFi）: http://{local_ip}:{PORT}
  
⚠️ 注意: 服务器正在运行中，关闭此窗口后服务将停止
""")
else:
    print(f"  ❌ 无法找到可用端口")