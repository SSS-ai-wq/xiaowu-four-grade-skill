#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
四年级数学教程技能 - 集成数据处理器
专为四年级优化的云服务器数据发送功能
当用户填写个人信息并提交错题后，自动向云服务器接口发送数据
保证数据一定能发送（本地缓存 + 重试机制）
"""

import json
import os
import sys
import time
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Optional
import socket

# 导入云服务器发送器
try:
    from cloud_data_sender import CloudDataSender, Config
except ImportError:
    print("[WARN] cloud_data_sender 未找到，云服务器功能将受限")

print("四年级数学教程数据处理器 v1.0")
print("=" * 50)

class FourthGradeDataHandler:
    def __init__(self):
        self.cache_dir = os.path.join(os.path.dirname(__file__), "..", "cache")
        self._ensure_dirs()
        
        # 四年级特定的数据文件
        self.local_users_file = os.path.join(self.cache_dir, "fourth_grade_users.json")
        self.local_mistakes_file = os.path.join(self.cache_dir, "fourth_grade_mistakes.json")
        self.sync_status_file = os.path.join(self.cache_dir, "sync_status.json")
        
        # 初始化本地数据
        self._init_local_data()
        
        # 初始化云服务器发送器
        try:
            self.cloud_sender = CloudDataSender()
            self.cloud_enabled = True
            print("[OK] 云服务器发送器已启用（四年级专用）")
        except:
            self.cloud_enabled = False
            print("[WARN] 云服务器发送器未启用，仅使用本地缓存")
            
    def _ensure_dirs(self):
        """确保目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _init_local_data(self):
        """初始化本地数据文件"""
        # 初始化用户文件
        if not os.path.exists(self.local_users_file):
            with open(self.local_users_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": "1.0",
                    "grade": "四年级",
                    "users": [],
                    "created_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
                
        # 初始化错题文件
        if not os.path.exists(self.local_mistakes_file):
            with open(self.local_mistakes_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": "1.0",
                    "grade": "四年级",
                    "mistakes": [],
                    "created_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
                
    def save_user_info(self, user_data: Dict) -> Dict:
        """
        保存四年级用户信息
        参数:
            user_data: 包含用户信息的字典
        返回:
            包含操作状态的字典
        """
        print(f"保存四年级用户信息: {user_data.get('username', '未知用户')}")
        
        # 验证必要字段
        required_fields = ["phone", "password"]
        for field in required_fields:
            if field not in user_data:
                return {
                    "success": False,
                    "message": f"缺少必要字段: {field}",
                    "data_type": "user",
                    "grade": "四年级"
                }
                
        # 验证手机号格式（四年级要求11位数字）
        phone = user_data["phone"]
        if len(phone) != 11 or not phone.isdigit():
            return {
                "success": False,
                "message": "手机号必须是11位数字",
                "data_type": "user",
                "grade": "四年级"
            }
                
        # 添加四年级特定的元数据
        user_data["grade"] = user_data.get("grade", "四年级")  # 确保年级正确
        user_data["saved_at"] = datetime.now().isoformat()
        user_data["sync_status"] = "pending"
        user_data["sync_attempts"] = 0
        user_data["last_sync_attempt"] = None
        user_data["skill_version"] = "fourth_grade_math"
        
        # 保存到本地文件
        try:
            with open(self.local_users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            users = data.get("users", [])
            
            # 检查是否已存在
            user_exists = False
            for i, user in enumerate(users):
                if user.get("phone") == phone:
                    users[i] = user_data  # 更新现有用户
                    user_exists = True
                    print(f"更新现有四年级用户: {phone}")
                    break
                    
            if not user_exists:
                users.append(user_data)
                print(f"添加新四年级用户: {phone}")
                
            # 保存数据
            data["users"] = users
            data["last_updated"] = datetime.now().isoformat()
            data["total_users"] = len(users)
            
            with open(self.local_users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"[OK] 四年级用户信息已保存到本地: {self.local_users_file}")
            
        except Exception as e:
            return {
                "success": False,
                "message": f"保存本地文件失败: {e}",
                "data_type": "user",
                "grade": "四年级"
            }
            
        # 尝试立即同步到云服务器
        sync_result = None
        if self.cloud_enabled:
            sync_result = self._sync_user_to_cloud(user_data)
            
        return {
            "success": True,
            "message": "四年级用户信息保存成功",
            "data_type": "user",
            "grade": "四年级",
            "local_saved": True,
            "cloud_synced": sync_result["success"] if sync_result else False,
            "cloud_message": sync_result["message"] if sync_result else "云服务器功能未启用",
            "user_id": f"fourth_grade_user_{phone}",
            "timestamp": user_data["saved_at"]
        }
        
    def save_mistake(self, user_phone: str, mistake_data: Dict) -> Dict:
        """
        保存四年级错题信息
        参数:
            user_phone: 用户手机号
            mistake_data: 错题信息
        返回:
            包含操作状态的字典
        """
        print(f"保存四年级错题信息: {mistake_data.get('question_text', '未知题目')[:50]}...")
        
        # 验证必要字段
        if not user_phone:
            return {
                "success": False,
                "message": "缺少用户手机号",
                "data_type": "mistake",
                "grade": "四年级"
            }
            
        required_fields = ["question_text"]
        for field in required_fields:
            if field not in mistake_data:
                return {
                    "success": False,
                    "message": f"缺少必要字段: {field}",
                    "data_type": "mistake",
                    "grade": "四年级"
                }
                
        # 添加四年级特定的元数据
        mistake_data["user_phone"] = user_phone
        mistake_data["grade"] = "四年级"  # 标记为四年级错题
        mistake_data["subject"] = mistake_data.get("subject", "数学")
        mistake_data["saved_at"] = datetime.now().isoformat()
        mistake_data["sync_status"] = "pending"
        mistake_data["sync_attempts"] = 0
        mistake_data["last_sync_attempt"] = None
        
        # 为错题生成唯一ID
        mistake_id = hashlib.md5(
            f"fourth_grade_{user_phone}_{mistake_data['question_text']}_{mistake_data['saved_at']}".encode()
        ).hexdigest()[:12]
        mistake_data["mistake_id"] = mistake_id
        
        # 保存到本地文件
        try:
            with open(self.local_mistakes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            mistakes = data.get("mistakes", [])
            mistakes.append(mistake_data)
            
            # 保存数据
            data["mistakes"] = mistakes
            data["last_updated"] = datetime.now().isoformat()
            data["total_mistakes"] = len(mistakes)
            
            with open(self.local_mistakes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"[OK] 四年级错题信息已保存到本地: {self.local_mistakes_file}")
            
        except Exception as e:
            return {
                "success": False,
                "message": f"保存本地文件失败: {e}",
                "data_type": "mistake",
                "grade": "四年级"
            }
            
        # 尝试立即同步到云服务器
        sync_result = None
        if self.cloud_enabled:
            sync_result = self._sync_mistake_to_cloud(user_phone, mistake_data)
            
        return {
            "success": True,
            "message": "四年级错题信息保存成功",
            "data_type": "mistake",
            "grade": "四年级",
            "local_saved": True,
            "cloud_synced": sync_result["success"] if sync_result else False,
            "cloud_message": sync_result["message"] if sync_result else "云服务器功能未启用",
            "mistake_id": mistake_id,
            "timestamp": mistake_data["saved_at"]
        }
        
    def _sync_user_to_cloud(self, user_data: Dict) -> Dict:
        """同步四年级用户到云服务器"""
        if not self.cloud_enabled:
            return {"success": False, "message": "云服务器功能未启用"}
            
        try:
            # 准备发送数据（适配四年级API）
            send_data = {
                "phone": user_data["phone"],
                "username": user_data.get("username", ""),
                "grade": user_data.get("grade", "四年级"),
                "password_hash": hashlib.sha256(user_data["password"].encode()).hexdigest(),
                "created_from": user_data.get("created_from", "fourth_grade_math_tutor"),
                "hobbies": user_data.get("hobbies", ""),
                "skill_type": "四年级数学"
            }
            
            # 使用云服务器发送器
            success = self.cloud_sender.register_user(send_data)
            
            if success:
                return {
                    "success": True,
                    "message": "四年级用户信息已成功同步到云服务器"
                }
            else:
                # 添加到待发送队列
                self.cloud_sender.add_pending_user(send_data)
                return {
                    "success": False,
                    "message": "四年级用户信息同步失败，已添加到待发送队列"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"同步四年级用户信息异常: {e}"
            }
            
    def _sync_mistake_to_cloud(self, user_phone: str, mistake_data: Dict) -> Dict:
        """同步四年级错题到云服务器"""
        if not self.cloud_enabled:
            return {"success": False, "message": "云服务器功能未启用"}
            
        try:
            # 准备发送数据（适配四年级错题格式）
            send_data = {
                "question_text": mistake_data["question_text"],
                "subject": mistake_data.get("subject", "数学"),
                "wrong_answer": mistake_data.get("wrong_answer", ""),
                "correct_answer": mistake_data.get("correct_answer", ""),
                "error_type": mistake_data.get("error_type", "计算错误"),
                "hint_level": mistake_data.get("hint_level", "L1"),
                "grade": "四年级",
                "skill_type": "四年级数学"
            }
            
            # 使用云服务器发送器
            success = self.cloud_sender.submit_mistake(user_phone, send_data)
            
            if success:
                return {
                    "success": True,
                    "message": "四年级错题信息已成功同步到云服务器"
                }
            else:
                # 添加到待发送队列
                self.cloud_sender.add_pending_mistake(user_phone, send_data)
                return {
                    "success": False,
                    "message": "四年级错题信息同步失败，已添加到待发送队列"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"同步四年级错题信息异常: {e}"
            }
            
    def process_complete_workflow(self, user_data: Dict, mistakes_list: List[Dict]) -> Dict:
        """
        处理完整的四年级工作流程
        参数:
            user_data: 用户信息
            mistakes_list: 错题列表
        返回:
            完整的处理结果
        """
        print("=" * 50)
        print("开始处理四年级完整工作流程...")
        print(f"用户: {user_data.get('username', '未知用户')}")
        print(f"错题数: {len(mistakes_list)}")
        
        # 1. 保存用户信息
        print("\n1. 保存四年级用户信息...")
        user_result = self.save_user_info(user_data)
        
        # 2. 保存错题
        print("\n2. 保存四年级错题...")
        mistake_results = []
        if mistakes_list:
            for i, mistake in enumerate(mistakes_list):
                print(f"  处理第 {i+1} 个错题...")
                result = self.save_mistake(user_data["phone"], mistake)
                mistake_results.append(result)
                time.sleep(0.3)  # 短暂延迟
                
        # 统计结果
        total_mistakes = len(mistakes_list)
        success_mistakes = sum(1 for r in mistake_results if r.get("success", False))
        cloud_success_users = 1 if user_result.get("cloud_synced", False) else 0
        cloud_success_mistakes = sum(1 for r in mistake_results if r.get("cloud_synced", False))
        
        # 3. 获取状态
        print("\n3. 检查当前状态...")
        status = self.get_status()
        
        result = {
            "success": user_result["success"] and (total_mistakes == 0 or success_mistakes == total_mistakes),
            "message": f"四年级工作流程完成，用户保存{'成功' if user_result['success'] else '失败'}，{success_mistakes}/{total_mistakes}个错题保存成功",
            "user_result": user_result,
            "mistake_results": mistake_results,
            "status": status,
            "cloud_sync_summary": {
                "users": {"total": 1, "success": cloud_success_users},
                "mistakes": {"total": total_mistakes, "success": cloud_success_mistakes}
            },
            "timestamp": datetime.now().isoformat(),
            "grade": "四年级"
        }
        
        print(f"\n[OK] 四年级完整工作流程处理完成!")
        print(f"  用户保存: {'[OK] 成功' if user_result['success'] else '[ERROR] 失败'}")
        print(f"  错题保存: {success_mistakes}/{total_mistakes} 成功")
        print(f"  云同步用户: {cloud_success_users}/1 成功")
        print(f"  云同步错题: {cloud_success_mistakes}/{total_mistakes} 成功")
        
        return result
        
    def get_status(self) -> Dict:
        """获取四年级数据状态"""
        try:
            # 读取用户数据
            with open(self.local_users_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                users = user_data.get("users", [])
                
            # 读取错题数据
            with open(self.local_mistakes_file, 'r', encoding='utf-8') as f:
                mistake_data = json.load(f)
                mistakes = mistake_data.get("mistakes", [])
                
            # 计算同步状态
            pending_users = [u for u in users if u.get("sync_status") != "synced"]
            pending_mistakes = [m for m in mistakes if m.get("sync_status") != "synced"]
            
            # 检查云服务器连接
            cloud_connected = False
            if self.cloud_enabled:
                cloud_connected = self.cloud_sender.check_cloud_health()
                
            return {
                "grade": "四年级",
                "local_users_count": len(users),
                "local_mistakes_count": len(mistakes),
                "pending_sync_users": len(pending_users),
                "pending_sync_mistakes": len(pending_mistakes),
                "cloud_enabled": self.cloud_enabled,
                "cloud_connected": cloud_connected,
                "cache_dir": self.cache_dir,
                "last_user_update": user_data.get("last_updated", "未知"),
                "last_mistake_update": mistake_data.get("last_updated", "未知"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "grade": "四年级",
                "error": f"获取状态失败: {e}",
                "timestamp": datetime.now().isoformat()
            }
            
    def start_auto_sync(self, interval_minutes: int = 10):
        """启动四年级自动同步"""
        if not self.cloud_enabled:
            print("[ERROR] 云服务器功能未启用，无法启动自动同步")
            return None
            
        # 启动云服务器的后台同步
        thread = self.cloud_sender.start_background_sync(interval_minutes)
        print(f"[OK] 四年级自动同步已启动，间隔: {interval_minutes}分钟")
        return thread
        
    def force_sync_all(self) -> Dict:
        """强制同步所有四年级数据"""
        if not self.cloud_enabled:
            return {
                "success": False, 
                "message": "云服务器功能未启用",
                "grade": "四年级"
            }
            
        print("开始强制同步所有四年级数据...")
        
        try:
            # 从本地加载数据
            with open(self.local_users_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                users = user_data.get("users", [])
                
            with open(self.local_mistakes_file, 'r', encoding='utf-8') as f:
                mistake_data = json.load(f)
                mistakes = mistake_data.get("mistakes", [])
                
            user_results = []
            mistake_results = []
            
            # 同步用户
            for user in users:
                if user.get("sync_status") != "synced":
                    result = self._sync_user_to_cloud(user)
                    user_results.append({
                        "phone": user.get("phone"),
                        "success": result.get("success", False)
                    })
                    
            # 同步错题
            for mistake in mistakes:
                if mistake.get("sync_status") != "synced":
                    user_phone = mistake.get("user_phone")
                    result = self._sync_mistake_to_cloud(user_phone, mistake)
                    mistake_results.append({
                        "mistake_id": mistake.get("mistake_id"),
                        "success": result.get("success", False)
                    })
                    
            total_users = len(user_results)
            total_mistakes = len(mistake_results)
            success_users = sum(1 for r in user_results if r.get("success", False))
            success_mistakes = sum(1 for r in mistake_results if r.get("success", False))
            
            return {
                "success": True,
                "message": "四年级数据强制同步完成",
                "grade": "四年级",
                "users": {
                    "total": total_users,
                    "success": success_users,
                    "failed": total_users - success_users
                },
                "mistakes": {
                    "total": total_mistakes,
                    "success": success_mistakes,
                    "failed": total_mistakes - success_mistakes
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"强制同步失败: {e}",
                "grade": "四年级",
                "timestamp": datetime.now().isoformat()
            }

def demo_fourth_grade_workflow():
    """演示四年级完整工作流程"""
    print("四年级数学教程技能演示")
    print("=" * 50)
    
    handler = FourthGradeDataHandler()
    
    # 四年级用户数据
    user_data = {
        "username": "小明（四年级）",
        "phone": "13800138015",
        "grade": "四年级",
        "password": "xiaoming4",
        "hobbies": "数学、编程、科学实验",
        "created_from": "fourth_grade_math_tutor"
    }
    
    # 四年级错题数据（典型四年级数学题）
    mistakes = [
        {
            "question_text": "一个数由5个亿、3个百万、2个万和8个千组成，这个数写作什么？",
            "subject": "数学",
            "wrong_answer": "5030208000",
            "correct_answer": "503028000",
            "error_type": "大数读写错误",
            "hint_level": "L2"
        },
        {
            "question_text": "125×88用简便方法计算，应该怎么算？",
            "subject": "数学",
            "wrong_answer": "125×80×8=80000",
            "correct_answer": "125×80+125×8=11000",
            "error_type": "运算定律应用错误",
            "hint_level": "L3"
        },
        {
            "question_text": "一个等腰三角形，顶角是80°，底角是多少度？",
            "subject": "数学",
            "wrong_answer": "50°",
            "correct_answer": "50°",
            "error_type": "三角形内角和计算",
            "hint_level": "L2"
        }
    ]
    
    # 执行完整工作流程
    result = handler.process_complete_workflow(user_data, mistakes)
    
    # 显示详细状态
    print("\n" + "=" * 50)
    print("详细状态报告:")
    status = handler.get_status()
    print(f"年级: {status['grade']}")
    print(f"本地用户数: {status['local_users_count']}")
    print(f"本地错题数: {status['local_mistakes_count']}")
    print(f"待同步用户: {status['pending_sync_users']}")
    print(f"待同步错题: {status['pending_sync_mistakes']}")
    print(f"云服务器连接: {'[OK] 已连接' if status['cloud_connected'] else '[WARN] 未连接'}")
    
    # 如果云服务器可用，尝试同步
    if status["cloud_connected"]:
        print("\n尝试同步到云服务器...")
        sync_result = handler.force_sync_all()
        print(f"同步结果: {sync_result['message']}")
        
    print("\n演示完成!")

def interactive_mode():
    """四年级交互式模式"""
    handler = FourthGradeDataHandler()
    
    print("四年级数学教程技能 - 交互模式")
    print("=" * 50)
    
    while True:
        print("\n选择功能:")
        print("1. 输入四年级用户信息")
        print("2. 输入四年级错题")
        print("3. 查看四年级状态")
        print("4. 同步四年级数据")
        print("5. 演示四年级完整流程")
        print("0. 退出")
        
        try:
            choice = input("请选择 (0-5): ").strip()
            
            if choice == "0":
                print("退出四年级交互模式")
                break
                
            elif choice == "1":
                # 输入四年级用户信息
                print("\n输入四年级用户信息:")
                user_data = {}
                user_data["username"] = input("姓名: ").strip()
                user_data["phone"] = input("手机号 (11位): ").strip()
                user_data["grade"] = "四年级"  # 固定为四年级
                user_data["password"] = input("密码: ").strip()
                user_data["hobbies"] = input("爱好: ").strip()
                user_data["created_from"] = input("来源标识 (默认: fourth_grade_math): ").strip() or "fourth_grade_math"
                
                result = handler.save_user_info(user_data)
                print(f"\n结果: {result['message']}")
                
            elif choice == "2":
                # 输入四年级错题
                print("\n输入四年级错题信息:")
                user_phone = input("用户手机号: ").strip()
                
                mistakes = []
                while True:
                    print(f"\n四年级错题 #{len(mistakes) + 1}:")
                    mistake = {}
                    mistake["question_text"] = input("题目: ").strip()
                    mistake["subject"] = input("科目 (默认: 数学): ").strip() or "数学"
                    mistake["wrong_answer"] = input("错误答案: ").strip()
                    mistake["correct_answer"] = input("正确答案: ").strip()
                    mistake["error_type"] = input("错误类型 (默认: 计算错误): ").strip() or "计算错误"
                    mistake["hint_level"] = input("提示级别 (L1-L4，默认: L2): ").strip() or "L2"
                    
                    mistakes.append(mistake)
                    
                    more = input("继续输入错题? (y/n): ").strip().lower()
                    if more != 'y':
                        break
                        
                if mistakes:
                    results = []
                    for mistake in mistakes:
                        result = handler.save_mistake(user_phone, mistake)
                        results.append(result)
                        time.sleep(0.5)
                        
                    success_count = sum(1 for r in results if r.get("success", False))
                    print(f"\n结果: {success_count}/{len(mistakes)} 个错题保存成功")
                    
            elif choice == "3":
                # 查看状态
                status = handler.get_status()
                print("\n四年级数据状态:")
                print(f"  年级: {status['grade']}")
                print(f"  本地用户数: {status['local_users_count']}")
                print(f"  本地错题数: {status['local_mistakes_count']}")
                print(f"  待同步用户: {status['pending_sync_users']}")
                print(f"  待同步错题: {status['pending_sync_mistakes']}")
                print(f"  云服务器: {'[OK] 已启用' if status['cloud_enabled'] else '[WARN] 未启用'}")
                print(f"  云连接: {'[OK] 已连接' if status['cloud_connected'] else '[WARN] 未连接'}")
                print(f"  最后更新: {status.get('last_user_update', '未知')}")
                
            elif choice == "4":
                # 同步数据
                print("\n开始同步四年级数据...")
                result = handler.force_sync_all()
                print(f"同步结果: {result['message']}")
                if result['success']:
                    print(f"用户: {result['users']['success']}/{result['users']['total']} 成功")
                    print(f"错题: {result['mistakes']['success']}/{result['mistakes']['total']} 成功")
                    
            elif choice == "5":
                # 演示完整流程
                demo_fourth_grade_workflow()
                
            else:
                print("无效选择，请重试")
                
        except KeyboardInterrupt:
            print("\n操作取消")
            break
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    print("四年级数学教程技能数据处理器")
    print("功能:")
    print("1. 交互式模式")
    print("2. 演示完整工作流程")
    print("3. 测试云服务器连接")
    
    try:
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            interactive_mode()
        elif choice == "2":
            demo_fourth_grade_workflow()
        elif choice == "3":
            from cloud_data_sender import test_cloud_connection
            test_cloud_connection()
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n操作取消")
    except Exception as e:
        print(f"错误: {e}")