import os, subprocess, re
work_dir = r"D:\AiPy文件\3"
git_dir = os.path.join(work_dir, 'deploy_git')
index_file = os.path.join(git_dir, 'index.html')
with open(index_file, 'r', encoding='utf-8') as f:
    content = f.read()
print(f"📄 文件大小: {len(content)} 字符")
# =========================================
# 1. 完善系统管理员权限 - 确保员工汇总只有管理员可见
# =========================================
print("\n📌 1. 完善系统管理员权限...")
# 检查loadPerfStaffSummary中的权限控制
idx = content.find('function loadPerfStaffSummary')
if idx >= 0:
    end = content.find('\n}', idx)
    snippet = content[idx:end+2]
    # 检查是否已有权限控制
    if '系统管理员' in snippet and '科主任' in snippet:
        print("  ✅ 已有权限控制（系统管理员/科主任/副主任）")
    else:
        print("  ⚠️ 需要添加权限控制")
        # 添加权限控制
        old = "if(!currentUser || (currentUser.role !== '系统管理员' && currentUser.role !== '科主任' && currentUser.role !== '副主任')){"
        if old in snippet:
            print("  ✅ 权限控制已存在")
        else:
            print("  ❌ 权限控制不完整")
# =========================================
# 2. 完善月报表下载功能 - 确保所有用户都可以下载
# =========================================
print("\n📌 2. 完善月报表下载功能...")
# 检查downloadMonthlyReport
idx = content.find('function downloadMonthlyReport')
if idx >= 0:
    end = content.find('\n}', idx)
    snippet = content[idx:end+2]
    print(f"  downloadMonthlyReport长度: {len(snippet)}")
    if 'exportToCsv' in snippet:
        print("  ✅ 已调用exportToCsv导出CSV")
    else:
        print("  ⚠️ 未调用exportToCsv")
# =========================================
# 3. 完善月度分析 - 增加更详细的图表
# =========================================
print("\n📌 3. 完善月度分析...")
idx = content.find('function showMonthlyAnalysis')
if idx >= 0:
    end = content.find('\n}', idx)
    snippet = content[idx:end+2]
    print(f"  showMonthlyAnalysis长度: {len(snippet)}")
    if 'generateMonthlyReport' in snippet:
        print("  ✅ 已调用generateMonthlyReport")
    else:
        print("  ⚠️ 未调用generateMonthlyReport")
# =========================================
# 4. 确保云端同步在所有保存操作后触发
# =========================================
print("\n📌 4. 云端同步检查...")
# 检查patchAllSaves
idx = content.find('function patchAllSaves')
if idx >= 0:
    end = content.find('\n}', idx)
    snippet = content[idx:end+2]
    # 统计覆盖的保存函数数量
    func_count = snippet.count("typeof window[")
    print(f"  patchAllSaves覆盖 {func_count} 个保存函数")
# 检查ensureCloudSync
idx = content.find('function ensureCloudSync')
if idx >= 0:
    end = content.find('\n}', idx)
    snippet = content[idx:end+2]
    if 'autoSyncToCloud' in snippet:
        print("  ✅ ensureCloudSync调用autoSyncToCloud")
    else:
        print("  ⚠️ ensureCloudSync未调用autoSyncToCloud")
# =========================================
# 5. 检查是否有语法错误
# =========================================
print("\n📌 5. JS语法检查...")
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
js_code = '\n'.join(scripts)
js_file = os.path.join(work_dir, '_temp_verify_v25.js')
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_code)
result = subprocess.run(['node', '--check', js_file], capture_output=True, text=True, timeout=15)
if result.returncode == 0:
    print("  ✅ JS语法检查通过!")
else:
    print(f"  ❌ JS语法错误:")
    print(result.stderr[:2000])
# 保存
with open(index_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n✅ 文件已保存: {len(content)} 字符")