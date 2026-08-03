import os, subprocess, time, threading, socket, requests, json
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
PORT = 8083
print("=" * 60)
print("🌐 尝试获取公网访问网址")
print("=" * 60)
# 方法1: 使用Python的pyngrok
print("\n📌 方法1: 安装并使用pyngrok...")
try:
    import subprocess
    result = subprocess.run(['uv', 'pip', 'install', 'pyngrok'], capture_output=True, text=True, timeout=60)
    print(f"  ✅ pyngrok安装成功")
    from pyngrok import ngrok
    # 启动ngrok隧道
    public_url = ngrok.connect(PORT, "http")
    print(f"  ✅ ngrok隧道建立成功！")
    print(f"  🌐 {public_url}")
except Exception as e:
    print(f"  ⚠️ pyngrok失败: {e}")
# 方法2: 使用serveo.net的自动模式
print("\n📌 方法2: 使用serveo.net自动模式...")
try:
    # 使用subprocess启动SSH隧道，并捕获输出
    import subprocess
    # 先检查ssh是否可用
    result = subprocess.run(['ssh', '-V'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"  ✅ SSH可用")
        # 启动SSH隧道，使用-o选项自动响应
        ssh_cmd = [
            'ssh', '-o', 'StrictHostKeyChecking=accept-new',
            '-o', 'ServerAliveInterval=60',
            '-R', f'80:localhost:{PORT}',
            'serveo.net'
        ]
        print(f"  🔄 正在连接serveo.net...")
        # 使用Popen并设置超时
        proc = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # 等待最多15秒获取URL
        start_time = time.time()
        url_found = None
        while time.time() - start_time < 15:
            line = proc.stdout.readline()
            if line:
                print(f"  {line.strip()}")
                if 'serveo.net' in line:
                    # 提取URL
                    import re
                    urls = re.findall(r'https?://[^\s]+', line)
                    for u in urls:
                        if 'serveo.net' in u:
                            url_found = u
                            break
                if url_found:
                    break
            time.sleep(0.1)
        if url_found:
            print(f"  ✅ 公网访问地址获取成功！")
            print(f"  🌐 {url_found}")
        else:
            print(f"  ⚠️ 未获取到URL，请手动检查")
        # 不终止进程，保持隧道
    else:
        print(f"  ❌ SSH不可用")
except Exception as e:
    print(f"  ⚠️ serveo失败: {e}")
# 方法3: 使用browserless.io
print("\n📌 方法3: 尝试使用localhost.run (不需要注册)...")
try:
    proc = subprocess.Popen(
        ['ssh', '-o', 'StrictHostKeyChecking=accept-new', '-R', f'80:localhost:{PORT}', 'nokey@localhost.run'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    start_time = time.time()
    url_found = None
    while time.time() - start_time < 15:
        line = proc.stdout.readline()
        if line:
            print(f"  {line.strip()}")
            if 'https://' in line:
                import re
                urls = re.findall(r'https://[^\s]+', line)
                for u in urls:
                    url_found = u
                    break
            if url_found:
                break
        time.sleep(0.1)
    if url_found:
        print(f"  ✅ localhost.run成功！")
        print(f"  🌐 {url_found}")
    else:
        print(f"  ⚠️ localhost.run未获取到URL")
except Exception as e:
    print(f"  ⚠️ localhost.run失败: {e}")
# 汇总
print("\n" + "=" * 60)
print("📋 最终访问方式")
print("=" * 60)
print(f"""
📱 当前可用的访问方式:
  1. 本机: http://localhost:{PORT}
  2. 局域网: http://192.168.31.124:{PORT}
  
📥 部署包（推荐部署到Netlify）:
  📁 [部署包](file:///D:/AiPy文件/3/netlify_deploy.zip)
  🌐 打开 https://app.netlify.com/drop 拖拽部署
  
🌐 GitHub Pages（需手动启用）:
  🌐 https://shpeibing.github.io/lab-daily-log
  ⚠️ 需在GitHub仓库Settings → Pages中启用
""")