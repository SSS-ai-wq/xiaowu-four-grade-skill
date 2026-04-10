#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
四年级数学苏格拉底式教学引擎
针对四年级特点：大数、小数、运算定律、几何图形
"""

import random
import json
from datetime import datetime

class SocraticTeachingEngine:
    def __init__(self):
        self.current_hint_level = "L1"  # 当前提示级别
        self.student_progress = {}      # 学生学习进度
        self.question_types = self._load_question_types()
        self.teaching_strategies = self._load_teaching_strategies()
        self.grade_level = "四年级"
    
    def _load_question_types(self):
        """加载四年级题目类型定义"""
        return {
            "大数类": [
                "亿以内数读写", "亿以上数读写", "数的大小比较", 
                "整万/整亿数改写", "近似数求法"
            ],
            "小数类": [
                "小数意义", "小数读写", "小数性质", "小数点移动",
                "小数大小比较", "小数近似数", "单位换算"
            ],
            "计算类": [
                "三位数乘两位数", "除数是两位数除法", "小数加减法",
                "四则混合运算", "简便计算（运算定律）"
            ],
            "几何类": [
                "角的度量", "直线射线线段", "角分类", "平行与垂直",
                "平行四边形特征", "梯形特征", "三角形特性",
                "图形运动", "观察物体"
            ],
            "统计类": [
                "条形统计图", "平均数计算", "复式条形统计图",
                "数据分析"
            ],
            "应用类": [
                "归一问题", "归总问题", "行程问题", "购物问题",
                "几何应用题", "优化问题", "鸡兔同笼"
            ],
            "思维类": [
                "运算定律应用", "逻辑推理", "策略选择", "最优方案"
            ]
        }
    
    def _load_teaching_strategies(self):
        """加载四年级教学策略"""
        return {
            "四年级特色引导": {
                "大数问题": [
                    "先分级，从右向左每四位一级",
                    "亿级、万级、个级分别读写",
                    "求近似数看省略部分的最高位"
                ],
                "小数问题": [
                    "理解小数意义：十分之几、百分之几",
                    "小数点向右移动扩大，向左移动缩小",
                    "单位换算：大单位化小单位乘进率，小单位化大单位除以进率"
                ],
                "运算定律问题": [
                    "识别可以简便计算的形式",
                    "乘法分配律：a×(b+c)=a×b+a×c",
                    "结合律与分配律的区别"
                ],
                "几何问题": [
                    "角的分类：锐角(<90°)、直角(=90°)、钝角(>90°且<180°)、平角(=180°)、周角(=360°)",
                    "平行：同一平面内不相交的两条直线",
                    "垂直：两条直线相交成直角"
                ],
                "鸡兔同笼问题": [
                    "假设法：假设全是鸡/兔",
                    "计算假设腿数与实际腿数的差",
                    "调整假设求出正确答案"
                ]
            },
            "提问层级": {
                "L1": {
                    "目标": "信息提取",
                    "问题": [
                        "题目中有哪些数字？是什么数？",
                        "要求我们求什么？",
                        "单位是什么？"
                    ],
                    "话术": "我们先看看题目给了什么信息"
                },
                "L2": {
                    "目标": "关系建立", 
                    "问题": [
                        "这些数字之间有什么关系？",
                        "要先求什么才能求出答案？",
                        "这题和哪种题型类似？"
                    ],
                    "话术": "想想这些信息怎么联系起来"
                },
                "L3": {
                    "target": "方法选择",
                    "问题": [
                        "可以用什么方法？",
                        "用运算定律能简便计算吗？",
                        "要分几步计算？"
                    ],
                    "话术": "选择合适的方法来解决"
                },
                "L4": {
                    "目标": "过程监控",
                    "问题": [
                        "这一步算对了吗？",
                        "单位需要统一吗？",
                        "需要验算吗？"
                    ],
                    "话术": "检查一下计算过程"
                },
                "L5": {
                    "目标": "知识迁移",
                    "问题": [
                        "如果条件变化会怎样？",
                        "这题的方法还能用在什么地方？",
                        "还有其他解法吗？"
                    ],
                    "话术": "想想这个方法还能解决什么问题"
                }
            },
            "四年级常见错误干预": {
                "大数读写错误": [
                    "从右向左每四位一级分级",
                    "亿级、万级、个级分别读写",
                    "注意每级末尾的0不读"
                ],
                "小数点移动错误": [
                    "小数点向右移动扩大，向左移动缩小",
                    "移动一位，扩大或缩小10倍",
                    "移动两位，扩大或缩小100倍"
                ],
                "运算定律用错": [
                    "分配律：a×(b+c)=a×b+a×c",
                    "结合律：(a×b)×c=a×(b×c)",
                    "区分：分配律是乘加关系，结合律是连乘关系"
                ],
                "几何概念混淆": [
                    "锐角<90°，直角=90°，钝角>90°且<180°",
                    "平行：同一平面内不相交",
                    "垂直：相交成直角"
                ],
                "鸡兔同笼困惑": [
                    "假设全是鸡，计算腿数",
                    "比较假设腿数与实际腿数",
                    "每把一只鸡换成兔，增加2条腿"
                ]
            }
        }
    
    def analyze_question(self, question_text):
        """分析四年级题目类型和结构"""
        analysis = {
            "question_type": "未知",
            "difficulty": "基础",
            "keywords": [],
            "numbers": [],
            "units": []
        }
        
        # 提取数字
        import re
        numbers = re.findall(r'\d+\.?\d*', question_text)
        analysis["numbers"] = numbers
        
        # 识别题目类型
        text_lower = question_text.lower()
        
        # 判断是否是大数题
        if any(word in text_lower for word in ["亿", "万", "千万", "百万", "分级", "四舍五入", "近似数"]):
            analysis["question_type"] = "大数类"
            if "读写" in text_lower or "写作" in text_lower or "读作" in text_lower:
                analysis["question_type"] = "大数类 - 读写"
            elif "近似" in text_lower or "四舍五入" in text_lower:
                analysis["question_type"] = "大数类 - 近似数"
        
        # 判断是否是小数题
        elif any(word in text_lower for word in ["小数", ".点", "小数点", "扩大", "缩小", "0."]):
            analysis["question_type"] = "小数类"
            if "小数点" in text_lower and ("移动" in text_lower or "扩大" in text_lower or "缩小" in text_lower):
                analysis["question_type"] = "小数类 - 小数点移动"
            elif "性质" in text_lower:
                analysis["question_type"] = "小数类 - 小数性质"
        
        # 判断是否是运算定律题
        elif any(word in text_lower for word in ["简便", "运算定律", "分配律", "结合律", "交换律", "简便计算"]):
            analysis["question_type"] = "计算类 - 简便计算"
        
        # 判断是否是几何题
        elif any(word in text_lower for word in ["角", "度", "平行", "垂直", "三角形", "四边形", "梯形", "对称", "平移"]):
            analysis["question_type"] = "几何类"
            if "角" in text_lower:
                analysis["question_type"] = "几何类 - 角度"
            elif "平行" in text_lower or "垂直" in text_lower:
                analysis["question_type"] = "几何类 - 位置关系"
            elif "三角形" in text_lower:
                analysis["question_type"] = "几何类 - 三角形"
        
        # 判断是否是鸡兔同笼
        elif any(word in text_lower for word in ["鸡", "兔", "同笼", "头", "腿", "脚"]):
            analysis["question_type"] = "应用类 - 鸡兔同笼"
        
        # 判断是否是优化问题
        elif any(word in text_lower for word in ["沏茶", "烙饼", "田忌赛马", "最少时间", "合理安排"]):
            analysis["question_type"] = "应用类 - 优化问题"
        
        # 判断是否是平均数问题
        elif "平均" in text_lower and ("数" in text_lower or "成绩" in text_lower or "身高" in text_lower):
            analysis["question_type"] = "统计类 - 平均数"
        
        # 提取单位
        unit_keywords = ["亿", "万", "千", "百", "十", "个", "米", "厘米", "千米", "吨", "千克", "克", "时", "分", "秒", "元", "角", "分", "度"]
        for unit in unit_keywords:
            if unit in text_lower:
                analysis["units"].append(unit)
        
        # 提取关键词
        keywords = ["一共", "还剩", "每个", "每", "平均", "倍", "比", "多", "少", "原来", "又", "再", "同时", "相向", "相遇"]
        for word in keywords:
            if word in text_lower:
                analysis["keywords"].append(word)
        
        # 判断难度
        if len(numbers) > 3 or "综合" in text_lower or "多种" in text_lower:
            analysis["difficulty"] = "较难"
        elif len(numbers) > 2 or "两步" in text_lower or "先" in text_lower and "再" in text_lower:
            analysis["difficulty"] = "中等"
        
        return analysis
    
    def generate_hint(self, question_analysis, student_response=None):
        """根据当前情况和提示级别生成提示（四年级专用）"""
        hint_level = self.current_hint_level
        q_type = question_analysis["question_type"]
        
        # L1: 信息提取
        if hint_level == "L1":
            if "大数" in q_type:
                return "我们先看看这是多大的数？怎么分级？"
            elif "小数" in q_type:
                return "题目里的小数是多少？表示什么意思？"
            elif "运算定律" in q_type:
                return "看看这个计算能不能用简便方法？"
            elif "鸡兔同笼" in q_type:
                return "题目告诉我们什么信息？要求什么？"
            else:
                return "我们先看看题目说了什么"
        
        # L2: 关系建立
        elif hint_level == "L2":
            if "大数读写" in q_type:
                return "怎么分级读写大数？"
            elif "小数点移动" in q_type:
                return "小数点移动有什么规律？"
            elif "分配律" in q_type:
                return "乘法分配律怎么用？"
            elif "鸡兔同笼" in q_type:
                return "假设全是鸡会怎样？"
            else:
                return "这些信息之间有什么关系？"
        
        # L3: 方法选择
        elif hint_level == "L3":
            if "大数读写" in q_type:
                return "从右向左每四位一级，分别读写"
            elif "小数点移动" in q_type:
                return "小数点向右移动扩大，向左移动缩小"
            elif "分配律" in q_type:
                return "用乘法分配律：a×(b+c)=a×b+a×c"
            elif "鸡兔同笼" in q_type:
                return "假设全是鸡，计算腿数差"
            else:
                return "想想用什么方法计算"
        
        # L4: 完整思路
        else:
            return self._generate_complete_solution(question_analysis)
    
    def _generate_complete_solution(self, question_analysis):
        """生成完整解题思路（四年级专用）"""
        q_type = question_analysis["question_type"]
        
        if "大数读写" in q_type:
            return "大数读写：从右向左每四位一级，先分级再读写"
        elif "小数点移动" in q_type:
            return "小数点移动：向右移动扩大，向左移动缩小，移动一位变10倍"
        elif "分配律" in q_type:
            return "乘法分配律：a×(b+c)=a×b+a×c，分别相乘再相加"
        elif "鸡兔同笼" in q_type:
            return "鸡兔同笼：假设全是鸡，算腿数差，每差2条腿换一只兔"
        elif "平均数" in q_type:
            return "平均数=总和÷个数，先求总和再除以个数"
        
        return "我们一步一步来解决这个问题"
    
    def evaluate_response(self, question_analysis, student_response, correct_answer):
        """评估学生回答并决定下一步教学策略（四年级专用）"""
        evaluation = {
            "is_correct": False,
            "error_type": None,
            "next_hint_level": self.current_hint_level,
            "teaching_action": "continue",
            "encouragement": ""
        }
        
        # 简化答案比较
        try:
            # 去除空格和单位比较
            student_clean = str(student_response).strip().replace(" ", "")
            correct_clean = str(correct_answer).strip().replace(" ", "")
            
            # 检查是否包含数字
            import re
            student_nums = re.findall(r'\d+\.?\d*', student_clean)
            correct_nums = re.findall(r'\d+\.?\d*', correct_clean)
            
            if student_nums and correct_nums and student_nums[0] == correct_nums[0]:
                evaluation["is_correct"] = True
                evaluation["encouragement"] = self._generate_encouragement(True)
                evaluation["teaching_action"] = "reinforce_and_advance"
                evaluation["next_hint_level"] = "L1"  # 重置提示级别
            else:
                evaluation["is_correct"] = False
                evaluation["error_type"] = self._identify_error_type(question_analysis)
                evaluation["encouragement"] = self._generate_encouragement(False)
                
                # 提高提示级别
                hint_levels = ["L1", "L2", "L3", "L4"]
                current_index = hint_levels.index(self.current_hint_level)
                if current_index < len(hint_levels) - 1:
                    evaluation["next_hint_level"] = hint_levels[current_index + 1]
                else:
                    evaluation["next_hint_level"] = "L4"
                
                evaluation["teaching_action"] = "provide_more_guidance"
        
        except Exception as e:
            evaluation["is_correct"] = False
            evaluation["error_type"] = "理解错误"
            evaluation["encouragement"] = "没关系，我们慢慢来"
            evaluation["teaching_action"] = "clarify_question"
        
        return evaluation
    
    def _identify_error_type(self, question_analysis):
        """识别四年级常见错误类型"""
        q_type = question_analysis["question_type"]
        
        if "大数" in q_type:
            return "大数读写错误"
        elif "小数" in q_type:
            if "移动" in q_type:
                return "小数点移动错误"
            else:
                return "小数概念错误"
        elif "运算定律" in q_type:
            return "运算定律应用错误"
        elif "几何" in q_type:
            if "角" in q_type:
                return "角度概念错误"
            elif "平行" in q_type or "垂直" in q_type:
                return "位置关系错误"
        elif "鸡兔同笼" in q_type:
            return "鸡兔同笼方法错误"
        elif "平均数" in q_type:
            return "平均数计算错误"
        
        return "计算错误"
    
    def _generate_encouragement(self, is_correct):
        """生成鼓励话语（四年级专用）"""
        if is_correct:
            encouragements = [
                "太棒了！完全正确！",
                "真厉害！思路很清晰！",
                "非常好！你掌握得很好！",
                "完全正确！继续加油！"
            ]
        else:
            encouragements = [
                "没关系，我们再来一次！",
                "差一点就对了，再想想！",
                "这是个很好的尝试！",
                "四年级数学有点挑战，我们一起克服！"
            ]
        
        return random.choice(encouragements)
    
    def generate_follow_up_question(self, question_analysis, was_correct):
        """生成跟进问题（四年级专用）"""
        q_type = question_analysis["question_type"]
        
        if was_correct:
            # 如果正确，提供变式题
            if "大数读写" in q_type:
                return "如果把这个数改写成以'万'为单位的数，是多少？"
            elif "小数点移动" in q_type:
                return "如果向左移动两位，会变成多少？"
            elif "分配律" in q_type:
                return "用分配律计算：99×45"
            elif "鸡兔同笼" in q_type:
                return "如果头数不变，腿数变成34条，鸡兔各多少？"
            else:
                return "这道题你已经掌握了，试试稍微难一点的？"
        else:
            # 如果错误，提供更简单的类似题
            if "大数读写" in q_type:
                return "我们先从简单的开始，300000读作什么？"
            elif "小数点移动" in q_type:
                return "我们先试试简单的，0.5扩大到10倍是多少？"
            elif "分配律" in q_type:
                return "我们先理解一下，25×(4+8)怎么用分配律？"
            elif "鸡兔同笼" in q_type:
                return "我们先从简单的开始，鸡兔同笼，头5个，腿14条，鸡兔各多少？"
            else:
                return "我们换个简单点的题目试试？"
    
    def get_grade_specific_advice(self, question_analysis):
        """获取四年级专项建议"""
        q_type = question_analysis["question_type"]
        
        advice = {
            "大数读写": "大数读写：从右向左每四位一级，先分级再读写",
            "小数点移动": "小数点移动：向右移动扩大，向左移动缩小",
            "乘法分配律": "乘法分配律：a×(b+c)=a×b+a×c",
            "角的度量": "角的分类：锐角<90°，直角=90°，钝角>90°且<180°，平角=180°，周角=360°",
            "鸡兔同笼": "鸡兔同笼：假设全是鸡，算腿数差，每差2条腿换一只兔",
            "平均数": "平均数=总和÷个数"
        }
        
        for key, value in advice.items():
            if key in q_type:
                return value
        
        return "认真审题，仔细计算，做完要检查"

# 测试函数
def test_grade4_teaching_engine():
    """测试四年级教学引擎"""
    engine = SocraticTeachingEngine()
    
    print(f"测试{engine.grade_level}教学引擎...")
    print("="*60)
    
    # 测试四年级典型题目分析
    grade4_questions = [
        ("大数读写", "五亿零三百万写作：______"),
        ("小数点移动", "把0.05扩大到原数的100倍是：______"),
        ("运算定律", "用简便方法计算：25×32"),
        ("几何问题", "一个等腰三角形，底角是40°，顶角是多少度？"),
        ("鸡兔同笼", "鸡兔同笼，头10个，腿32条，鸡兔各几只？"),
        ("平均数", "小明五次测验成绩：90、85、88、92、95，平均成绩是多少？")
    ]
    
    for name, question in grade4_questions:
        print(f"\n{name}: {question}")
        analysis = engine.analyze_question(question)
        print(f"   题目类型: {analysis.get('question_type', '未知')}")
        print(f"   难度: {analysis.get('difficulty', '未知')}")
        
        # 测试引导提示
        engine.current_hint_level = "L2"
        hint = engine.generate_hint(analysis)
        print(f"   L2提示: {hint}")
    
    print("\n" + "="*60)
    
    # 测试回答评估
    print("测试回答评估（四年级典型题目）...")
    
    # 测试大数问题
    big_number_question = "五亿零三百万写作：______"
    analysis = engine.analyze_question(big_number_question)
    print(f"\n题目: {big_number_question}")
    print(f"正确答案: 503000000")
    
    test_answers = [
        ("503000000", "完全正确"),
        ("5003000", "大数读写错误"),
        ("50300000", "分级错误")
    ]
    
    for answer, error_type in test_answers:
        evaluation = engine.evaluate_response(analysis, answer, "503000000")
        print(f"   学生答案: {answer} → 正确: {evaluation['is_correct']}, 错误类型: {evaluation.get('error_type', '未知')}")
    
    print("\n" + "="*60)
    print("四年级教学引擎测试完成！")

if __name__ == "__main__":
    test_grade4_teaching_engine()