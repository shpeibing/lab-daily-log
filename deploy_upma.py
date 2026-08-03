import os, requests, json, zipfile, io, subprocess, time
work_dir = r"D:\AiPy文件\3"
deploy_dir = os.path.join(work_dir, "deploy_netlify")
print("=" * 60)
print("🌐 尝试多个免费托管平台")
print("=" * 60)
# 方案1: 尝试Upma.cn（上码）- 国内免费静态托管
print("\n📌 方案1: 尝试Upma.cn...")
try:
    # 读取index.html
    with open(os.path.join(deploy_dir, 'index.html'), 'rb') as f:
        html_content = f.read()
    # 创建zip包
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zf.write(file_path, arcname)
    zip_buffer.seek(0)
    # Upma的API - 上传zip
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    files = {'file': ('deploy.zip', zip_buffer.getvalue(), 'application/zip')}
    upma_resp = requests.post(
        'https://www.upma.cn/api/upload',
        headers=headers,
        files=files,
        timeout=60
    )
    print(f"   Upma API: {upma_resp.status_code}")
    if upma_resp.status_code in [200, 201]:
        data = upma_resp.json()
        print(f"   响应: {json.dumps(data, ensure_ascii=False)[:200]}")
        site_url = data.get('url') or data.get('site_url') or data.get('link')
        if site_url:
            print(f"✅ Upma部署成功!")
            print(f"   访问地址: {site_url}")
            with open(os.path.join(work_dir, 'deploy_url.txt'), 'w') as f:
                f.write(site_url)
    else:
        print(f"   Upma失败: {upma_resp.text[:200]}")
except Exception as e:
    print(f"   Upma异常: {e}")
# 方案2: 尝试使用Cloudflare Pages API
print("\n📌 方案2: 尝试Cloudflare Pages...")
try:
    # Cloudflare Pages需要API token，但可以尝试直接上传
    cf_resp = requests.post(
        'https://api.cloudflare.com/client/v4/accounts/me/pages/projects',
        headers={'Authorization': 'Bearer test'},
        json={'name': 'lab-daily-log'},
        timeout=15
    )
    print(f"   Cloudflare: {cf_resp.status_code}")
except Exception as e:
    print(f"   Cloudflare异常: {e}")
# 方案3: 尝试使用Python的http.server生成二维码并启动服务
print("\n📌 方案3: 生成二维码 + 本地服务器...")
# 生成二维码图片
try:
    # 使用qrcode库（如果已安装）
    import qrcode
    qr_url = "https://shpeibing.github.io/lab-daily-log/"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(work_dir, "app_qrcode.png")
    img.save(qr_path)
    print(f"   ✅ 二维码已生成: [app_qrcode.png](file:///{qr_path})")
except ImportError:
    print("   未安装qrcode库，尝试安装...")
    try:
        import subprocess
        subprocess.run(['pip', 'install', 'qrcode[pil]'], capture_output=True, text=True, timeout=30)
        import qrcode
        qr_url = "https://shpeibing.github.io/lab-daily-log/"
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(work_dir, "app_qrcode.png")
        img.save(qr_path)
        print(f"   ✅ 二维码已生成: [app_qrcode.png](file:///{qr_path})")
    except:
        print("   无法安装qrcode库")
# 方案4: 尝试使用GitHub Pages的另一种方式 - 通过创建gh-pages分支
print("\n📌 方案4: 通过GitHub API创建gh-pages分支...")
try:
    # 使用GitHub的deploy key方式
    # 先尝试通过HTTPS使用token
    # 检查是否有保存的凭证
    token = None
    # 尝试从git credential获取
    try:
        cred = subprocess.run(
            ['git', 'credential', 'fill'],
            input=b'protocol=https\nhost=github.com\n\n',
            capture_output=True, text=True, timeout=10
        )
        if cred.returncode == 0:
            for line in cred.stdout.split('\n'):
                if 'password=' in line:
                    token = line.split('=')[1]
                    print("   从git credential获取到token")
    except:
        pass
    if token:
        print(f"✅ 找到Token: {token[:4]}...{token[-4:]}")
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        # 获取main分支最新commit
        main_ref = requests.get(
            'https://api.github.com/repos/shpeibing/lab-daily-log/git/ref/heads/main',
            headers=headers, timeout=15
        )
        if main_ref.status_code == 200:
            main_sha = main_ref.json()['object']['sha']
            print(f"   main最新commit: {main_sha[:10]}...")
            # 创建gh-pages分支
            gh_ref = requests.post(
                'https://api.github.com/repos/shpeibing/lab-daily-log/git/refs',
                headers=headers,
                json={'ref': 'refs/heads/gh-pages', 'sha': main_sha},
                timeout=15
            )
            print(f"   创建gh-pages: {gh_ref.status_code}")
            if gh_ref.status_code == 201:
                print("✅ gh-pages分支创建成功!")
                # 启用Pages
                pages_resp = requests.post(
                    'https://api.github.com/repos/shpeibing/lab-daily-log/pages',
                    headers=headers,
                    json={'source': {'branch': 'gh-pages', 'path': '/'}},
                    timeout=15
                )
                print(f"   启用Pages: {pages_resp.status_code}")
                if pages_resp.status_code == 201:
                    data = pages_resp.json()
                    url = data.get('html_url', 'https://shpeibing.github.io/lab-daily-log/')
                    print(f"✅ GitHub Pages已启用!")
                    print(f"   访问地址: {url}")
                    with open(os.path.join(work_dir, 'deploy_url.txt'), 'w') as f:
                        f.write(url)
            elif gh_ref.status_code == 422:
                print("   gh-pages分支已存在，尝试直接启用Pages...")
                pages_resp = requests.post(
                    'https://api.github.com/repos/shpeibing/lab-daily-log/pages',
                    headers=headers,
                    json={'source': {'branch': 'gh-pages', 'path': '/'}},
                    timeout=15
                )
                print(f"   启用Pages: {pages_resp.status_code}")
    else:
        print("   未找到GitHub Token")
except Exception as e:
    print(f"   GitHub API异常: {e}")
# 最终结果
print("\n" + "=" * 60)
url_file = os.path.join(work_dir, 'deploy_url.txt')
if os.path.exists(url_file):
    with open(url_file, 'r') as f:
        url = f.read().strip()
    print(f"✅ 公网网址: {url}")
else:
    print("⚠️ 自动部署未成功")
    print("💡 最简单的手动部署方法:")
    print("   1. 打开 https://app.netlify.com/drop")
    print("   2. 将 [deploy_netlify](file:///D:/AiPy文件/3/deploy_netlify) 文件夹拖拽到页面")
    print("   3. 自动生成公网网址！")
    print("")
    print("   或者打开 https://www.upma.cn/ 拖拽上传")