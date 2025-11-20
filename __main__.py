import sys
import os
import pygame
import time
from src.control.RPSController import RPSController
from src.control.game import RPSGame


def init_dataset_path(filename: str) -> str:
    """
    在主函数中初始化数据集目录和文件
    filename 例子："/solve1/jsq.json"
    """

    # 转换为完整路径：../dataset/solve1/jsq.json
    base = "./dataset"
    full_path = base + filename

    # 获取目录，如 ../dataset/solve1/
    dir_path = os.path.dirname(full_path)

    # 自动创建目录
    os.makedirs(dir_path, exist_ok=True)

    # 如果文件不存在 → 自动创建空结构
    if not os.path.exists(full_path):
        init_data = {
            "metadata": {
                "created_date": "",
                "total_games": 0,
                "computer_wins": 0,
                "user_wins": 0,
                "draws": 0,
                "last_updated": "",
                "version": "1.0"
            },
            "game_records": []
        }

        with open(full_path, "w", encoding="utf-8") as f:
            import json
            json.dump(init_data, f, ensure_ascii=False, indent=2)

        print(f"已自动创建数据文件: {full_path}")

    return filename  # 返回相对路径（RPSController 会拼接 ../dataset）


def main():

    # === 1. 主程序自定义变量 ===
    dataset_name = "/solve1/jsq.json"   # 数据集文件
    mode = "1"                          # 训练模式

    # === 2. 主函数中完成目录和文件初始化 ===
    dataset_name = init_dataset_path(dataset_name)

    # === 3. 初始化控制器与游戏 ===
    controller = RPSController(filename=dataset_name, mode=mode)
    game = RPSGame()

    print(f"系统已启动 → 数据集: {dataset_name}, 模式: {mode}")
    print("游戏窗口已打开，使用鼠标选择出拳。Ctrl+C 可强制退出。\n")

    clock = pygame.time.Clock()

    try:
        while True:
            user_input = game.get_user_input()

            if user_input in ["rock", "scissors", "paper"]:
                # 计算结果
                result = controller.method1_process_game(user_input)

                # 显示结果
                game.user_choice = result["user_choice"]
                game.computer_choice = result["computer_choice"]
                game.result = result["result"]

                # 保存数据
                controller.method2_save_to_dataset()

            game.draw_interface()
            clock.tick(60)

    except KeyboardInterrupt:
        print("\n收到 Ctrl+C，程序已退出。")
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
