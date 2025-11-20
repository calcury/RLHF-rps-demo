import json
import os
from datetime import datetime
import random


class RPSController:
    def __init__(self, filename="rps_dataset.json", mode="1"):
        """
        初始化石头剪刀布游戏控制类

        Args:
            filename (str): 数据集文件名称
            mode (str): 使用的运算方法 ["1", "2", "3"]
        """
        self.filename = filename
        self.mode = mode
        self.current_user_choice = None
        self.current_computer_choice = None
        self.current_result = None
        self.timestamp = None
        self.processor = None

        # 初始化数据集文件
        self._init_dataset_file()
        # 加载运算类
        self._load_processor()

    def _init_dataset_file(self):
        """初始化数据集文件"""
        if not os.path.exists(self.filename):
            initial_data = {
                "metadata": {
                    "created_date": datetime.now().isoformat(),
                    "total_games": 0,
                    "computer_wins": 0,
                    "user_wins": 0,
                    "draws": 0,
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "game_records": []
            }
            self._save_dataset(initial_data)
            print(f"已创建新的数据集文件: {self.filename}")

    def _load_processor(self):
        """根据模式加载对应的运算类"""
        try:
            if self.mode == "1":
                # 使用新的简化版预测器
                from solve.solve1 import SimpleRPSPredictor
                self.processor = SimpleRPSPredictor(self.filename)
                print("已加载简化版神经网络预测器 (模式1)")

            else:
                raise ImportError("模式不存在")

        except ImportError as e:
            print(f"加载运算类失败: {e}")
            # 使用随机策略作为备用
            self.processor = RandomPredictor()

    def _load_dataset(self):
        """加载数据集文件"""
        try:
            with open("./dataset"+self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载数据集失败: {e}")
            return self._create_empty_dataset()

    def _create_empty_dataset(self):
        """创建空的数据集结构"""
        return {
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "total_games": 0,
                "computer_wins": 0,
                "user_wins": 0,
                "draws": 0,
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            },
            "game_records": []
        }

    def _save_dataset(self, data):
        """保存数据集到文件"""
        try:
            with open("./dataset"+self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据集失败: {e}")
            return False

    def method1_process_game(self, user_choice):
        """
        方法1：处理游戏逻辑，调用运算类获取电脑选择

        Args:
            user_choice (str): 用户选择，应为 "rock", "scissors", "paper" 之一

        Returns:
            dict: 包含电脑选择和当前结果的字典
        """
        # 验证用户输入
        valid_choices = ["rock", "scissors", "paper"]
        if user_choice not in valid_choices:
            raise ValueError(f"无效的选择: {user_choice}。请使用: {valid_choices}")

        # 设置当前用户选择
        self.current_user_choice = user_choice
        self.timestamp = datetime.now().isoformat()

        # 调用运算类获取电脑选择
        computer_choice = self.processor.compute_choice(user_choice)
        self.current_computer_choice = computer_choice

        # 判断游戏结果
        self.current_result = self._determine_winner(
            user_choice, computer_choice)

        # 返回当前游戏状态
        game_result = {
            "user_choice": user_choice,
            "computer_choice": computer_choice,
            "result": self.current_result,
            "timestamp": self.timestamp
        }

        print(
            f"游戏结果: 用户={user_choice}, 电脑={computer_choice}, 结果={self.current_result}")
        return game_result

    def _determine_winner(self, user_choice, computer_choice):
        """
        判断游戏胜负

        Args:
            user_choice (str): 用户选择
            computer_choice (str): 电脑选择

        Returns:
            str: "user_win", "computer_win", 或 "draw"
        """
        if user_choice == computer_choice:
            return "draw"
        elif (user_choice == "rock" and computer_choice == "scissors") or \
             (user_choice == "scissors" and computer_choice == "paper") or \
             (user_choice == "paper" and computer_choice == "rock"):
            return "user_win"
        else:
            return "computer_win"

    def method2_save_to_dataset(self):
        """
        方法2：将当前游戏记录保存到数据集

        Returns:
            bool: 保存是否成功
        """
        if not all([self.current_user_choice, self.current_computer_choice, self.current_result]):
            print("没有完整的游戏记录可保存")
            return False

        # 加载现有数据
        data = self._load_dataset()

        # 创建新记录
        new_record = {
            "user_choice": self.current_user_choice,
            "computer_choice": self.current_computer_choice,
            "result": self.current_result,
            "timestamp": self.timestamp
        }

        # 添加到记录列表
        data["game_records"].append(new_record)

        # 更新元数据
        data["metadata"]["total_games"] += 1
        if self.current_result == "computer_win":
            data["metadata"]["computer_wins"] += 1
        elif self.current_result == "user_win":
            data["metadata"]["user_wins"] += 1
        else:
            data["metadata"]["draws"] += 1

        data["metadata"]["last_updated"] = datetime.now().isoformat()

        # 保存数据
        success = self._save_dataset(data)

        if success:
            print(f"游戏记录已保存到 {self.filename}")
            # 通知运算类更新（如果有更新方法）
            if hasattr(self.processor, 'update_with_new_data'):
                self.processor.update_with_new_data()
                print("已通知预测器更新模型")

        return success

    def method3_get_statistics(self):
        """
        方法3：获取游戏统计数据

        Returns:
            dict: 包含各种统计数据的字典
        """
        data = self._load_dataset()
        metadata = data["metadata"]
        total_games = metadata["total_games"]
        computer_wins = metadata["computer_wins"]
        user_wins = metadata["user_wins"]
        draws = metadata["draws"]

        # 计算胜率
        computer_win_rate = (computer_wins / total_games *
                             100) if total_games > 0 else 0
        user_win_rate = (user_wins / total_games *
                         100) if total_games > 0 else 0
        draw_rate = (draws / total_games * 100) if total_games > 0 else 0

        # 获取处理器信息
        processor_info = "未知"
        if hasattr(self.processor, 'get_model_info'):
            processor_info = self.processor.get_model_info()
        elif hasattr(self.processor, '__class__'):
            processor_info = self.processor.__class__.__name__

        statistics = {
            "total_games": total_games,
            "computer_wins": computer_wins,
            "user_wins": user_wins,
            "draws": draws,
            "computer_win_rate": round(computer_win_rate, 2),
            "user_win_rate": round(user_win_rate, 2),
            "draw_rate": round(draw_rate, 2),
            "dataset_filename": self.filename,
            "processor_mode": self.mode,
            "processor_type": processor_info,
            "created_date": metadata["created_date"],
            "last_updated": metadata["last_updated"]
        }

        return statistics

    def change_mode(self, new_mode):
        """
        更改运算模式

        Args:
            new_mode (str): 新的运算模式

        Returns:
            bool: 是否成功更改模式
        """
        if new_mode not in ["1", "2", "3"]:
            print(f"无效的模式: {new_mode}")
            return False

        self.mode = new_mode
        self._load_processor()
        print(f"已切换到模式 {new_mode}")
        return True

    def get_processor_info(self):
        """
        获取当前处理器的详细信息

        Returns:
            dict: 处理器信息
        """
        info = {
            "mode": self.mode,
            "processor_type": self.processor.__class__.__name__ if self.processor else "None"
        }

        # 尝试获取更详细的信息
        if hasattr(self.processor, 'get_model_info'):
            try:
                model_info = self.processor.get_model_info()
                if isinstance(model_info, dict):
                    info.update(model_info)
                else:
                    info["model_details"] = model_info
            except Exception as e:
                info["model_details"] = f"获取模型信息失败: {e}"

        # 获取最近序列（如果可用）
        if hasattr(self.processor, 'get_recent_sequence'):
            try:
                recent_seq = self.processor.get_recent_sequence()
                info["recent_sequence"] = recent_seq
                info["sequence_length"] = len(recent_seq)
            except Exception as e:
                info["recent_sequence"] = f"获取序列失败: {e}"

        return info


class RandomPredictor:
    """随机策略预测器（模式3）"""

    def __init__(self, data_filename=None):
        self.actions = ["rock", "scissors", "paper"]

    def compute_choice(self, user_choice):
        """随机选择"""
        choice = random.choice(self.actions)
        print(f"随机策略选择: {choice}")
        return choice


# 使用示例
if __name__ == "__main__":
    # 创建控制类实例
    controller = RPSController(filename="rps_data.json", mode="1")

    # 测试不同模式
    print("\n=== 测试模式1 ===")
    for i in range(15):
        user_choice = random.choice(["rock", "scissors", "paper"])

        # 方法1: 处理游戏
        result = controller.method1_process_game(user_choice)

        # 方法2: 保存记录
        controller.method2_save_to_dataset()

        # 每5轮显示统计
        if (i + 1) % 5 == 0:
            stats = controller.method3_get_statistics()
            print(
                f"统计: 总游戏={stats['total_games']}, 电脑胜率={stats['computer_win_rate']}%")

    # 显示处理器信息
    processor_info = controller.get_processor_info()
    print(f"\n处理器信息: {processor_info}")

    # 测试切换模式
    print("\n=== 切换到模式3 ===")
    controller.change_mode("3")

    for i in range(5):
        user_choice = random.choice(["rock", "scissors", "paper"])
        result = controller.method1_process_game(user_choice)
        controller.method2_save_to_dataset()

    # 最终统计
    stats = controller.method3_get_statistics()
    print(f"\n最终统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
