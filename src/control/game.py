import pygame
import sys
import random
import os
from pygame.locals import *


class RPSGame:
    def __init__(self, width=800, height=600):
        # 初始化Pygame
        pygame.init()

        # 游戏窗口设置
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("石头剪刀布游戏")

        # 颜色定义
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 120, 255)
        self.GRAY = (200, 200, 200)

        # 游戏状态
        self.user_choice = None      # 用户选择
        self.computer_choice = None  # 电脑选择
        self.result = None           # 游戏结果
        self.game_started = False    # 游戏是否开始

        # 加载图片资源
        self.load_images()

        # 初始化按钮
        self.init_buttons()

        # 字体
        self.font = pygame.font.SysFont('simHei', 36)
        self.small_font = pygame.font.SysFont('simHei', 28)

    def load_images(self):
        """加载游戏所需的图片资源（实际图片版）"""
        # 创建图片目录（如果不存在）
        if not os.path.exists('images'):
            os.makedirs('images')
            print("⚠️ images 文件夹不存在，已自动创建。请把 rock.png / scissors.png / paper.png 放进去！")

        try:
            # 加载用户选择按钮图片（120×120）
            self.rock_img = pygame.image.load(
                "images/rock.png").convert_alpha()
            self.rock_img = pygame.transform.scale(self.rock_img, (120, 120))

            self.scissors_img = pygame.image.load(
                "images/scissors.png").convert_alpha()
            self.scissors_img = pygame.transform.scale(
                self.scissors_img, (120, 120))

            self.paper_img = pygame.image.load(
                "images/paper.png").convert_alpha()
            self.paper_img = pygame.transform.scale(self.paper_img, (120, 120))

            # 电脑显示用大图（180×180）
            self.rock_img_large = pygame.transform.scale(
                self.rock_img, (180, 180))
            self.scissors_img_large = pygame.transform.scale(
                self.scissors_img, (180, 180))
            self.paper_img_large = pygame.transform.scale(
                self.paper_img, (180, 180))

            print("✅ 图片资源加载成功！")

        except Exception as e:
            print(f"❌ 图片加载失败: {e}")
            print("⚠️ 将使用备用绘制图形...")
            self.create_fallback_images()

    def init_buttons(self):
        """初始化用户选择按钮"""
        # 用户选择按钮位置和区域
        self.rock_button = pygame.Rect(150, 450, 120, 120)
        self.scissors_button = pygame.Rect(340, 450, 120, 120)
        self.paper_button = pygame.Rect(530, 450, 120, 120)

        # 再来一次按钮
        self.play_again_button = pygame.Rect(350, 400, 100, 40)

    def get_user_input(self):
        """方法1：获取用户输入（处理按钮点击）"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                # 检查用户点击了哪个按钮
                if self.rock_button.collidepoint(event.pos):
                    self.user_choice = "rock"
                    self.game_started = True
                    return "rock"
                elif self.scissors_button.collidepoint(event.pos):
                    self.user_choice = "scissors"
                    self.game_started = True
                    return "scissors"
                elif self.paper_button.collidepoint(event.pos):
                    self.user_choice = "paper"
                    self.game_started = True
                    return "paper"
                elif self.play_again_button.collidepoint(event.pos) and self.result:
                    # 重新开始游戏
                    self.user_choice = None
                    self.computer_choice = None
                    self.result = None
                    self.game_started = False

        return None

    def get_computer_choice(self):
        """方法2：获取电脑选择并显示结果"""
        if self.user_choice and not self.computer_choice:
            # 电脑随机选择
            choices = ["rock", "scissors", "paper"]
            self.computer_choice = random.choice(choices)

            # 判断胜负
            self.determine_winner()

        return self.computer_choice, self.result

    def determine_winner(self):
        """判断游戏胜负"""
        if self.user_choice == self.computer_choice:
            self.result = "draw"  # 平局
        elif (self.user_choice == "rock" and self.computer_choice == "scissors") or \
             (self.user_choice == "scissors" and self.computer_choice == "paper") or \
             (self.user_choice == "paper" and self.computer_choice == "rock"):
            self.result = "user"  # 用户赢
        else:
            self.result = "computer"  # 电脑赢

    def draw_interface(self):
        """绘制游戏界面"""
        # 清空屏幕
        self.screen.fill(self.WHITE)

        # 绘制标题
        title = self.font.render("石头剪刀布游戏", True, self.BLACK)
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 20))

        if not self.game_started:
            # 显示等待用户选择的界面
            instruction = self.small_font.render("请选择你的出拳:", True, self.BLACK)
            self.screen.blit(instruction, (self.width//2 -
                             instruction.get_width()//2, 80))

            # 绘制用户选择按钮
            self.draw_buttons()

        else:
            # 显示游戏进行中的界面
            self.draw_game_interface()

        # 更新显示
        pygame.display.flip()

    def draw_buttons(self):
        """绘制用户选择按钮"""
        # 绘制石头按钮
        pygame.draw.rect(self.screen, self.GRAY,
                         self.rock_button, border_radius=10)
        pygame.draw.rect(self.screen, self.BLUE,
                         self.rock_button, 3, border_radius=10)
        self.screen.blit(self.rock_img, self.rock_button)
        rock_text = self.small_font.render("石头", True, self.BLACK)
        self.screen.blit(rock_text, (self.rock_button.centerx - rock_text.get_width()//2,
                                     self.rock_button.bottom + 5))

        # 绘制剪刀按钮
        pygame.draw.rect(self.screen, self.GRAY,
                         self.scissors_button, border_radius=10)
        pygame.draw.rect(self.screen, self.RED,
                         self.scissors_button, 3, border_radius=10)
        self.screen.blit(self.scissors_img, self.scissors_button)
        scissors_text = self.small_font.render("剪刀", True, self.BLACK)
        self.screen.blit(scissors_text, (self.scissors_button.centerx - scissors_text.get_width()//2,
                                         self.scissors_button.bottom + 5))

        # 绘制布按钮
        pygame.draw.rect(self.screen, self.GRAY,
                         self.paper_button, border_radius=10)
        pygame.draw.rect(self.screen, self.GREEN,
                         self.paper_button, 3, border_radius=10)
        self.screen.blit(self.paper_img, self.paper_button)
        paper_text = self.small_font.render("布", True, self.BLACK)
        self.screen.blit(paper_text, (self.paper_button.centerx - paper_text.get_width()//2,
                                      self.paper_button.bottom + 5))

    def draw_game_interface(self):
        """绘制游戏进行中的界面"""
        # 显示用户选择
        user_text = self.small_font.render("你的选择:", True, self.BLUE)
        self.screen.blit(user_text, (150, 100))

        if self.user_choice == "rock":
            self.screen.blit(self.rock_img_large, (130, 130))
        elif self.user_choice == "scissors":
            self.screen.blit(self.scissors_img_large, (130, 130))
        elif self.user_choice == "paper":
            self.screen.blit(self.paper_img_large, (130, 130))

        # 显示电脑选择
        computer_text = self.small_font.render("电脑选择:", True, self.RED)
        self.screen.blit(computer_text, (500, 100))

        if self.computer_choice == "rock":
            self.screen.blit(self.rock_img_large, (480, 130))
        elif self.computer_choice == "scissors":
            self.screen.blit(self.scissors_img_large, (480, 130))
        elif self.computer_choice == "paper":
            self.screen.blit(self.paper_img_large, (480, 130))

        # 显示结果
        if self.result:
            result_y = 350
            if self.result == "user":
                result_text = self.font.render("你赢了!", True, self.GREEN)
                self.screen.blit(
                    result_text, (self.width//2 - result_text.get_width()//2, result_y))
            elif self.result == "computer":
                result_text = self.font.render("电脑赢了!", True, self.RED)
                self.screen.blit(
                    result_text, (self.width//2 - result_text.get_width()//2, result_y))
            else:
                result_text = self.font.render("平局!", True, self.BLUE)
                self.screen.blit(
                    result_text, (self.width//2 - result_text.get_width()//2, result_y))

            # 绘制再来一次按钮
            pygame.draw.rect(self.screen, self.GRAY,
                             self.play_again_button, border_radius=5)
            pygame.draw.rect(self.screen, self.BLACK,
                             self.play_again_button, 2, border_radius=5)
            again_text = self.small_font.render("再来一次", True, self.BLACK)
            self.screen.blit(again_text, (self.play_again_button.centerx - again_text.get_width()//2,
                                          self.play_again_button.centery - again_text.get_height()//2))
        else:
            # 显示等待电脑选择
            waiting_text = self.font.render("电脑思考中...", True, self.BLACK)
            self.screen.blit(waiting_text, (self.width//2 -
                             waiting_text.get_width()//2, 350))

    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()

        while True:
            # 获取用户输入
            user_input = self.get_user_input()

            # 如果用户做出了选择，获取电脑选择
            if user_input and not self.computer_choice:
                self.get_computer_choice()

            # 绘制界面
            self.draw_interface()

            # 控制帧率
            clock.tick(60)


# 使用示例
if __name__ == "__main__":
    # 创建游戏实例
    game = RPSGame()

    # 运行游戏
    game.run()
