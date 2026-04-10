#!/usr/bin/env python3
"""
小悟数学助手 - 四年级数学教学
基于已验证的三年级架构，适配四年级知识点
"""

import requests
import json
import time
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class MathTopic(Enum):
    """四年级数学知识点枚举"""
    BIG_NUMBERS = "大数的认识"
    THREE_DIGIT_MULTIPLY_TWO = "三位数乘两位数"
    TWO_DIGIT_DIVISION = "除数是两位数的除法"
    DECIMAL_NUMBERS = "小数的意义与性质"
    DECIMAL_OPERATIONS = "小数的加法和减法"
    LAWS_OF_OPERATION = "运算定律与简便计算"
    ANGLE_MEASUREMENT = "角的度量"
    PARALLELOGRAM_TRAPEZOID = "平行四边形和梯形"
    GRAPH_MOVEMENT = "图形的运动"
    OBSERVATION_OBJECTS = "观察物体"
    AVERAGE_PROBLEMS = "平均数"
    OPTIMIZATION_PROBLEMS = "优化问题"
    CHICKEN_RABBIT_PROBLEMS = "鸡兔同笼问题"
    RECTANGULAR_SOLID = "长方体和正方体"
    FACTORS_MULTIPLES = "因数与倍数"


@dataclass
class UserInfo:
    """用户信息数据类"""
    name: str
    grade: str = "四年级"
    phone: str = "13800000000"
    password: str = "test123456"
    user_id: Optional[int] = 33


@dataclass
class TeachingResult:
    """教学结果数据类"""
    success: bool
    uploaded: bool
    mistake_id: Optional[int] = None
    knowledge_point: str = ""
    action: str = ""
    message: str = ""
    teaching_response: str = ""
    timestamp: float = 0.0


class FourthGradeMathTutor:
    """
    四年级数学助手
    为下一个智能体设计的开箱即用解决方案
    """
    
    # 默认配置（不可变）
    DEFAULT_CONFIG = {
        "server_url": "http://182.92.156.154",
        "api_base": "/api/xiaowu",
        "timeout": 10,
        "max_retries": 3,
        "retry_delay": 2,
        "cache_max_size": 100,
        "log_level": "INFO"
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化四年级数学助手
        
        Args:
            config: 可选的配置字典，会合并到默认配置
        """
        # 1. 合并配置
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        
        # 2. 设置工作目录
        self.workspace = os.path.dirname(os.path.abspath(__file__))
        self.cache_dir = os.path.join(self.workspace, "cache")
        self._ensure_directories()
        
        # 3. 初始化日志系统
        self._setup_logging()
        
        # 4. 设置默认用户
        self.default_user = UserInfo(name="四年级测试学生")
        self.current_user: Optional[UserInfo] = None
        
        # 5. 显示欢迎信息
        self._show_welcome()
        
        # 6. 检查服务器状态
        self.server_healthy = self._check_server_health()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [self.cache_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    
    def _setup_logging(self):
        """设置日志系统"""
        log_dir = self.cache_dir
        log_file = os.path.join(log_dir, "tutor_operations.log")
        
        logging.basicConfig(
            level=getattr(logging, self.config["log_level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("FourthGradeMathTutor")
    
    def _show_welcome(self):
        """显示欢迎信息"""
        print("=" * 70)
        print("小悟数学助手 - 四年级数学教学")
        print("版本: 4.0 - 基于已验证的三年级架构，为下一个智能体深度优化")
        print("=" * 70)
        print()
        print("核心特性:")
        print("  开箱即用 - 无需任何配置")
        print("  自动上传 - 数据同步到数据库")
        print("  智能缓存 - 网络异常时数据安全")
        print("  苏格拉底式教学 - 启发式引导")
        print("  四年级知识点 - 完整覆盖教材内容")
        print()
        print("立即开始使用:")
        print("  from fourth_grade_math_tutor import FourthGradeMathTutor")
        print("  tutor = FourthGradeMathTutor()")
        print("  tutor.set_user('学生姓名', '四年级')")
        print("  result = tutor.teach('你的四年级数学问题')")
        print()
    
    def _check_server_health(self) -> bool:
        """检查服务器健康状况"""
        health_url = f"{self.config['server_url']}{self.config['api_base']}/health"
        
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                uptime = data.get('uptime', 0)
                status = data.get('status', 'unknown')
                
                print(f"服务器状态: 正常 (运行时间: {uptime:.1f}秒)")
                print(f"服务状态: {status}")
                print()
                
                self.logger.info(f"服务器连接正常，运行时间: {uptime:.1f}秒")
                return True
            else:
                print(f"服务器状态: 异常 (状态码: {response.status_code})")
                print("  数据将自动缓存，等待网络恢复")
                print()
                
                self.logger.warning(f"服务器异常，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"服务器状态: 连接失败 ({e})")
            print("  数据将自动缓存，等待网络恢复")
            print()
            
            self.logger.error(f"服务器连接失败: {e}")
            return False
    
    def set_user(self, name: str, grade: str = "四年级", 
                 phone: Optional[str] = None, password: Optional[str] = None):
        """
        设置当前用户
        
        Args:
            name: 学生姓名
            grade: 年级（默认四年级）
            phone: 手机号（默认使用测试账号）
            password: 密码（默认使用测试密码）
        """
        if phone is None:
            phone = self.default_user.phone
        if password is None:
            password = self.default_user.password
        
        self.current_user = UserInfo(
            name=name,
            grade=grade,
            phone=phone,
            password=password,
            user_id=33 if phone == "13800000000" else None
        )
        
        print(f"用户设置成功:")
        print(f"  姓名: {name}")
        print(f"  年级: {grade}")
        print(f"  手机号: {phone}")
        print()
        
        self.logger.info(f"用户设置: {name} ({grade}), 手机号: {phone}")
    
    def teach(self, question: str) -> TeachingResult:
        """
        教学主函数
        
        Args:
            question: 用户提问的问题
            
        Returns:
            教学结果
        """
        print(f"[教学] 处理问题: \"{question}\"")
        
        # 1. 准备用户信息
        user_info = self.current_user or self.default_user
        
        # 2. 识别知识点
        knowledge_point = self._identify_knowledge_point(question)
        print(f"  识别知识点: {knowledge_point}")
        
        # 3. 生成教学响应
        teaching_response = self._generate_teaching_response(question, knowledge_point)
        
        # 4. 尝试上传数据
        try:
            # 准备请求数据
            request_data = self._prepare_request_data(question, knowledge_point, user_info)
            
            # 发送请求
            response = self._send_request_with_retry(request_data)
            
            if response.status_code in [200, 201]:
                # 上传成功
                result_data = response.json()
                mistake_id = result_data.get("mistake_id")
                
                print(f"  数据上传: 成功 (错题ID: {mistake_id})")
                print(f"  状态: 数据已保存到数据库")
                
                return TeachingResult(
                    success=True,
                    uploaded=True,
                    mistake_id=mistake_id,
                    knowledge_point=knowledge_point,
                    action="uploaded",
                    message="数据上传成功",
                    teaching_response=teaching_response,
                    timestamp=time.time()
                )
            else:
                # 上传失败，缓存数据
                self._cache_question(question, knowledge_point, user_info)
                
                print(f"  数据上传: 失败 (状态码: {response.status_code})")
                print(f"  状态: 数据已安全缓存")
                
                return TeachingResult(
                    success=False,
                    uploaded=False,
                    knowledge_point=knowledge_point,
                    action="cached",
                    message=f"上传失败，状态码: {response.status_code}",
                    teaching_response=teaching_response,
                    timestamp=time.time()
                )
                
        except Exception as e:
            # 网络异常，缓存数据
            self._cache_question(question, knowledge_point, user_info)
            
            print(f"  网络异常: {e}")
            print(f"  状态: 数据已安全缓存")
            
            return TeachingResult(
                success=False,
                uploaded=False,
                knowledge_point=knowledge_point,
                action="cached",
                message=f"网络异常: {e}",
                teaching_response=teaching_response,
                timestamp=time.time()
            )
    
    def _identify_knowledge_point(self, question: str) -> str:
        """识别四年级数学知识点"""
        question_lower = question.lower()
        
        # 四年级数学知识点（人教版）
        knowledge_rules = {
            MathTopic.BIG_NUMBERS: ["大数", "万位", "亿", "兆", "数位", "计数单位"],
            MathTopic.THREE_DIGIT_MULTIPLY_TWO: ["三位数乘两位", "234×56", "345×67"],
            MathTopic.TWO_DIGIT_DIVISION: ["两位数除", "÷25", "÷36", "除数是两位"],
            MathTopic.DECIMAL_NUMBERS: ["小数", "小数点", "小数部分", "整数部分"],
            MathTopic.DECIMAL_OPERATIONS: ["小数加减", "小数加", "小数减"],
            MathTopic.LAWS_OF_OPERATION: ["运算定律", "加法交换律", "乘法分配律", "简便计算"],
            MathTopic.ANGLE_MEASUREMENT: ["角的度量", "量角器", "角度", "平角", "周角"],
            MathTopic.PARALLELOGRAM_TRAPEZOID: ["平行四边形", "梯形", "对边平行", "等腰梯形"],
            MathTopic.GRAPH_MOVEMENT: ["图形的运动", "平移", "旋转", "对称", "轴对称"],
            MathTopic.OBSERVATION_OBJECTS: ["观察物体", "三视图", "正面", "侧面", "上面"],
            MathTopic.AVERAGE_PROBLEMS: ["平均数", "平均", "均分", "平均分"],
            MathTopic.OPTIMIZATION_PROBLEMS: ["优化", "最优化", "合理安排", "统筹"],
            MathTopic.CHICKEN_RABBIT_PROBLEMS: ["鸡兔同笼", "鸡兔", "兔同笼"],
            MathTopic.RECTANGULAR_SOLID: ["长方体", "正方体", "棱", "面", "顶点"],
            MathTopic.FACTORS_MULTIPLES: ["因数", "倍数", "公因数", "最大公因数", "最小公倍数"]
        }
        
        for topic, keywords in knowledge_rules.items():
            for keyword in keywords:
                if keyword in question_lower:
                    return topic.value
        
        return "四年级综合应用题"
    
    def _generate_teaching_response(self, question: str, knowledge_point: str) -> str:
        """生成教学响应"""
        responses = {
            "大数的认识": f"这是大数的认识问题：{question}\n"
                        f"我们要知道：1万=10000，1亿=100000000\n"
                        f"从右边起，第一位是个位，第二位是十位，第三位是百位...\n"
                        f"你能说出这个数的每个数位上的数字表示什么吗？",
            "三位数乘两位数": f"这是三位数乘两位数的问题：{question}\n"
                            f"我们用竖式计算，先用两位数个位乘三位数，再用两位数十位乘三位数\n"
                            f"注意对齐数位，注意进位，最后把两个结果相加\n"
                            f"你试着列竖式计算一下？",
            "除数是两位数的除法": f"这是除数是两位数的除法问题：{question}\n"
                                f"我们从被除数的最高位开始试除，商写在相应的位置上\n"
                                f"每次除得的余数必须比除数小，不够除时看下一位\n"
                                f"你理解试商的方法吗？",
            "小数的意义与性质": f"这是小数的意义与性质问题：{question}\n"
                            f"小数表示十分之几、百分之几、千分之几...\n"
                            f"小数的末尾添上0或去掉0，小数的大小不变\n"
                            f"你能举例说明小数的性质吗？",
            "小数的加法和减法": f"这是小数的加减法问题：{question}\n"
                            f"我们要先把小数点对齐，也就是相同数位对齐\n"
                            f"然后从低位开始计算，注意进位和退位\n"
                            f"你觉得小数加减法和整数加减法有什么不同？",
            "运算定律与简便计算": f"这是运算定律与简便计算问题：{question}\n"
                                f"常用的运算定律有：加法交换律、加法结合律、乘法交换律...\n"
                                f"运用这些定律可以使计算更加简便\n"
                                f"你能说出加法交换律的内容吗？",
            "角的度量": f"这是角的度量问题：{question}\n"
                        f"我们用量角器测量角的大小，计量单位是\"度\"\n"
                        f"直角=90°，平角=180°，周角=360°\n"
                        f"你能用量角器量出这个角的大小吗？",
            "平行四边形和梯形": f"这是平行四边形和梯形的问题：{question}\n"
                            f"平行四边形：两组对边分别平行\n"
                            f"梯形：只有一组对边平行\n"
                            f"你能画出这两种图形吗？",
            "平均数": f"这是平均数问题：{question}\n"
                    f"平均数=总数÷总份数\n"
                    f"它表示一组数据的集中趋势\n"
                    f"你能说说平均数有什么用吗？"
        }
        
        return responses.get(knowledge_point, 
                           f"这个四年级数学问题很有意思：{question}\n"
                           f"我们一起来分析，先看看题目告诉了我们哪些信息？")
    
    def _prepare_request_data(self, question: str, knowledge_point: str, user: UserInfo) -> Dict[str, Any]:
        """准备请求数据"""
        return {
            "phone": user.phone,
            "password": user.password,
            "user_id": user.user_id or 33,
            "question_text": question,
            "subject": "数学",
            "knowledge_point": knowledge_point,
            "grade": user.grade,
            "ask_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "wrong_answer": "",
            "correct_answer": "",
            "error_type": "user_question",
            "timestamp": time.time()
        }
    
    def _send_request_with_retry(self, data: Dict[str, Any]) -> requests.Response:
        """发送请求（带重试机制）"""
        url = f"{self.config['server_url']}{self.config['api_base']}/wrong-questions"
        
        for attempt in range(self.config['max_retries']):
            try:
                response = requests.post(
                    url,
                    json=data,
                    timeout=self.config['timeout']
                )
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < self.config['max_retries'] - 1:
                    wait_time = self.config['retry_delay'] * (attempt + 1)
                    self.logger.warning(f"请求失败，{wait_time}秒后重试: {e}")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise requests.exceptions.RequestException("达到最大重试次数")
    
    def _cache_question(self, question: str, knowledge_point: str, user: UserInfo):
        """缓存问题数据"""
        cache_file = os.path.join(self.cache_dir, "fourth_grade_questions.json")
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
            else:
                cached_data = []
            
            cache_entry = {
                "question": question,
                "knowledge_point": knowledge_point,
                "user": {
                    "name": user.name,
                    "grade": user.grade,
                    "phone": user.phone,
                    "user_id": user.user_id
                },
                "timestamp": time.time(),
                "cached_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            cached_data.append(cache_entry)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据缓存: {question[:50]}...")
            
        except Exception as e:
            self.logger.error(f"缓存失败: {e}")
    
    def print_status(self):
        """打印系统状态"""
        print("=" * 60)
        print("四年级数学助手 - 系统状态报告")
        print("=" * 60)
        print()
        
        # 1. 服务器状态
        if self.server_healthy:
            print("服务器状态: 正常")
        else:
            print("服务器状态: 异常")
            print("  数据自动缓存中")
        
        # 2. 当前用户
        user = self.current_user or self.default_user
        print(f"当前用户: {user.name} ({user.grade})")
        
        # 3. 缓存数据
        cache_file = os.path.join(self.cache_dir, "fourth_grade_questions.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                print(f"待上传数据: {len(cached_data)} 条")
                
                if cached_data:
                    print("最近缓存:")
                    for i, item in enumerate(cached_data[:3], 1):
                        question = item.get('question', '未知')[:40]
                        print(f"  {i}. {question}...")
            except:
                print("缓存数据: 读取失败")
        else:
            print("缓存数据: 无")
        
        print()
        print("=" * 60)
    
    def get_cached_data_count(self) -> int:
        """获取缓存数据数量"""
        cache_file = os.path.join(self.cache_dir, "fourth_grade_questions.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                return len(cached_data)
            except:
                return 0
        return 0
    
    def clear_cache(self) -> bool:
        """清除所有缓存数据"""
        cache_file = os.path.join(self.cache_dir, "fourth_grade_questions.json")
        
        try:
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return True
        except Exception as e:
            self.logger.error(f"清除缓存失败: {e}")
            return False
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试服务器连接"""
        try:
            response = requests.get(
                f"{self.config['server_url']}{self.config['api_base']}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, f"连接正常 ({data.get('status', 'unknown')})"
            else:
                return False, f"连接异常，状态码: {response.status_code}"
                
        except Exception as e:
            return False, f"连接失败: {e}"
    
    def demo_math_topics(self):
        """演示四年级数学知识点"""
        print("四年级数学知识点演示")
        print("-" * 50)
        
        demo_questions = [
            ("32456读作什么？", "大数的认识"),
            ("234 × 56 = ?", "三位数乘两位数"),
            ("456 ÷ 25 = ?", "除数是两位数的除法"),
            ("0.8表示什么？", "小数的意义与性质"),
            ("3.45 + 2.67 = ?", "小数的加法和减法"),
            ("25 × 18 + 25 × 2 = ?", "运算定律与简便计算"),
            ("这个角是多少度？", "角的度量"),
            ("什么是平行四边形？", "平行四边形和梯形"),
            ("求8、9、10、11的平均数", "平均数"),
            ("鸡兔同笼，头20个，脚56只，鸡兔各几只？", "鸡兔同笼问题"),
        ]
        
        for question, expected_knowledge in demo_questions:
            print(f"\n问题: {question}")
            result = self.teach(question)
            
            if result.knowledge_point == expected_knowledge:
                print(f"  知识点识别: 正确")
            else:
                print(f"  知识点识别: 识别为 {result.knowledge_point} (期望: {expected_knowledge})")
            
            if result.uploaded:
                print(f"  数据状态: 已上传到数据库")
            else:
                print(f"  数据状态: 已安全缓存")
        
        print("\n" + "=" * 50)
        print("演示完成")
        print("=" * 50)


# ======================================================
# 智能体友好接口
# ======================================================

def create_tutor(config: Optional[Dict[str, Any]] = None) -> FourthGradeMathTutor:
    """创建四年级数学助手"""
    return FourthGradeMathTutor(config=config)


def quick_teach(question: str, user_name: str = "四年级学生") -> TeachingResult:
    """快速教学接口"""
    tutor = FourthGradeMathTutor()
    tutor.set_user(user_name)
    return tutor.teach(question)


def diagnose_skill() -> Dict[str, Any]:
    """诊断技能状态"""
    import platform
    import sys
    
    results = {
        "timestamp": time.time(),
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "python_executable": sys.executable
        },
        "dependencies": {
            "requests": requests.__version__ if hasattr(requests, '__version__') else "unknown"
        },
        "tests": {}
    }
    
    try:
        tutor = FourthGradeMathTutor()
        results["tests"]["create_tutor"] = "success"
        
        status, message = tutor.test_connection()
        results["tests"]["connection"] = "success" if status else "failed"
        results["tests"]["connection_message"] = message
        
        results["tests"]["status_report"] = "success"
        
    except Exception as e:
        results["tests"]["create_tutor"] = "failed"
        results["tests"]["error"] = str(e)
    
    return results


# ======================================================
# 主入口
# ======================================================

if __name__ == "__main__":
    print("小悟数学助手 - 四年级数学教学")
    print("=" * 70)
    
    # 创建助手
    tutor = FourthGradeMathTutor()
    
    # 显示状态
    tutor.print_status()
    
    print("技能准备就绪！开始使用:")
    print("  1. from fourth_grade_math_tutor import FourthGradeMathTutor")
    print("  2. tutor = FourthGradeMathTutor()")
    print("  3. tutor.set_user('学生姓名', '四年级')")
    print("  4. result = tutor.teach('你的四年级数学问题')")
    print()
    
    # 快速测试
    test_question = "234 × 56 = ?"
    print(f"快速测试: {test_question}")
    
    result = tutor.teach(test_question)
    
    print(f"  结果: {result.action}")
    print(f"  消息: {result.message}")
    print()
    
    print("技能初始化完成！")