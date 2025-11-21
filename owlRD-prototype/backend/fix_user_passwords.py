#!/usr/bin/env python3
"""
紧急修复：为所有用户设置默认密码
"""

import json
import bcrypt
from pathlib import Path

def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def main():
    # 读取users.json
    users_file = Path("app/data/users.json")
    
    if not users_file.exists():
        print("❌ users.json 不存在！请先运行 init_sample_data.py")
        return
    
    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    print("=" * 60)
    print("🔧 修复用户密码")
    print("=" * 60)
    print()
    
    # 为所有password_hash为null的用户设置默认密码
    default_password = "demo123"
    fixed_count = 0
    
    for user in users:
        if user.get("password_hash") is None or user.get("password_hash") == "":
            user["password_hash"] = hash_password(default_password)
            print(f"✅ 设置用户 '{user['username']}' 的密码为: {default_password}")
            fixed_count += 1
        else:
            print(f"⏭️  用户 '{user['username']}' 已有密码，跳过")
    
    # 保存
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 60)
    print(f"🎉 修复完成！共修复 {fixed_count} 个用户")
    print("=" * 60)
    print()
    print("📋 可用账号：")
    print("-" * 60)
    for user in users:
        if user.get("password_hash"):
            password_hint = "demo123" if fixed_count > 0 and user['username'] != 'hhtbing' else "(注册时设置的密码)"
            print(f"  用户名: {user['username']:15} | 密码: {password_hint:20} | 角色: {user.get('role', 'N/A')}")
    print("-" * 60)
    print()

if __name__ == "__main__":
    main()
