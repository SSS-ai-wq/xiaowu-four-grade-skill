#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
云服务器数据发送器
向云服务器接口发送用户信息和错题数据，保证数据一定能发送
支持重试机制、本地缓存和自动恢复
"""

import json
import os
import sys
import time
import hashlib
import requests
from datetime import datetime, timedelta
import socket
import threading
from typing import Dict, List, Optional, Any

print("云服务器数据发送器 v1.0")
print("=" * 50)

# 配置
class Config:
    # 云服务器API端点
    CLOUD_API_BASE = "http://182.92.156.154:3000"  # 云服务器地址
    # API路径
    API_REGISTER_USER = "/api/users/register"  # 注册用户
    API_SUBMIT_MISTAKE = "/api/mistakes/submit"  # 提交错题
    API_GET_SESSION = "/api/sessions/create"    # 创建会话
    API_HEALTH_CHECK = "/api/health"            # 健康检查
    
    # 重试配置
    MAX_RETRIES = 10  # 最大重试次数
    INITIAL_RETRY_DELAY = 1  # 初始重试延迟（秒）
    MAX_RETRY_DELAY = 300  # 最大重试延迟（5分钟）
    RETRY_MULTIPLIER = 2  # 重试延迟乘数
    
    # 超时配置
    REQUEST_TIMEOUT = 30  # 请求超时（秒）
    
    # 本地缓存配置
    CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
    PENDING_USERS_FILE = "pending_users.json"
    PENDING_MISTAKES_FILE = "pending_mistakes.json"
    SENT_DATA_FILE = "sent_data_log.json"
    
    # 日志配置
    LOG_FILE = "cloud_sender.log"

class CloudDataSender:
    def __init__(self):
        self.config = Config()
        self._ensure_cache_dir()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MathTutorDataSender/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.config.CACHE_DIR):
            os.makedirs(self.config.CACHE_DIR)
            
    def _load_pending_data(self, filename: str) -> List[Dict]:
        """加载待发送数据"""
        filepath = os.path.join(self.config.CACHE_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def _save_pending_data(self, filename: str, data: List[Dict]):
        """保存待发送数据"""
        filepath = os.path.join(self.config.CACHE_DIR, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存待发送数据失败: {e}")
            
    def _log_sent_data(self, data_type: str, data_id: str, success: bool, response: Optional[Dict] = None):
        """记录已发送数据"""
        log_file = os.path.join(self.config.CACHE_DIR, self.config.SENT_DATA_FILE)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "data_id": data_id,
            "success": success,
            "response": response
        }
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {"logs": []}
                
            log_data["logs"].append(log_entry)
            
            # 只保留最近1000条日志
            if len(log_data["logs"]) > 1000:
                log_data["logs"] = log_data["logs"][-1000:]
                
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"记录日志失败: {e}")
            
    def _log_message(self, message: str, level: str = "INFO"):
        """记录日志消息"""
        log_file = os.path.join(self.config.CACHE_DIR, self.config.LOG_FILE)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass
            
    def check_cloud_health(self) -> bool:
        """检查云服务器健康状态"""
        try:
            url = f"{self.config.CLOUD_API_BASE}{self.config.API_HEALTH_CHECK}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "ok"
        except Exception as e:
            self._log_message(f"健康检查失败: {e}", "WARNING")
        return False
        
    def _calculate_backoff(self, retry_count: int) -> float:
        """计算退避时间"""
        delay = self.config.INITIAL_RETRY_DELAY * (self.config.RETRY_MULTIPLIER ** retry_count)
        return min(delay, self.config.MAX_RETRY_DELAY)
        
    def _send_with_retry(self, url: str, data: Dict, data_type: str, data_id: str) -> bool:
        """带重试机制发送数据"""
        for retry_count in range(self.config.MAX_RETRIES):
            try:
                self._log_message(f"发送{data_type}数据 (尝试 {retry_count + 1}/{self.config.MAX_RETRIES})")
                
                response = self.session.post(
                    url,
                    json=data,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self._log_sent_data(data_type, data_id, True, result)
                    self._log_message(f"{data_type}数据发送成功: {data_id}")
                    return True
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                    self._log_message(f"{data_type}数据发送失败: {error_msg}", "ERROR")
                    
            except requests.exceptions.Timeout:
                self._log_message(f"{data_type}数据发送超时 (尝试 {retry_count + 1})", "WARNING")
            except requests.exceptions.ConnectionError:
                self._log_message(f"连接云服务器失败 (尝试 {retry_count + 1})", "WARNING")
            except Exception as e:
                self._log_message(f"发送{data_type}数据异常: {e} (尝试 {retry_count + 1})", "ERROR")
                
            # 计算并等待重试延迟
            if retry_count < self.config.MAX_RETRIES - 1:
                delay = self._calculate_backoff(retry_count)
                self._log_message(f"等待 {delay:.1f} 秒后重试...")
                time.sleep(delay)
                
        self._log_message(f"{data_type}数据发送失败，达到最大重试次数: {data_id}", "ERROR")
        self._log_sent_data(data_type, data_id, False)
        return False
        
    def register_user(self, user_data: Dict) -> bool:
        """注册用户到云服务器"""
        # 生成唯一ID
        user_id = f"user_{hashlib.md5(json.dumps(user_data, sort_keys=True).encode()).hexdigest()[:8]}"
        
        # 准备请求数据
        request_data = {
            "phone": user_data.get("phone", ""),
            "username": user_data.get("username", ""),
            "grade": user_data.get("grade", ""),
            "password_hash": hashlib.sha256(user_data.get("password", "").encode()).hexdigest(),
            "created_from": user_data.get("created_from", "math_tutor")
        }
        
        url = f"{self.config.CLOUD_API_BASE}{self.config.API_REGISTER_USER}"
        return self._send_with_retry(url, request_data, "user", user_id)
        
    def submit_mistake(self, user_phone: str, mistake_data: Dict) -> bool:
        """提交错题到云服务器"""
        # 生成唯一ID
        mistake_id = f"mistake_{hashlib.md5(json.dumps(mistake_data, sort_keys=True).encode()).hexdigest()[:8]}"
        
        # 准备请求数据
        request_data = {
            "user_phone": user_phone,
            "question_text": mistake_data.get("question_text", ""),
            "subject": mistake_data.get("subject", "数学"),
            "wrong_answer": mistake_data.get("wrong_answer", ""),
            "correct_answer": mistake_data.get("correct_answer", ""),
            "error_type": mistake_data.get("error_type", "计算错误")
        }
        
        url = f"{self.config.CLOUD_API_BASE}{self.config.API_SUBMIT_MISTAKE}"
        return self._send_with_retry(url, request_data, "mistake", mistake_id)
        
    def create_teaching_session(self, user_phone: str) -> Optional[Dict]:
        """创建教学会话"""
        try:
            url = f"{self.config.CLOUD_API_BASE}{self.config.API_GET_SESSION}"
            request_data = {
                "user_phone": user_phone,
                "session_type": "math_tutoring"
            }
            
            response = self.session.post(
                url,
                json=request_data,
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self._log_message(f"创建教学会话失败: {e}", "ERROR")
        return None
        
    def process_pending_data(self):
        """处理所有待发送数据"""
        print("开始处理待发送数据...")
        
        # 处理待发送用户
        pending_users = self._load_pending_data(self.config.PENDING_USERS_FILE)
        if pending_users:
            print(f"发现 {len(pending_users)} 个待发送用户")
            
            successful_users = []
            failed_users = []
            
            for user in pending_users:
                if self.register_user(user):
                    successful_users.append(user)
                else:
                    failed_users.append(user)
                    
            # 保存失败的用户（下次重试）
            if failed_users:
                self._save_pending_data(self.config.PENDING_USERS_FILE, failed_users)
                print(f"{len(failed_users)} 个用户发送失败，已保存待重试")
            else:
                # 删除空文件
                filepath = os.path.join(self.config.CACHE_DIR, self.config.PENDING_USERS_FILE)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
            print(f"{len(successful_users)} 个用户发送成功")
            
        # 处理待发送错题
        pending_mistakes = self._load_pending_data(self.config.PENDING_MISTAKES_FILE)
        if pending_mistakes:
            print(f"发现 {len(pending_mistakes)} 个待发送错题")
            
            successful_mistakes = []
            failed_mistakes = []
            
            for mistake in pending_mistakes:
                user_phone = mistake.get("user_phone", "")
                if self.submit_mistake(user_phone, mistake):
                    successful_mistakes.append(mistake)
                else:
                    failed_mistakes.append(mistake)
                    
            # 保存失败的错题（下次重试）
            if failed_mistakes:
                self._save_pending_data(self.config.PENDING_MISTAKES_FILE, failed_mistakes)
                print(f"{len(failed_mistakes)} 个错题发送失败，已保存待重试")
            else:
                # 删除空文件
                filepath = os.path.join(self.config.CACHE_DIR, self.config.PENDING_MISTAKES_FILE)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
            print(f"{len(successful_mistakes)} 个错题发送成功")
            
        print("待发送数据处理完成")
        
    def add_pending_user(self, user_data: Dict):
        """添加待发送用户"""
        pending_users = self._load_pending_data(self.config.PENDING_USERS_FILE)
        
        # 检查是否已存在
        phone = user_data.get("phone", "")
        for i, user in enumerate(pending_users):
            if user.get("phone") == phone:
                pending_users[i] = user_data  # 更新现有用户
                break
        else:
            pending_users.append(user_data)  # 添加新用户
            
        self._save_pending_data(self.config.PENDING_USERS_FILE, pending_users)
        print(f"用户已添加到待发送队列: {phone}")
        
    def add_pending_mistake(self, user_phone: str, mistake_data: Dict):
        """添加待发送错题"""
        mistake_data["user_phone"] = user_phone
        pending_mistakes = self._load_pending_data(self.config.PENDING_MISTAKES_FILE)
        pending_mistakes.append(mistake_data)
        self._save_pending_data(self.config.PENDING_MISTAKES_FILE, pending_mistakes)
        print(f"错题已添加到待发送队列: {mistake_data.get('question_text', '')[:50]}...")
        
    def start_background_sync(self, interval_minutes: int = 5):
        """启动后台同步线程"""
        def sync_worker():
            while True:
                try:
                    time.sleep(interval_minutes * 60)
                    self._log_message("开始定时同步...")
                    self.process_pending_data()
                    self._log_message("定时同步完成")
                except Exception as e:
                    self._log_message(f"定时同步异常: {e}", "ERROR")
                    
        thread = threading.Thread(target=sync_worker, daemon=True)
        thread.start()
        self._log_message(f"后台同步线程已启动，间隔: {interval_minutes}分钟")
        return thread

def test_cloud_connection():
    """测试云服务器连接"""
    print("测试云服务器连接...")
    sender = CloudDataSender()
    
    if sender.check_cloud_health():
        print("✅ 云服务器健康检查通过")
        return True
    else:
        print("❌ 云服务器连接失败")
        return False
        
def demo_send_data():
    """演示发送数据"""
    print("\n演示发送数据...")
    sender = CloudDataSender()
    
    # 测试用户数据
    test_user = {
        "username": "测试用户",
        "phone": "13800138000",
        "grade": "一年级",
        "password": "test123",
        "created_from": "demo"
    }
    
    # 测试错题数据
    test_mistake = {
        "question_text": "3 + 5 = ?",
        "subject": "数学",
        "wrong_answer": "7",
        "correct_answer": "8",
        "error_type": "计算错误"
    }
    
    # 先添加到待发送队列
    sender.add_pending_user(test_user)
    sender.add_pending_mistake(test_user["phone"], test_mistake)
    
    # 尝试发送
    print("尝试发送待处理数据...")
    sender.process_pending_data()
    
    print("演示完成")

def monitor_pending_data():
    """监控待发送数据状态"""
    print("\n待发送数据状态监控...")
    sender = CloudDataSender()
    
    pending_users = sender._load_pending_data(Config.PENDING_USERS_FILE)
    pending_mistakes = sender._load_pending_data(Config.PENDING_MISTAKES_FILE)
    
    print(f"待发送用户数: {len(pending_users)}")
    for user in pending_users[:5]:  # 显示前5个
        print(f"  - {user.get('username', '未知')} ({user.get('phone', '无手机号')})")
        
    if len(pending_users) > 5:
        print(f"  ... 还有 {len(pending_users) - 5} 个用户")
        
    print(f"待发送错题数: {len(pending_mistakes)}")
    for mistake in pending_mistakes[:5]:  # 显示前5个
        question = mistake.get('question_text', '无题目')
        print(f"  - {question[:50]}...")
        
    if len(pending_mistakes) > 5:
        print(f"  ... 还有 {len(pending_mistakes) - 5} 个错题")
        
    # 检查日志文件
    log_file = os.path.join(Config.CACHE_DIR, Config.LOG_FILE)
    if os.path.exists(log_file):
        print(f"\n日志文件: {log_file}")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"最后5条日志:")
                    for line in lines[-5:]:
                        print(f"  {line.strip()}")
        except:
            print("无法读取日志文件")

if __name__ == "__main__":
    print("云服务器数据发送器")
    print("功能:")
    print("1. 测试云服务器连接")
    print("2. 发送演示数据")
    print("3. 监控待发送数据状态")
    print("4. 启动后台同步")
    print("\n请选择功能 (1-4): ")
    
    try:
        choice = input().strip()
        
        if choice == "1":
            test_cloud_connection()
        elif choice == "2":
            demo_send_data()
        elif choice == "3":
            monitor_pending_data()
        elif choice == "4":
            sender = CloudDataSender()
            thread = sender.start_background_sync(interval_minutes=5)
            print("后台同步已启动，按Ctrl+C停止")
            try:
                thread.join()
            except KeyboardInterrupt:
                print("停止后台同步")
        else:
            print("无效选择")
            
    except KeyboardInterrupt:
        print("\n操作取消")
    except Exception as e:
        print(f"错误: {e}")