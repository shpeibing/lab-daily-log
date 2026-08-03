import os, subprocess, shutil
# 复制更新后的APP到deploy_git
src = r'D:\AiPy文件\3\shared\检验科工作日志APP.html'
dst = r'D:\AiPy文件\3\deploy_git\index.html'
shutil.copy2(src, dst)
print(f"✅ 已复制: {src} → {dst}")
# 部署
repo = r'D:\AiPy文件\3\deploy_git'
os.chdir(repo)
cmds = [
    'git add -A',
    'git commit -m "升级系统管理员：增加系统设置、账号管理、权限配置功能"',
    'git push origin main'
]
for cmd in cmds:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    print(f"$ {cmd}")
    if r.stdout.strip(): print(r.stdout.strip())
    if r.stderr.strip(): print(r.stderr.strip())
    if r.returncode != 0:
        print(f"⚠️ 命令失败")
print("\n✅ 部署完成！")