#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
四年级数学教学系统API处理脚本
用于与云端数据库交互，保存用户信息和错题记录
支持分层架构和苏格拉底式教学
（针对四年级数学特点：大数、小数、运算定律、几何图形）
"""

import json
import requests
import time
from datetime import datetime
import os

class APIHandler:
    def __init__(self):
        # API配置（与一、二、三年级相同）
        self.mistakes_api = "http://182.92.156.154:5000"
        self.teaching_api = "http://182.92.156.154:5001"
        
        # 本地缓存目录
        self.cache_dir = os.path.join(os.path.dirname(__file__), "..", "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # 本地数据文件
        self.users_file = os.path.join(self.cache_dir, "users.json")
        self.mistakes_file = os.path.join(self.cache_dir, "mistakes.json")
        self.cached_file = os.path.join(self.cache_dir, "cached_data.json")
        
        # 初始化本地数据存储
        self._init_local_data()
    
    def _init_local_data(self):
        """初始化本地数据文件"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": []}, f, ensure_ascii=False, indent=2)
        
        if not os.path.exists(self.mistakes_file):
            with open(self.mistakes_file, 'w', encoding='utf-8') as f:
                json.dump({"mistakes": []}, f, ensure_ascii=False, indent=2)
        
        if not os.path.exists(self.cached_file):
            with open(self.cached_file, 'w', encoding='utf-8') as f:
                json.dump({"pending_users": [], "pending_mistakes": []}, f, ensure_ascii=False, indent=2)
    
    def check_api_status(self):
        """检查API服务状态"""
        try:
            # 检查错题库API
            response1 = requests.get(f"{self.mistakes_api}/api/health", timeout=5)
            mistakes_status = response1.status_code == 200
            
            # 检查教学API
            response2 = requests.get(f"{self.teaching_api}/api/xiaowu/health", timeout=5)
            teaching_status = response2.status_code == 200
            
            return {
                "mistakes_api": mistakes_status,
                "teaching_api": teaching_status,
                "all_ok": mistakes_status and teaching_status
            }
        except requests.exceptions.RequestException as e:
            print(f"API连接检查失败: {e}")
            return {
                "mistakes_api": False,
                "teaching_api": False,
                "all_ok": False
            }
    
    def register_user(self, user_data):
        """注册新用户（四年级专用）"""
        # 确保手机号是11位
        phone = user_data.get("phone", "")
        if len(phone) != 11 or not phone.isdigit():
            return {
                "success": False,
                "message": "手机号必须是11位数字",
                "user_id": None,
                "synced": False
            }
        
        user_info = {
            "username": user_data.get("username", ""),
            "grade": user_data.get("grade", "四年级"),
            "phone": phone,
            "password": user_data.get("password", ""),
            "hobbies": user_data.get("hobbies", ""),
            "register_time": datetime.now().isoformat()
        }
        
        # 保存到本地文件
        self._save_user_locally(user_info)
        
        # 尝试同步到云端
        sync_result = self._sync_user_to_cloud(user_info)
        
        if sync_result["success"]:
            return {
                "success": True,
                "message": "用户注册成功",
                "user_id": sync_result.get("user_id", "local"),
                "synced": True
            }
        else:
            # 缓存到待同步队列
            self._cache_for_sync("user", user_info)
            return {
                "success": True,
                "message": "用户注册成功（已缓存，稍后同步）",
                "user_id": "pending",
                "synced": False
            }
    
    def record_mistake(self, phone, password, question_data):
        """记录错题（四年级专用）"""
        mistake_record = {
            "phone": phone,
            "password": password,
            "question_text": question_data.get("question_text", ""),
            "subject": "数学",
            "wrong_answer": question_data.get("wrong_answer", ""),
            "correct_answer": question_data.get("correct_answer", ""),
            "error_type": question_data.get("error_type", ""),
            "hint_level": question_data.get("hint_level", "L1"),
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到本地文件
        self._save_mistake_locally(mistake_record)
        
        # 尝试同步到云端
        sync_result = self._sync_mistake_to_cloud(mistake_record)
        
        if sync_result["success"]:
            return {
                "success": True,
                "message": "错题记录成功",
                "record_id": sync_result.get("record_id", "local"),
                "synced": True
            }
        else:
            # 缓存到待同步队列
            self._cache_for_sync("mistake", mistake_record)
            return {
                "success": True,
                "message": "错题记录成功（已缓存，稍后同步）",
                "record_id": "pending",
                "synced": False
            }
    
    def get_wrong_questions(self, phone, password, subject="数学"):
        """获取错题记录"""
        try:
            response = requests.get(
                f"{self.mistakes_api}/api/wrong-questions",
                params={
                    "phone": phone,
                    "password": password,
                    "subject": subject
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json().get("data", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_questions(self, phone, password, subject="数学", limit=3):
        """生成练习题（四年级专用）"""
        try:
            response = requests.get(
                f"{self.mistakes_api}/api/generate-questions",
                params={
                    "phone": phone,
                    "password": password,
                    "subject": subject,
                    "limit": limit
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json().get("data", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_weekly_report(self, phone, password, year=None, week=None):
        """获取周报"""
        params = {
            "phone": phone,
            "password": password
        }
        
        if year:
            params["year"] = year
        if week:
            params["week"] = week
        
        try:
            response = requests.get(
                f"{self.mistakes_api}/api/weekly-report",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "report": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_pending_data(self):
        """同步所有待同步的数据"""
        try:
            with open(self.cached_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            synced_count = 0
            failed_count = 0
            
            # 同步用户数据
            for user in cached_data.get("pending_users", []):
                result = self._sync_user_to_cloud(user)
                if result["success"]:
                    synced_count += 1
                else:
                    failed_count += 1
            
            # 同步错题数据
            for mistake in cached_data.get("pending_mistakes", []):
                result = self._sync_mistake_to_cloud(mistake)
                if result["success"]:
                    synced_count += 1
                else:
                    failed_count += 1
            
            # 清空已同步的数据
            if synced_count > 0:
                self._clear_synced_data()
            
            return {
                "success": True,
                "synced_count": synced_count,
                "failed_count": failed_count
            }
        except Exception as e:
            print(f"同步数据失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_user_locally(self, user_info):
        """保存用户信息到本地"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否已存在
            existing_users = data.get("users", [])
            user_exists = any(u.get("phone") == user_info.get("phone") for u in existing_users)
            
            if not user_exists:
                existing_users.append(user_info)
                data["users"] = existing_users
                
                with open(self.users_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户信息到本地失败: {e}")
    
    def _save_mistake_locally(self, mistake_record):
        """保存错题记录到本地"""
        try:
            with open(self.mistakes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            mistakes = data.get("mistakes", [])
            mistakes.append(mistake_record)
            data["mistakes"] = mistakes
            
            with open(self.mistakes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存错题记录到本地失败: {e}")
    
    def _sync_user_to_cloud(self, user_info):
        """同步用户信息到云端"""
        try:
            # 使用正确的端点
            response = requests.post(
                f"{self.mistakes_api}/api/v1/users",
                json=user_info,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "user_id": result.get("user_id")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sync_mistake_to_cloud(self, mistake_record):
        """同步错题记录到云端"""
        try:
            response = requests.post(
                f"{self.mistakes_api}/api/wrong-questions",
                json=mistake_record,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "record_id": result.get("record_id", "unknown")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _cache_for_sync(self, data_type, data):
        """缓存数据到待同步队列"""
        try:
            with open(self.cached_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            if data_type == "user":
                cached_data["pending_users"].append(data)
            elif data_type == "mistake":
                cached_data["pending_mistakes"].append(data)
            
            with open(self.cached_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"缓存数据失败: {e}")
    
    def _clear_synced_data(self):
        """清空已同步的数据"""
        try:
            with open(self.cached_file, 'w', encoding='utf-8') as f:
                json.dump({"pending_users": [], "pending_mistakes": []}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"清空缓存数据失败: {e}")
    
    def get_local_user_by_phone(self, phone):
        """根据手机号获取本地用户信息"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for user in data.get("users", []):
                if user.get("phone") == phone:
                    return user
            return None
        except Exception as e:
            print(f"获取本地用户信息失败: {e}")
            return None

# 四年级专用测试函数
def test_grade4_api_handler():
    """测试四年级API处理功能"""
    handler = APIHandler()
    
    print("测试四年级数学苏格拉底教学技能...")
    print("="*60)
    
    # 检查API状态
    print("1. 检查API状态...")
    status = handler.check_api_status()
    print(f"   错题库API: {'正常' if status['mistakes_api'] else '异常'}")
    print(f"   教学API: {'正常' if status['teaching_api'] else '异常'}")
    
    # 测试用户注册（四年级）
    print("\n2. 测试用户注册（四年级）...")
    test_user = {
        "username": "四年级测试学生",
        "grade": "四年级",
        "phone": "13800138010",
        "password": "grade4test",
        "hobbies": "数学、编程、阅读"
    }
    
    result = handler.register_user(test_user)
    print(f"   注册结果: {result.get('message')}")
    print(f"   成功: {result.get('success')}")
    
    if result.get('success'):
        print(f"   用户ID: {result.get('user_id')}")
        
        # 测试错题记录（四年级典型题目）
        print("\n3. 测试错题记录（四年级典型题目）...")
        
        # 大数读写问题
        big_number_question = {
            "question_text": "五亿零三百万写作：______",
            "wrong_answer": "5003000",
            "correct_answer": "503000000",
            "error_type": "大数读写错误",
            "hint_level": "L2"
        }
        
        mistake_result1 = handler.record_mistake(
            test_user["phone"],
            test_user["password"],
            big_number_question
        )
        print(f"   大数问题记录: {mistake_result1.get('message')}")
        
        # 小数问题
        decimal_question = {
            "question_text": "把0.05扩大到原数的100倍是：______",
            "wrong_answer": "0.5",
            "correct_answer": "5",
            "error_type": "小数点移动错误",
            "hint_level": "L3"
        }
        
        mistake_result2 = handler.record_mistake(
            test_user["phone"],
            test_user["password"],
            decimal_question
        )
        print(f"   小数问题记录: {mistake_result2.get('message')}")
        
        # 运算定律问题
        operation_law_question = {
            "question_text": "用简便方法计算：25×32",
            "wrong_answer": "25×30+2",
            "correct_answer": "25×4×8=800",
            "error_type": "运算定律应用错误",
            "hint_level": "L3"
        }
        
        mistake_result3 = handler.record_mistake(
            test_user["phone"],
            test_user["password"],
            operation_law_question
        )
        print(f"   运算定律问题记录: {mistake_result3.get('message')}")
        
        # 测试同步功能
        print("\n4. 测试数据同步...")
        sync_result = handler.sync_pending_data()
        print(f"   同步结果: 成功{sync_result.get('synced_count', 0)}条，失败{sync_result.get('failed_count', 0)}条")
        
        # 测试生成题目
        print("\n5. 测试生成题目（四年级）...")
        generate_result = handler.generate_questions(test_user["phone"], test_user["password"], "数学", 2)
        print(f"   生成题目结果: {generate_result.get('success', False)}")
        if generate_result.get("success"):
            questions = generate_result.get("data", [])
            for i, q in enumerate(questions):
                print(f"   题目{i+1}: {q.get('question_text', '')[:50]}...")
    
    print("\n" + "="*60)
    print("四年级数学技能API测试完成！")

if __name__ == "__main__":
    test_grade4_api_handler()