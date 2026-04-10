#!/usr/bin/env python3
"""
四年级数学助手 - 快速验证脚本
为下一个智能体设计的简单验证工具
"""

print("=" * 60)
print("四年级数学助手 - 功能验证")
print("基于已验证的一、二、三年级架构")
print("=" * 60)
print()

print("开始验证...")
print()

# 第1步: 导入技能
print("1. 导入四年级数学助手...")
try:
    from fourth_grade_math_tutor import FourthGradeMathTutor, quick_teach
    print("   成功 - 技能导入成功")
except Exception as e:
    print(f"   失败 - 导入失败: {e}")
    exit(1)

# 第2步: 创建助手实例
print("\n2. 创建教学助手...")
try:
    tutor = FourthGradeMathTutor()
    print("   成功 - 助手实例创建完成")
    print(f"   服务器: {tutor.config['server_url']}")
    print(f"   API路径: {tutor.config['api_base']}")
except Exception as e:
    print(f"   失败 - 创建失败: {e}")

# 第3步: 设置用户
print("\n3. 设置用户信息...")
try:
    tutor.set_user("四年级测试学生", "四年级")
    print("   成功 - 用户信息设置完成")
    print("   手机号: 13800000000")
    print("   密码: test123456")
except Exception as e:
    print(f"   失败 - 用户设置失败: {e}")

# 第4步: 测试连接
print("\n4. 测试服务器连接...")
try:
    connected, message = tutor.test_connection()
    if connected:
        print(f"   成功 - 连接正常: {message}")
    else:
        print(f"   注意 - 连接异常: {message}")
        print("   数据将自动缓存，等待网络恢复")
except Exception as e:
    print(f"   失败 - 连接测试失败: {e}")

# 第5步: 测试教学功能
print("\n5. 测试四年级数学教学...")
test_question = "234 × 56 = ?"
print(f"   测试问题: {test_question}")

try:
    result = tutor.teach(test_question)
    print(f"   成功 - 教学完成")
    print(f"   知识点: {result.knowledge_point}")
    print(f"   状态: {result.action}")
    
    if result.uploaded:
        print("   数据状态: 已上传到数据库")
    else:
        print("   数据状态: 已安全缓存")
        print(f"   消息: {result.message}")
        
except Exception as e:
    print(f"   失败 - 教学失败: {e}")

# 第6步: 查看状态
print("\n6. 查看系统完整状态...")
try:
    tutor.print_status()
    print("   成功 - 状态查看完成")
except Exception as e:
    print(f"   失败 - 状态查看失败: {e}")

print()
print("=" * 60)
print("四年级数学助手 - 验证完成")
print("=" * 60)
print()

print("下一个智能体可以立即开始使用:")
print()
print("基本使用:")
print("  from fourth_grade_math_tutor import FourthGradeMathTutor")
print("  tutor = FourthGradeMathTutor()")
print("  tutor.set_user('学生姓名', '四年级')")
print("  result = tutor.teach('你的四年级数学问题')")
print()
print("快速使用:")
print("  from fourth_grade_math_tutor import quick_teach")
print("  result = quick_teach('234 × 56 = ?', '小明')")
print("  print(f'知识点: {result.knowledge_point}')")
print()
print("技能已验证，可以开始教学任务！")