import os, subprocess, requests
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
os.chdir(git_dir)
print("=" * 60)
print("🔍 验证推送状态")
print("=" * 60)
# 1. 检查Git日志
print("\n📌 1. Git日志...")
result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
print(f"  最近5次提交:\n{result.stdout}")
# 2. 检查远程分支
print("\n📌 2. 远程分支状态...")
result = subprocess.run(['git', 'branch', '-a'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
print(f"  分支:\n{result.stdout}")
# 3. 检查是否已推送到远程
print("\n📌 3. 检查远程提交...")
result = subprocess.run(['git', 'rev-list', '--count', 'origin/main..main'], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
ahead = result.stdout.strip()
print(f"  本地领先远程: {ahead} 个提交")
if ahead == '0':
    print("  ✅ 已成功推送到GitHub!")
else:
    print(f"  ⚠️ 还有 {ahead} 个提交未推送")
# 4. 尝试通过API验证
print("\n📌 4. GitHub API验证...")
try:
    resp = requests.get('https://api.github.com/repos/shpeibing/lab-daily-log/contents/index.html', timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f"  ✅ GitHub仓库文件存在!")
        print(f"  大小: {data.get('size', 0)} bytes")
        print(f"  SHA: {data.get('sha', '')[:10]}...")
        # 解码内容检查是否包含新功能
        import base64
        content = base64.b64decode(data.get('content', '')).decode('utf-8')
        if 'showMonthlyReport' in content:
            print("  ✅ 最新版本已推送到GitHub!")
        else:
            print("  ⚠️ GitHub上的版本不是最新")
    else:
        print(f"  ⚠️ API请求失败: {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ API验证失败: {e}")
# 5. 创建部署包
print("\n📌 5. 创建部署包...")
import zipfile
zip_path = os.path.join(work_dir, 'lab_app_v2.5.zip')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in os.listdir(git_dir):
        if f.endswith('.html') or f.endswith('.js') or f.endswith('.json') or f.endswith('.css') or f.endswith('.md') or f.endswith('.toml') or f.endswith('.yml') or f.startswith('_') or f.startswith('.'):
            continue
        fpath = os.path.join(git_dir, f)
        if os.path.isfile(fpath):
            zf.write(fpath, f)
    # 添加关键文件
    for f in ['index.html', 'manifest.json', 'sw.js', '404.html', 'README.md', 'vercel.json', 'netlify.toml', '_headers', '.nojekyll']:
        fpath = os.path.join(git_dir, f)
        if os.path.exists(fpath):
            zf.write(fpath, f)
zip_size = os.path.getsize(zip_path)
print(f"  ✅ 部署包已创建: {zip_path}")
print(f"  大小: {zip_size} bytes ({zip_size/1024:.1f} KB)")
# 6. 输出最终信息
print("\n" + "=" * 60)
print("✅ V2.5 最终交付")
print("=" * 60)
print(f"📄 主文件: index.html ({len(open(os.path.join(git_dir, 'index.html'), 'r', encoding='utf-8').read())} 字符, {open(os.path.join(git_dir, 'index.html'), 'r', encoding='utf-8').read().count(chr(10))} 行)")
print(f"\n📱 访问方式:")
print(f"   [本地访问](http://localhost:8082)")
print(f"   [手机访问](http://192.168.31.124:8082)")
print(f"   [GitHub Pages](https://shpeibing.github.io/lab-daily-log/)")
print(f"\n📦 部署包: [lab_app_v2.5.zip](file://{zip_path}) ({zip_size/1024:.1f}KB)")
print("\n🏆 V2.5 新增功能:")
print("   1. 📊 工作台月报表 - 当月统计+明细+员工排名")
print("   2. 📈 月度分析 - 每周趋势图+积分构成+员工分析")
print("   3. 👥 员工积分汇总 - 所有在职员工积分明细及汇总")
print("   4. 📥 月报表下载 - CSV格式，可下载保存")
print("   5. ☁️ 云端同步增强 - 所有保存操作自动同步云端")
print("   6. 🔐 权限控制 - 管理员/科主任可查看统计汇总")
print("=" * 60)