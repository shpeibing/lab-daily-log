app_path = r'D:\AiPy文件\3\shared\检验科工作日志APP.html'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()
# 验证所有新功能
checks = {
    '系统管理员角色': '系统管理员',
    '系统设置入口': 'showSystemSettings()',
    '账号管理入口': 'showUserManagement()',
    '权限配置入口': 'showPermConfig()',
    '系统设置弹窗': 'systemSettingsModal',
    '权限配置弹窗': 'permConfigModal',
    '权限列表': 'rolePermList',
    '系统设置JS': 'function showSystemSettings',
    '权限配置JS': 'function showPermConfig',
    '保存系统设置': 'function saveSystemSettings',
    '保存权限配置': 'function saveRolePerms',
    '加载角色权限': 'function loadRolePerms',
    '新权限-系统设置': "{ id: '系统设置', label: '系统设置' }",
    '新权限-账号管理': "{ id: '账号管理', label: '账号管理' }",
    '新权限-权限配置': "{ id: '权限配置', label: '权限配置' }",
}
print("=== 功能验证 ===")
all_ok = True
for name, keyword in checks.items():
    found = keyword in content
    if not found: all_ok = False
    print(f"  {'✅' if found else '❌'} {name}")
print(f"\n{'🎉 全部功能验证通过！' if all_ok else '⚠️ 有功能缺失，需要修复'}")
# 检查admin用户权限
idx = content.find("id: 'admin'")
if idx >= 0:
    print(f"\n=== admin用户定义 ===\n{content[idx:idx+250]}")