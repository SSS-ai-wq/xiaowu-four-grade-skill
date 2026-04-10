#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四年级数学智能体友好接口 - 增强版
集成每次提问自动上传功能
专门为四年级数学设计
"""

import json
import os
import sys
from typing import Dict, Optional

# 导入四年级自动上传模块
from fourth_grade_auto_uploader import FourthGradeAutoUploader, upload_fourth_grade_question


class FourthGradeDataManagerEnhanced:
    """
    四年级数学数据管理器 - 增强版
    集成了每次提问自动上传功能
    """
    
    def __init__(self, server_url: str = "http://182.92.156.154"):
        """
        初始化四年级增强版数据管理器
        """
        # 初始化四年级自动上传器
        self.auto_uploader = FourthGradeAutoUploader(server_url)
        
        # 当前学生信息
        self.current_student = None
        
        # 四年级专用默认账号

        self.default_user = {
            "phone": "13800000000",
            "password": "test123",
            "user_id": 33,
            "grade": "四年级",
            "name": "四年级测试学生"
        }
        
        print("=" * 60)
        print("四年级数学数据管理器 - 增强版")
        print("已集成每次提问自动上传功能")
        print("=" * 60)
        print()
        print("四年级核心功能:")

        print("1. 每次用户提问自动上传到数据库")
        print("2. 智能识别四年级数学知识点")
        print("3. 支持离线缓存和自动同步")
        print("4. 开箱即用，无需复杂配置")
        print()
        print(f"服务器: {server_url}")
        print(f"默认账号: {self.default_user['phone']} (ID: {self.default_user['user_id']})")
        print(f"年级: {self.default_user['grade']}")
        print()
    
    def set_current_user(self, user_info: Dict):
        """
        设置当前四年级用户
        """
        self.current_student = user_info
        print(f"四年级当前用户已设置: {user_info.get('name', '未知用户')}")
    
    def process_fourth_grade_question(self, question: str) -> Dict:
        """
        处理四年级数学问题（智能体主要调用此方法）
        每次提问时自动上传到数据库
        """
        # 使用当前用户或默认用户
        user_info = self.current_student or self.default_user
        
        # 自动上传四年级问题
        result = self.auto_uploader.upload_fourth_grade_question(question, user_info)
        
        # 返回结果
        return {
            "success": result.get("success", False),
            "question": question,
            "user_id": user_info.get("user_id"),
            "grade": user_info.get("grade", "四年级"),
            "knowledge_point": self._extract_knowledge_from_result(result),
            "action": result.get("action", "unknown"),
            "message": result.get("message", ""),
            "details": result
        }
    
    def _extract_knowledge_from_result(self, result: Dict) -> str:
        """从结果中提取知识点"""
        return "四年级数学知识点"
    
    def register_fourth_grade_student(self, student_info: Dict) -> Dict:
        """
        注册四年级学生
        """
        # 设置当前用户
        user_info = {
            "phone": student_info.get("phone", self.default_user["phone"]),
            "password": student_info.get("password", self.default_user["password"]),
            "user_id": student_info.get("user_id", self.default_user["user_id"]),
            "grade": "四年级",  # 固定为四年级
            "name": student_info.get("name", "四年级学生")
        }
        
        self.set_current_user(user_info)
        
        return {
            "success": True,
            "user_id": user_info["user_id"],
            "grade": user_info["grade"],
            "message": "四年级学生注册成功",
            "note": "使用默认账号: 13800000000 / test123"
        }
    
    def get_fourth_grade_status(self) -> Dict:
        """
        获取四年级系统状态
        """
        status = self.auto_uploader.get_status()
        
        # 添加当前用户信息

        if self.current_student:
            status["current_student"] = {
                "name": self.current_student.get("name"),
                "user_id": self.current_student.get("user_id"),
                "grade": self.current_student.get("grade", "四年级")
            }
        else:
            status["current_student"] = "未设置（使用四年级默认账号）"
        
        return status
    
    def print_fourth_grade_status(self):
        """打印四年级系统状态"""
        status = self.get_fourth_grade_status()
        
        print("\n" + "=" * 50)
        print("四年级数学系统状态报告")
        print("=" * 50)
        
        # 服务器信息
        print(f"服务器: {status.get('server_url')}")
        print(f"健康状态: {status.get('server_health', '未知')}")
        
        # 用户信息
        if isinstance(status.get("current_student"), dict):
            student = status["current_student"]
            print(f"\n当前四年级用户: {student.get('name', '未知')}")
            print(f"用户ID: {student.get('user_id', '未知')}")
            print(f"年级: {student.get('grade', '四年级')}")
        else:
            print(f"\n当前四年级用户: {status.get('current_student')}")
            default = status.get("default_account", {})
            print(f"默认账号: {default.get('phone', '未知')} (ID: {default.get('user_id', '未知')})")
            print(f"年级: {default.get('grade', '四年级')}")
        
        # 缓存状态
        cache_status = status.get("cache_status", {})
        pending = cache_status.get("pending_questions", 0)
        print(f"\n四年级缓存状态: {pending} 条待上传问题")
        
        print("=" * 50)


# 简化接口函数
def process_fourth_grade_question(question: str, user_info: Optional[Dict] = None) -> Dict:
    """处理四年级数学问题简化接口"""
    return upload_fourth_grade_question(question, user_info)


def get_fourth_grade_system_status() -> Dict:
    """获取四年级系统状态简化接口"""
    uploader = FourthGradeAutoUploader()
    return uploader.get_status()


# 快速测试
if __name__ == "__main__":
    print("=== 四年级数学自动上传器测试 ===")
    
    manager = FourthGradeDataManagerEnhanced()
    
    # 四年级典型问题
    test_questions = [
        "325 × 24 = ?",                          # 三位数乘两位数
        "什么是乘法分配律？",                     # 运算定律
        "一个平角等于几个直角？",                  # 角的度量
        "小数 3.45 中，3 在什么位？",             # 小数的意义
        "鸡兔同笼，头35个，脚94只，鸡兔各几只？"    # 鸡兔同笼

        "什么是平均数？"                           # 平均数概念
    ]
    
    for question in test_questions:
        print(f"\n测试问题: {question}")
        result = manager.process_fourth_grade_question(question)
        print(f"结果: {'成功' if result.get('success') else '失败'}")
        if result.get("success"):
            print(f"知识点: {result.get('knowledge_point', '未知')}")
        print(f"操作: {result.get('action', '未知')}")
    
    print("\n四年级自动上传功能测试完成！")