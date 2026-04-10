#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四年级数学教程技能 - 系统验证脚本
验证统一数据上传系统的所有功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fourth_grade_smart_interface import FourthGradeDataManager


def test_all_functions():
    """测试四年级所有功能"""
    print("🎯 四年级数学教学系统 - 完整功能验证")
    print("=" * 60)
    
    # 1. 创建四年级数据管理器
    print("\n1. 创建四年级数据管理器...")
    manager = FourthGradeDataManager()
    print("   ✅ 管理器创建成功")
    
    # 2. 注册四年级学生
    print("\n2. 注册四年级学生...")
    student_result = manager.register_student({
        "name": "四年级验证学生",
        "phone": "13800138003",
        "password": "grade4_verify",
        "hobbies": "数学,科学,编程,围棋"
    })
    
    print(f"   结果: {student_result.get('message', '未知')}")
    print(f"   用户ID: {student_result.get('user_id', '未知')}")
    print(f"   操作: {student_result.get('action', '未知')}")
    
    # 3. 记录四年级错题
    print("\n3. 记录四年级错题...")
    if student_result.get("success"):
        question_result = manager.record_wrong_question({
            "question": "小明的储蓄罐里有12枚5角硬币，20枚1元硬币。他一共有多少钱？",
            "student_answer": "20元",
            "correct_answer": "26元",
            "error_type": "计算错误",
            "knowledge_point": "小数乘法应用",
            "difficulty": "中等",
            "chapter": "小数",
            "section": "小数乘法"
        })
        print(f"   结果: {question_result.get('message', '未知')}")
        print(f"   操作: {question_result.get('action', '未知')}")
    
    # 4. 记录四年级知识点
    print("\n4. 记录四年级知识点掌握情况...")
    knowledge_result = manager.record_knowledge_point({
        "knowledge_point": "小数的意义与性质",
        "mastery_level": "熟练",
        "study_times": 10,
        "correct_rate": 88.5,
        "notes": "小数点的意义理解较好，但在混合运算中容易出错"
    })
    print(f"   结果: {knowledge_result.get('message', '未知')}")
    print(f"   掌握级别: {knowledge_result.get('data', {}).get('mastery_level', '未知')}")
    
    # 5. 记录四年级学习进度
    print("\n5. 记录四年级学习进度...")
    progress_result = manager.record_learning_progress({
        "topic": "小数的意义与性质",
        "duration": 60,
        "questions_total": 25,
        "questions_correct": 22,
        "week": 3,
        "strengths": "小数读写准确率高",
        "weaknesses": "小数与整数混合运算需要加强",
        "recommendations": "多做混合运算练习"
    })
    
    if progress_result.get("success"):
        total = 25
        correct = 22
        accuracy = (correct / max(total, 1)) * 100
        print(f"   结果: ✅ 记录成功!")
        print(f"   正确率: {accuracy:.1f}%")
    else:
        print(f"   结果: ❌ 记录失败")
    
    # 6. 同步数据
    print("\n6. 同步所有四年级数据...")
    sync_result = manager.sync_all_data()
    
    if sync_result.get("success"):
        details = sync_result.get("results", {})
        print(f"   结果: ✅ 同步完成!")
        print(f"   成功: {details.get('successful', 0)}条")
        print(f"   失败: {details.get('failed', 0)}条")
        print(f"   总计: {details.get('total', 0)}条")
    else:
        print(f"   结果: ❌ 同步失败: {sync_result.get('error', '未知错误')}")
    
    # 7. 查看系统状态
    print("\n7. 查看四年级系统状态...")
    status = manager.get_status()
    if status["server_health"].get("question_bank_api"):
        print(f"   服务器: ✅ 正常")
    else:
        print(f"   服务器: ❌ 异常")
    
    stats = status["upload_stats"]
    print(f"   总上传: {stats.get('total_uploads', 0)}次")
    print(f"   成功率: {stats.get('success_rate', 0):.1f}%")
    print(f"   待上传: {stats.get('total_pending', 0)}条数据")
    print(f"   已注册学生: {stats.get('registered_students', 0)}人")
    
    # 8. 打印完整状态报告
    print("\n8. 四年级系统详细状态报告:")
    print("-" * 50)
    manager.print_status()
    
    print("\n" + "=" * 60)
    print("🎉 四年级数学教学系统验证完成！")
    print(f"📊 结果总结:")
    print(f"   学生注册: {'✅ 成功' if student_result.get('success') else '❌ 失败'}")
    print(f"   错题记录: {'✅ 成功' if question_result.get('success') else '❌ 失败'}")
    print(f"   知识点记录: {'✅ 成功' if knowledge_result.get('success') else '❌ 失败'}")
    print(f"   进度记录: {'✅ 成功' if progress_result.get('success') else '❌ 失败'}")
    print(f"   数据同步: {'✅ 成功' if sync_result.get('success') else '❌ 失败'}")
    
    # 返回验证结果
    return {
        "student_registration": student_result.get("success", False),
        "wrong_question": question_result.get("success", False),
        "knowledge_point": knowledge_result.get("success", False),
        "learning_progress": progress_result.get("success", False),
        "data_sync": sync_result.get("success", False)
    }


def quick_test():
    """快速测试（仅验证基本功能）"""
    print("⚡ 四年级系统快速测试")
    print("=" * 40)
    
    try:
        # 导入检查
        from fourth_grade_unified_uploader import FourthGradeUnifiedUploader
        from fourth_grade_smart_interface import FourthGradeDataManager
        
        print("✅ 模块导入成功")
        
        # 创建管理器
        manager = FourthGradeDataManager()
        print("✅ 管理器创建成功")
        
        # 检查服务器
        health = manager.get_status()["server_health"]
        if health.get("question_bank_api"):
            print("✅ 服务器连接正常")
        else:
            print("⚠️  服务器连接异常")
            print(f"   错题库API: {'✅' if health.get('question_bank_api') else '❌'}")
            print(f"   小悟API: {'✅' if health.get('xiaowu_api') else '❌'}")
        
        # 打印状态
        manager.print_status()
        
        print("\n" + "=" * 40)
        print("🎯 四年级系统快速测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    # 根据参数选择测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        test_all_functions()