import json
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import os


class SimpleNeuralNetwork(nn.Module):
    """简单的神经网络分类器"""

    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNeuralNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.network(x)


class SimpleRPSPredictor:
    def __init__(self, data_filename="rps_dataset.json"):
        """
        简化版石头剪刀布预测器
        只使用前10个数据做循环预测

        Args:
            data_filename (str): 数据集文件名称
        """
        self.data_filename = data_filename
        self.actions = ["rock", "scissors", "paper"]
        self.action_to_idx = {action: idx for idx,
                              action in enumerate(self.actions)}
        self.idx_to_action = {idx: action for action,
                              idx in self.action_to_idx.items()}

        self.winning_actions = {
            "rock": "paper",      # 布赢石头
            "scissors": "rock",   # 石头赢剪刀
            "paper": "scissors"   # 剪刀赢布
        }

        # 神经网络参数
        self.input_size = 10  # 使用前10个动作的one-hot编码
        self.hidden_size = 32
        self.output_size = 3  # 3个类别

        # 数据存储
        self.recent_actions = deque(maxlen=10)  # 只保留最近10个动作
        self.total_games = 0

        # 神经网络模型
        self.model = None
        self.optimizer = None
        self.criterion = nn.CrossEntropyLoss()

        # 设备
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        # 加载历史数据
        self._load_historical_data()

    def _load_historical_data(self):
        """加载历史数据"""
        if not os.path.exists(self.data_filename):
            print("数据集文件不存在，等待数据积累")
            return

        try:
            with open("./dataset"+self.data_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            game_records = data.get("game_records", [])
            self.total_games = len(game_records)

            # 提取用户选择历史
            for record in game_records:
                user_choice = record.get("user_choice")
                if user_choice in self.actions:
                    self.recent_actions.append(user_choice)

            print(f"加载了 {len(self.recent_actions)} 条历史用户选择")

            # 如果数据足够，初始化模型
            if len(self.recent_actions) >= 10:
                self._initialize_model()
                self._train_model()

        except Exception as e:
            print(f"加载历史数据失败: {e}")

    def _initialize_model(self):
        """初始化神经网络模型"""
        self.model = SimpleNeuralNetwork(
            self.input_size, self.hidden_size, self.output_size)
        self.model.to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

    def _action_to_one_hot(self, action):
        """将动作转换为one-hot编码"""
        one_hot = [0, 0, 0]
        one_hot[self.action_to_idx[action]] = 1
        return one_hot

    def _prepare_training_data(self):
        """准备训练数据"""
        if len(self.recent_actions) < 11:  # 需要至少11个数据来创建10->1的映射
            return [], []

        X = []  # 输入：前10个动作的one-hot拼接
        y = []  # 输出：第11个动作的索引

        # 使用滑动窗口创建训练数据
        actions_list = list(self.recent_actions)
        for i in range(10, len(actions_list)):
            # 取前10个动作作为输入
            input_sequence = actions_list[i-10:i]
            # 第11个动作作为目标
            target_action = actions_list[i]

            # 将输入序列转换为one-hot编码
            input_features = []
            for action in input_sequence:
                input_features.extend(self._action_to_one_hot(action))

            X.append(input_features)
            y.append(self.action_to_idx[target_action])

        return X, y

    def _train_model(self):
        """训练模型"""
        X, y = self._prepare_training_data()

        if len(X) < 1:
            print("训练数据不足")
            return

        print(f"开始训练模型，使用 {len(X)} 个样本...")

        # 转换为张量
        X_tensor = torch.FloatTensor(X).to(self.device)
        y_tensor = torch.LongTensor(y).to(self.device)

        # 训练循环
        self.model.train()
        for epoch in range(100):
            # 前向传播
            outputs = self.model(X_tensor)
            loss = self.criterion(outputs, y_tensor)

            # 反向传播
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            if epoch % 20 == 0:
                print(f"训练轮次 {epoch}, 损失: {loss.item():.4f}")

        print("模型训练完成")

    def compute_choice(self, user_choice):
        """
        基于前10个数据预测计算电脑的选择

        Args:
            user_choice (str): 用户当前的选择

        Returns:
            str: 电脑的选择
        """
        # 更新最近动作列表
        self.recent_actions.append(user_choice)
        self.total_games += 1

        # 策略1: 数据不足10个时随机选择
        if len(self.recent_actions) < 10:
            computer_choice = random.choice(self.actions)
            print(f"数据不足 {len(self.recent_actions)}/10，随机选择: {computer_choice}")
            return computer_choice

        # 策略2: 使用模型预测
        try:
            # 获取最近10个动作
            recent_10 = list(self.recent_actions)[-10:]

            # 准备输入特征
            input_features = []
            for action in recent_10:
                input_features.extend(self._action_to_one_hot(action))

            # 使用模型预测
            if self.model is not None:
                self.model.eval()
                with torch.no_grad():
                    features_tensor = torch.FloatTensor(
                        input_features).unsqueeze(0).to(self.device)
                    outputs = self.model(features_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    predicted_idx = torch.argmax(outputs, dim=1).item()
                    predicted_action = self.idx_to_action[predicted_idx]

                # 获取预测概率
                probs = probabilities[0].cpu().numpy()
                prob_dict = {self.actions[i]: float(
                    probs[i]) for i in range(3)}

                print(f"模型预测用户下一动作: {predicted_action}")
                print(f"预测概率: {prob_dict}")

                # 选择能赢预测动作的动作
                computer_choice = self.winning_actions[predicted_action]
                print(f"针对性选择: {computer_choice}")
                return computer_choice

        except Exception as e:
            print(f"模型预测失败: {e}")

        # 备用策略: 随机选择
        computer_choice = random.choice(self.actions)
        print(f"备用随机选择: {computer_choice}")
        return computer_choice

    def update_with_new_data(self):
        """当有新数据时重新训练模型"""
        if len(self.recent_actions) >= 11:  # 有足够数据时才训练
            print("检测到新数据，重新训练模型...")
            self._train_model()

    def get_recent_sequence(self):
        """获取最近的动作序列"""
        return list(self.recent_actions)
