#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四年级数学自动问题上传器 - 核心模块
专门为四年级数学设计，每次提问自动上传
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional


class FourthGradeAutoUploader:
    """
    四年级数学自动问题上传器
    智能体友好的接口，专门适配四年级数学知识点
    """
    
    def __init__(self, server_url: str = "http://182.92.156.154"):
        """
        初始化四年级上传器
        """
        self.server_url = server_url.rstrip('/')
        self.cache_dir = self._get_cache_dir()
        
        # 四年级专用测试账号
        self.default_account = {
            "phone": "13800000000",
            "password": "test123",
            "user_id": 33,
            "grade": "四年级"
        }
        
        print(f"四年级数学自动上传器已初始化")
        print(f"服务器: {server_url}")
        print(f"默认账号: {self.default_account['phone']} (ID: {self.default_account['user_id']})")
        
        # 检查服务器状态
        self._check_server()
    
    def _get_cache_dir(self):
        """获取缓存目录"""
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_dir = os.path.join(skill_dir, "cache")
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        return cache_dir
    
    def _check_server(self):
        """检查服务器状态"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("服务器连接正常")
            else:
                print(f"服务器响应异常: {response.status_code}")
        except Exception as e:
            print(f"服务器连接失败: {e}")
            print("将使用本地缓存模式")
    
    def upload_fourth_grade_question(self, question: str, user_info: Optional[Dict] = None) -> Dict:
        """
        上传四年级数学问题（智能体主要调用此方法）
        """
        if user_info is None:
            user_info = self.default_account
        
        print(f"[四年级自动上传] 处理提问: {question[:50]}...")
        
        # 1. 提取四年级知识点
        knowledge_point = self._extract_fourth_grade_knowledge(question)
        print(f"  知识点识别: {knowledge_point}")
        
        # 2. 上传到错题数据库
        result = self._upload_to_wrong_questions(question, knowledge_point, user_info)
        
        # 3. 同时尝试上传知识点
        if result.get("success"):
            knowledge_result = self._upload_knowledge_point(question, knowledge_point, user_info)
            result["knowledge_result"] = knowledge_result
        else:
            # 上传失败，缓存数据
            self._cache_question_data(question, knowledge_point, user_info)
        
        return result
    
    def _extract_fourth_grade_knowledge(self, question: str) -> str:
        """
        从问题中智能提取四年级知识点
        """
        question_lower = question.lower()
        
        # 四年级数学知识点识别规则
        knowledge_rules = [
            # 大数的认识
            (["大数", "亿以内", "亿以上", "万", "亿", "千万", "百万"], "大数的认识"),
            (["近似数", "四舍五入", "精确"], "近似数"),
            
            # 三位数乘两位数
            (["三位数乘两位数", "乘数", "积", "末尾有0"], "三位数乘两位数"),
            (["单价×数量", "速度×时间", "路程", "总价"], "数量关系"),
            
            # 除数是两位数的除法
            (["除数是两位数", "试商", "商", "余数"], "除数是两位数的除法"),
            (["估算", "大约", "接近"], "估算"),
            
            # 角的度量
            (["角", "锐角", "直角", "钝角", "平角", "周角", "量角"], "角的度量"),
            (["直线", "射线", "线段", "垂直", "平行"], "线与角"),
            
            # 平行四边形和梯形
            (["平行四边形", "梯形", "高", "底", "对边"], "平行四边形和梯形"),
            
            # 小数运算
            (["小数", "小数点", "小数部分", "整数部分"], "小数的意义与性质"),
            (["小数加法", "小数减法", "小数加减", "+", "-"], "小数的加法和减法"),
            
            # 运算定律
            (["加法交换律", "加法结合律", "乘法交换律", "乘法结合律", "乘法分配律"], "运算定律与简便计算"),
            (["简便计算", "简便运算", "简便方法"], "简便计算"),
            
            # 三角形
            (["三角形", "三边关系", "内角和", "等腰", "等边", "直角三角"], "三角形"),
            
            # 图形运动
            (["轴对称", "对称轴", "平移", "旋转"], "图形的运动"),
            
            # 平均数
            (["平均数", "平均", "均分", "平均分"], "平均数"),
            
            # 优化问题
            (["沏茶", "烙饼", "田忌赛马", "优化", "合理安排"], "优化问题"),
            
            # 鸡兔同笼
            (["鸡兔同笼", "鸡兔", "头数", "脚数"], "鸡兔同笼问题"),
            
            # 四则运算
            (["四则运算", "运算顺序", "先乘除后加减", "括号"], "四则运算"),
            
            # 应用题类型
            (["多少", "几", "几个"], "数量关系"),
            (["一共", "总共", "合计", "总和"], "求和问题"),
            (["还剩", "剩下", "剩余", "余下"], "求剩余问题"),
            (["平均", "每", "分给", "分成"], "平均分问题"),
            (["比较", "谁多", "谁少", "多多少", "少多少"], "比较问题"),
            (["原来", "现在", "增加", "减少", "变化"], "变化问题"),
            (["归一", "归总", "归一问题", "归总问题"], "归一归总问题"),
            
            # 统计
            (["统计", "条形图", "统计图", "数据分析"], "条形统计图"),
            
            # 观察物体
            (["观察物体", "从不同角度看", "三视图"], "观察物体")
        ]
        
        for keywords, knowledge in knowledge_rules:
            for keyword in keywords:
                if keyword in question_lower:
                    return knowledge
        
        return "四年级综合应用题"
    
    def _upload_to_wrong_questions(self, question: str, knowledge_point: str, user_info: Dict) -> Dict:
        """上传问题到错题数据库"""
        try:
            data = {
                "phone": user_info["phone"],
                "password": user_info["password"],
                "user_id": user_info.get("user_id", 33),
                "question_text": question,
                "subject": "数学",
                "knowledge_point": knowledge_point,
                "grade": user_info.get("grade", "四年级"),
                "ask_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "wrong_answer": "",
                "correct_answer": "",
                "error_type": "user_question"
            }
            
            response = requests.post(
                f"{self.server_url}/api/wrong-questions",
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  错题上传: 成功 (ID: {result.get('mistake_id', '未知')})")
                return {
                    "success": True,
                    "mistake_id": result.get("mistake_id"),
                    "action": "uploaded",
                    "message": "问题上传成功"
                }
            else:
                error_msg = f"API错误: {response.status_code}"
                print(f"  错题上传: 失败 ({error_msg})")
                return {
                    "success": False,
                    "error": error_msg,
                    "action": "cached",
                    "message": "数据已缓存"
                }
                
        except Exception as e:
            error_msg = str(e)
            print(f"  错题上传: 异常 ({error_msg})")
            return {
                "success": False,
                "error": error_msg,
                "action": "cached",
                "message": "网络异常，数据已缓存"
            }
    
    def _upload_knowledge_point(self, question: str, knowledge_point: str, user_info: Dict) -> Dict:
        """上传知识点到知识点数据库"""
        try:
            data = {
                "phone": user_info["phone"],
                "password": user_info["password"],
                "user_id": user_info.get("user_id", 33),
                "knowledge_point": knowledge_point,
                "subject": "数学",
                "grade": user_info.get("grade", "四年级"),
                "related_question": question[:100],
                "mastery_level": 0,
                "practice_count": 1,
                "last_practiced": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 尝试所有可能的API端点
            endpoints = [
                f"{self.server_url}/api/knowledge-points",
                f"{self.server_url}/api/knowledge_points",
                f"{self.server_url}/api/user-knowledge-mastery",
                f"{self.server_url}/api/knowledge"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.post(endpoint, json=data, timeout=5)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  知识点上传: 成功 ({endpoint.split('/')[-1]})")
                        return {
                            "success": True,
                            "knowledge_id": result.get("id") or result.get("knowledge_id"),
                            "endpoint": endpoint.split('/')[-1],
                            "message": "知识点上传成功"
                        }
                except:
                    continue
            
            # 所有知识点API都失败，使用错题API替代
            print("  知识点API不可用，使用错题API替代")
            alt_data = {
                "phone": user_info["phone"],
                "password": user_info["password"],
                "user_id": user_info.get("user_id", 33),
                "question_text": f"四年级知识点: {knowledge_point}",
                "error_type": "knowledge_point_record",
                "knowledge_point": knowledge_point,
                "grade": "四年级"
            }
            
            response = requests.post(
                f"{self.server_url}/api/wrong-questions",
                json=alt_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"  知识点上传: 成功 (通过错题API)")
                return {
                    "success": True,
                    "alternative": True,
                    "message": "知识点通过错题API记录成功"
                }
            else:
                print(f"  知识点上传: 失败 (所有API都不可用)")
                return {
                    "success": False,
                    "error": "所有知识点API都不可用",
                    "message": "知识点上传失败"
                }
                
        except Exception as e:
            print(f"  知识点上传: 异常 ({e})")
            return {
                "success": False,
                "error": str(e),
                "message": "知识点上传异常"
            }
    
    def _cache_question_data(self, question: str, knowledge_point: str, user_info: Dict):
        """缓存问题数据"""
        cache_file = os.path.join(self.cache_dir, "fourth_grade_pending_questions.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                try:
                    cached_data = json.load(f)
                except:
                    cached_data = []
        else:
            cached_data = []
        
        cache_entry = {
            "question": question,
            "knowledge_point": knowledge_point,
            "user_info": user_info,
            "timestamp": time.time(),
            "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "grade": "四年级"
        }
        
        cached_data.append(cache_entry)
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, ensure_ascii=False, indent=2)
        
        print(f"  数据已缓存到: {cache_file}")
    
    def sync_cached_data(self) -> Dict:
        """同步所有缓存的数据"""
        cache_file = os.path.join(self.cache_dir, "fourth_grade_pending_questions.json")
        
        if not os.path.exists(cache_file):
            return {"success": True, "message": "没有缓存数据", "synced": 0}
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            print(f"[同步缓存] 发现 {len(cached_data)} 条四年级待上传数据")
            
            successful = []
            failed = []
            
            for i, data in enumerate(cached_data, 1):
                print(f"  处理 {i}/{len(cached_data)}: {data['question'][:30]}...")
                
                result = self.upload_fourth_grade_question(
                    question=data["question"],
                    user_info=data["user_info"]
                )
                
                if result.get("success"):
                    successful.append(data)
                else:
                    failed.append(data)
            
            if failed:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(failed, f, ensure_ascii=False, indent=2)
                print(f"  同步完成: 成功 {len(successful)} 条，失败 {len(failed)} 条")
            else:
                os.remove(cache_file)
                print(f"  同步完成: 所有 {len(successful)} 条数据已成功上传")
            
            return {
                "success": True,
                "synced": len(successful),
                "failed": len(failed),
                "total": len(cached_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "同步缓存数据失败"
            }
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        status = {
            "server_url": self.server_url,
            "default_account": {
                "phone": self.default_account["phone"],
                "user_id": self.default_account["user_id"],
                "grade": self.default_account["grade"]
            },
            "cache_status": {},
            "server_health": "unknown"
        }
        
        # 检查缓存文件
        cache_file = os.path.join(self.cache_dir, "fourth_grade_pending_questions.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                status["cache_status"]["pending_questions"] = len(cached_data)
            except:
                status["cache_status"]["pending_questions"] = "读取失败"
        else:
            status["cache_status"]["pending_questions"] = 0
        
        # 检查服务器健康
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=3)
            if response.status_code == 200:
                status["server_health"] = "healthy"
            else:
                status["server_health"] = f"unhealthy ({response.status_code})"
        except:
            status["server_health"] = "unreachable"
        
        return status


# 智能体友好的简化接口
def upload_fourth_grade_question(question: str, user_info: Optional[Dict] = None) -> Dict:
    """智能体友好接口：上传四年级数学问题"""
    uploader = FourthGradeAutoUploader()
    return uploader.upload_fourth_grade_question(question, user_info)


def sync_fourth_grade_data() -> Dict:
    """同步所有四年级缓存数据"""
    uploader = FourthGradeAutoUploader()
    return uploader.sync_cached_data()


def get_fourth_grade_status() -> Dict:
    """获取四年级系统状态"""
    uploader = FourthGradeAutoUploader()
    return uploader.get_status()


# 快速测试函数
if __name__ == "__main__":
    print("=== 四年级数学自动上传器测试 ===")
    
    uploader = FourthGradeAutoUploader()
    
    # 四年级典型问题测试
    test_questions = [
        "325 × 24 = ?",                          # 三位数乘两位数
        "什么是乘法分配律？",                     # 运算定律
        "一个平角等于几个直角？",                  # 角的度量
        "小数 3.45 中，3 在什么位？",             # 小数的意义
        "鸡兔同笼，头35个，脚94只，鸡兔各几只？"    # 鸡兔同笼
    ]
    
    for question in test_questions:
        print(f"\n测试问题: {question}")
        result = uploader.upload_fourth_grade_question(question)
        print(f"结果: {'成功' if result.get('success') else '失败'}")
        time.sleep(1)
    
    print("\n测试完成！")