import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                            QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import (QPainter, QPen, QColor, QBrush, QFont, 
                        QLinearGradient)
from PyQt5.QtCore import Qt, QRect

class TicTacToeBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.resetGame()

    def resetGame(self):
        self.board_state = [[0] * 3 for _ in range(3)]
        self.current_piece = 1  # X先手
        self.move_history = []
        self.game_over = False
        self.winner = 0
        self.winning_line = []
        self.ai_enabled = False  # 默认为人人对战
        self.update()

    def initUI(self):
        self.setMinimumSize(600, 500)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('#F0F0F0'))
        self.setPalette(palette)

    def mousePressEvent(self, event):
        if self.game_over:
            return

        board_size = min(self.width()-200, self.height()-200)
        start_x = (self.width() - board_size) // 2
        start_y = (self.height() - board_size) // 2
        cell_size = board_size // 3

        x = event.x() - start_x
        y = event.y() - start_y

        if 0 <= x <= board_size and 0 <= y <= board_size:
            row = int(y // cell_size)
            col = int(x // cell_size)
            
            if 0 <= row < 3 and 0 <= col < 3 and self.board_state[row][col] == 0:
                # 人机模式
                if self.ai_enabled:
                    if self.current_piece == 1 and event.button() == Qt.LeftButton:
                        self.make_move(row, col)
                        if not self.game_over:
                            self.ai_move()
                # 人人模式
                else:
                    if (self.current_piece == 1 and event.button() == Qt.LeftButton) or \
                       (self.current_piece == 2 and event.button() == Qt.RightButton):
                        self.make_move(row, col)

    def make_move(self, row, col):
        # 记录移动
        self.move_history.append((row, col))
        # 如果已经下了7个子，移除第一个
        if len(self.move_history) > 6:
            old_row, old_col = self.move_history.pop(0)
            self.board_state[old_row][old_col] = 0
        
        # 放置新棋子
        self.board_state[row][col] = self.current_piece
        
        # 检查是否获胜
        if self.check_winner():
            self.game_over = True
            self.winner = self.current_piece
            # 显示游戏结束对话框
            self.showGameOverDialog()
        else:
            # 切换棋子类型
            self.current_piece = 3 - self.current_piece
        
        self.update()

    def ai_move(self):
        move = self.get_best_move()
        if move:
            row, col = move
            self.make_move(row, col)

    def get_best_move(self):
        # 1. 检查AI是否能赢
        winning_move = self.find_winning_move(2)  # 2 代表 O
        if winning_move:
            return winning_move

        # 2. 检查是否需要阻止对手赢
        blocking_move = self.find_winning_move(1)  # 1 代表 X
        if blocking_move:
            return blocking_move

        # 3. 策略性选择位置
        # 优先级：中心 > 角落 > 边
        priority_positions = [
            (1, 1),  # 中心
            (0, 0), (0, 2), (2, 0), (2, 2),  # 角落
            (0, 1), (1, 0), (1, 2), (2, 1)   # 边
        ]

        # 检查这些位置是否可用
        for row, col in priority_positions:
            if self.board_state[row][col] == 0:
                return (row, col)

        return None

    def find_winning_move(self, player):
        # 检查每个空位
        for row in range(3):
            for col in range(3):
                if self.board_state[row][col] == 0:
                    # 尝试在此位置下棋
                    self.board_state[row][col] = player
                    # 检查是否获胜
                    if self.check_winner():
                        self.board_state[row][col] = 0  # 恢复
                        return (row, col)
                    self.board_state[row][col] = 0  # 恢复
        return None

    def drawX(self, painter, x, y, size, is_winner=False):
        if is_winner:
            # 获胜的X使用更粗的线条和金色
            painter.setPen(QPen(QColor('#FFD700'), 6, Qt.SolidLine, Qt.RoundCap))
        else:
            painter.setPen(QPen(Qt.red, 4, Qt.SolidLine, Qt.RoundCap))
        margin = size // 4
        painter.drawLine(x + margin, y + margin, x + size - margin, y + size - margin)
        painter.drawLine(x + size - margin, y + margin, x + margin, y + size - margin)

    def drawO(self, painter, x, y, size, is_winner=False):
        if is_winner:
            # 获胜的O使用更粗的线条和金色
            painter.setPen(QPen(QColor('#FFD700'), 6))
        else:
            painter.setPen(QPen(Qt.blue, 4))
        margin = size // 4
        painter.drawEllipse(x + margin, y + margin, size - 2*margin, size - 2*margin)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿

        # 绘制外部背景框
        painter.setPen(QPen(QColor('#8B4513'), 3))  # 棕色边框
        painter.setBrush(QBrush(QColor('#DEB887')))  # 浅棕色填充
        painter.drawRect(50, 50, self.width()-100, self.height()-100)

        # 计算棋盘在中心的位置
        board_size = min(self.width()-200, self.height()-200)  # 棋盘大小
        start_x = (self.width() - board_size) // 2
        start_y = (self.height() - board_size) // 2
        
        # 绘制棋盘背景
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor('#FFFFFF')))
        painter.drawRect(start_x, start_y, board_size, board_size)

        # 计算格子大小
        cell_size = board_size // 3

        # 绘制网格线
        for i in range(1, 3):
            painter.drawLine(
                start_x + cell_size * i, 
                start_y,
                start_x + cell_size * i, 
                start_y + board_size
            )
            painter.drawLine(
                start_x,
                start_y + cell_size * i,
                start_x + board_size,
                start_y + cell_size * i
            )

        # 绘制棋子
        for row in range(3):
            for col in range(3):
                x = start_x + col * cell_size
                y = start_y + row * cell_size
                is_winner = (row, col) in self.winning_line
                if self.board_state[row][col] == 1:  # X
                    self.drawX(painter, x, y, cell_size, is_winner)
                elif self.board_state[row][col] == 2:  # O
                    self.drawO(painter, x, y, cell_size, is_winner)

        # 如果游戏结束，绘制获胜效果
        if self.game_over:
            # 绘制半透明遮罩
            overlay = QColor(255, 255, 255, 180)
            painter.fillRect(self.rect(), overlay)
            
            # 绘制获胜线
            if self.winning_line:
                painter.setPen(QPen(QColor('#FFD700'), 8, Qt.SolidLine, Qt.RoundCap))
                start_pos = self.winning_line[0]
                end_pos = self.winning_line[2]
                x1 = start_x + start_pos[1] * cell_size + cell_size // 2
                y1 = start_y + start_pos[0] * cell_size + cell_size // 2
                x2 = start_x + end_pos[1] * cell_size + cell_size // 2
                y2 = start_y + end_pos[0] * cell_size + cell_size // 2
                painter.drawLine(x1, y1, x2, y2)

            # 绘制获胜文字
            painter.setPen(QPen(QColor('#4A4A4A'), 4))
            painter.setFont(QFont('Arial', 36, QFont.Bold))
            winner_text = "X 获胜！" if self.winner == 1 else "O 获胜！"
            
            # 创建文字阴影效果
            shadow_color = QColor(0, 0, 0, 100)
            painter.setPen(shadow_color)
            text_rect = self.rect()
            text_rect.translate(3, 3)  # 阴影偏移
            painter.drawText(text_rect, Qt.AlignCenter, winner_text)
            
            # 绘制主文字
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0.0, QColor('#FFD700'))
            gradient.setColorAt(1.0, QColor('#FFA500'))
            painter.setPen(QPen(QColor('#4A4A4A'), 2))
            painter.setBrush(QBrush(gradient))
            painter.drawText(self.rect(), Qt.AlignCenter, winner_text)

        # 显示当前应该下的棋子类型
        if not self.game_over:
            painter.setPen(QPen(Qt.black, 2))
            painter.setFont(QFont('Arial', 12))
            next_piece = "下一步: X" if self.current_piece == 1 else "下一步: O"
            painter.drawText(10, 30, next_piece)

    def check_winner(self):
        # 检查行
        for row in range(3):
            if self.board_state[row][0] != 0 and \
               self.board_state[row][0] == self.board_state[row][1] == self.board_state[row][2]:
                self.winning_line = [(row, 0), (row, 1), (row, 2)]
                return True
        
        # 检查列
        for col in range(3):
            if self.board_state[0][col] != 0 and \
               self.board_state[0][col] == self.board_state[1][col] == self.board_state[2][col]:
                self.winning_line = [(0, col), (1, col), (2, col)]
                return True
        
        # 检查对角线
        if self.board_state[0][0] != 0 and \
           self.board_state[0][0] == self.board_state[1][1] == self.board_state[2][2]:
            self.winning_line = [(0, 0), (1, 1), (2, 2)]
            return True
            
        if self.board_state[0][2] != 0 and \
           self.board_state[0][2] == self.board_state[1][1] == self.board_state[2][0]:
            self.winning_line = [(0, 2), (1, 1), (2, 0)]
            return True
            
        return False

    def showGameOverDialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("游戏结束")
        winner_text = "X 获胜！" if self.winner == 1 else "O 获胜！"
        msg.setText(f"游戏结束！{winner_text}\n\n要开始新游戏吗？")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            self.resetGame()
        else:
            # 如果不重新开始，可以继续查看当前棋局
            pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('井字棋')
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建模式选择按钮
        self.pve_button = QPushButton('人机对战', self)
        self.pvp_button = QPushButton('人人对战', self)
        self.restart_button = QPushButton('重新开始', self)
        self.quit_button = QPushButton('退出游戏', self)
        
        # 设置按钮样式
        for button in [self.pve_button, self.pvp_button, 
                      self.restart_button, self.quit_button]:
            button.setMinimumWidth(100)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
        
        # 添加按钮到布局
        button_layout.addWidget(self.pve_button)
        button_layout.addWidget(self.pvp_button)
        button_layout.addWidget(self.restart_button)
        button_layout.addWidget(self.quit_button)
        
        # 创建游戏板
        self.board = TicTacToeBoard(self)
        
        # 添加所有组件到主布局
        layout.addLayout(button_layout)
        layout.addWidget(self.board)
        
        # 连接按钮信号
        self.pve_button.clicked.connect(self.startPVE)
        self.pvp_button.clicked.connect(self.startPVP)
        self.restart_button.clicked.connect(self.restartGame)
        self.quit_button.clicked.connect(self.close)
        
        # 设置窗口大小
        self.setGeometry(100, 100, 800, 700)

    def startPVE(self):
        self.board.resetGame()
        self.board.ai_enabled = True
        self.showGameStartMessage("人机对战模式")

    def startPVP(self):
        self.board.resetGame()
        self.board.ai_enabled = False
        self.showGameStartMessage("人人对战模式")

    def restartGame(self):
        if self.board.game_over:
            self.board.resetGame()
        else:
            reply = QMessageBox.question(self, '确认重新开始', 
                                       '游戏尚未结束，确定要重新开始吗？',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.board.resetGame()

    def showGameStartMessage(self, mode):
        msg = QMessageBox(self)
        msg.setWindowTitle("游戏开始")
        msg.setText(f"{mode}已开始！\n\n" + 
                   ("电脑将执O棋。" if mode == "人机对战模式" else "玩家1执X，玩家2执O。"))
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '确认退出', 
                                   '确定要退出游戏吗？',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
