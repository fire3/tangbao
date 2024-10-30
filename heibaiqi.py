import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QRadioButton
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer

class ColorSelectDialog(QDialog):
    """颜色选择对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('选择您的棋子颜色')
        layout = QVBoxLayout()
        
        # 添加提示文本
        label = QLabel('请选择您要执的棋子颜色：')
        layout.addWidget(label)
        
        # 创建单选按钮
        self.black_radio = QRadioButton('执黑子（先手）')
        self.white_radio = QRadioButton('执白子（后手）')
        self.black_radio.setChecked(True)  # 默认选择黑子
        
        layout.addWidget(self.black_radio)
        layout.addWidget(self.white_radio)
        
        # 创建确认按钮
        confirm_button = QPushButton('确认')
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)
        
        self.setLayout(layout)

class ChessBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.is_ai_mode = False  # 默认人人对战模式
        self.player_is_black = True  # 默认玩家执黑
        # 初始化棋盘状态
        self.board_state = [[0] * 10 for _ in range(10)]
        center = 4
        self.board_state[center][center] = 1
        self.board_state[center+1][center+1] = 1
        self.board_state[center][center+1] = 2
        self.board_state[center+1][center] = 2
        self.current_turn = 1  # 黑子先手
        
        self.initUI()

    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建模式选择按钮
        self.pvp_button = QPushButton('人人对战', self)
        self.pve_button = QPushButton('人机对战', self)
        self.restart_button = QPushButton('重新开始', self)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #4A148C;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #6A1B9A;
            }
            QPushButton:pressed {
                background-color: #38006b;
            }
        """
        self.pvp_button.setStyleSheet(button_style)
        self.pve_button.setStyleSheet(button_style)
        self.restart_button.setStyleSheet(button_style)
        
        # 添加按钮到布局
        button_layout.addWidget(self.pvp_button)
        button_layout.addWidget(self.pve_button)
        button_layout.addWidget(self.restart_button)
        
        # 连接按钮信号
        self.pvp_button.clicked.connect(self.start_pvp_mode)
        self.pve_button.clicked.connect(self.show_color_select)
        self.restart_button.clicked.connect(self.reset_game)
        
        # 添加按钮布局到主布局（放在最上方）
        main_layout.addLayout(button_layout)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 设置窗口属性
        self.setWindowTitle('黑白棋')
        self.setGeometry(300, 300, 800, 850)
        
        # 只为按钮区域设置背景色
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setStyleSheet("""
            QWidget {
                background: #4A148C;
                padding: 10px;
            }
        """)
        
        main_layout.addWidget(button_container)
        main_layout.addStretch(1)  # 添加弹性空间

    def show_color_select(self):
        """显示颜色选择对话框"""
        dialog = ColorSelectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.player_is_black = dialog.black_radio.isChecked()
            self.start_pve_mode()

    def start_pve_mode(self):
        """切换到人机对战模式"""
        self.is_ai_mode = True
        self.reset_game()
        # 如果玩家选择执白，AI先手（执黑）
        if not self.player_is_black:
            self.current_turn = 1  # 确保是黑子回合
            QTimer.singleShot(500, self.ai_move)

    def ai_move(self):
        """AI落子逻辑"""
        best_score = float('-inf')
        best_move = None
        ai_color = 1 if not self.player_is_black else 2  # AI的颜色与玩家相反
        
        # 遍历所有可能的落子位置
        for row in range(10):
            for col in range(10):
                if self.board_state[row][col] == 0:
                    # 临时落子
                    self.board_state[row][col] = ai_color
                    if self.check_and_flip_pieces(row, col, ai_color, check_only=True):
                        # 计算这步棋的得分
                        score = self.evaluate_move(row, col)
                        if score > best_score:
                            best_score = score
                            best_move = (row, col)
                    # 撤销临时落子
                    self.board_state[row][col] = 0
        
        # 如果找到合法移动，执行这个移动
        if best_move:
            row, col = best_move
            self.board_state[row][col] = ai_color
            self.check_and_flip_pieces(row, col, ai_color)
            # 检查玩家是否有合法移动
            player_color = 2 if not self.player_is_black else 1
            if self.check_valid_moves(player_color):
                self.current_turn = player_color
            else:
                self.check_game_over()
            self.update()

    def evaluate_move(self, row, col):
        """评估某个位置的得分"""
        score = 0
        ai_color = 1 if not self.player_is_black else 2  # AI的颜色与玩家相反
        
        # 临时保存棋盘状态
        temp_board = [row[:] for row in self.board_state]
        # 计算这步棋能翻转多少个子
        self.check_and_flip_pieces(row, col, ai_color)
        # 计算翻转后的得分
        for i in range(10):
            for j in range(10):
                if self.board_state[i][j] == ai_color:
                    # 角落位置最有价值
                    if (i in [0, 9] and j in [0, 9]):
                        score += 10
                    # 边缘位置次之
                    elif i in [0, 9] or j in [0, 9]:
                        score += 5
                    # 普通位置
                    else:
                        score += 1
        # 恢复棋盘状态
        self.board_state = temp_board
        return score

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.drawBoard(painter)
        self.drawInitialPieces(painter)
        painter.end()
        
    def check_and_flip_pieces(self, row, col, color, check_only=False):
        """
        检查并翻转棋子
        check_only: 如果为True，只检查是否可以翻转，不实际翻转
        """
        directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
        flipped = False
        
        for dx, dy in directions:
            temp_flip = []
            current_row = row + dx
            current_col = col + dy
            
            while 0 <= current_row < 10 and 0 <= current_col < 10:
                if self.board_state[current_row][current_col] == 0:
                    break
                elif self.board_state[current_row][current_col] == (3 - color):
                    temp_flip.append((current_row, current_col))
                elif self.board_state[current_row][current_col] == color:
                    if temp_flip:  # 只有当有可翻转的棋子时才算作有效
                        if not check_only:  # 只在非检查模式下实际翻转棋子
                            for flip_row, flip_col in temp_flip:
                                self.board_state[flip_row][flip_col] = color
                        flipped = True
                    break
                
                current_row += dx
                current_col += dy
                
        return flipped

    def mousePressEvent(self, event):
        # 计算棋盘大小（与绘制时使用相同的计算方法）
        board_size = int(min(self.width(), self.height() - 100) * 0.8)  # 减去按钮区域的高度
        square_size = board_size // 10
        start_x = (self.width() - board_size) // 2
        start_y = ((self.height() - 100) - board_size) // 2 + 100  # 考虑按钮区域的高度
        
        # 获取鼠标点击的位置
        pos = event.pos()
        
        # 检查点击是否在棋盘范围内
        if (start_x <= pos.x() <= start_x + board_size and 
            start_y <= pos.y() <= start_y + board_size):
            
            # 转换为棋盘坐标
            col = (pos.x() - start_x) // square_size
            row = (pos.y() - start_y) // square_size
            
            # 检查是否在棋盘范围内（额外的安全检查）
            if 0 <= row < 10 and 0 <= col < 10:
                if self.board_state[row][col] == 0:
                    if self.is_ai_mode:
                        # 人机模式下的落子逻辑
                        if ((self.player_is_black and self.current_turn == 1) or 
                            (not self.player_is_black and self.current_turn == 2)):
                            # 玩家回合
                            if ((self.player_is_black and event.button() == Qt.LeftButton) or 
                                (not self.player_is_black and event.button() == Qt.RightButton)):
                                self.make_move(row, col)
                    else:
                        # 人人对战模式的原有逻辑
                        if ((self.current_turn == 1 and event.button() == Qt.LeftButton) or 
                            (self.current_turn == 2 and event.button() == Qt.RightButton)):
                            self.make_move(row, col)

    def make_move(self, row, col):
        """执行落子操作"""
        current_color = self.current_turn
        self.board_state[row][col] = current_color
        if self.check_and_flip_pieces(row, col, current_color, check_only=True):
            self.check_and_flip_pieces(row, col, current_color)
            next_turn = 3 - current_color
            if self.check_valid_moves(next_turn):
                self.current_turn = next_turn
                if self.is_ai_mode and ((self.player_is_black and current_color == 1) or 
                                      (not self.player_is_black and current_color == 2)):
                    QTimer.singleShot(500, self.ai_move)
            else:
                self.check_game_over()
            self.update()
        else:
            self.board_state[row][col] = 0

    def drawBoard(self, painter):
        # 计算棋盘大小（取窗口宽高的较小值的80%）
        board_size = int(min(self.width(), self.height() - 100) * 0.8)  # 减去按钮区域的高度
        square_size = board_size // 10
        
        # 计算棋盘在窗口中的位置（居中）
        start_x = (self.width() - board_size) // 2
        start_y = ((self.height() - 100) - board_size) // 2 + 100  # 考虑按钮区域的高度
        
        # 绘制棋盘外边框（深色边框）
        painter.setPen(Qt.black)
        painter.setBrush(QColor('#2C3E50'))  # 深色背景
        painter.drawRect(
            int(start_x - square_size*0.2),
            int(start_y - square_size*0.2),
            int(board_size + square_size*0.4),
            int(board_size + square_size*0.4)
        )
        
        # 绘制棋盘背景（米色）
        painter.fillRect(start_x, start_y, board_size, board_size, QColor('#F5DEB3'))
        
        # 绘制格子
        painter.setPen(QPen(QColor('#4A4A4A'), 1))  # 使用深灰色线条
        for i in range(11):
            # 绘制垂直线
            x = start_x + i * square_size
            painter.drawLine(x, start_y, x, start_y + board_size)
            # 绘制水平线
            y = start_y + i * square_size
            painter.drawLine(start_x, y, start_x + board_size, y)

    def drawInitialPieces(self, painter):
        # 计算棋盘大小
        board_size = int(min(self.width(), self.height() - 100) * 0.8)  # 减去按钮区域的高度
        square_size = board_size // 10
        start_x = (self.width() - board_size) // 2
        start_y = ((self.height() - 100) - board_size) // 2 + 100  # 考虑按钮区域的高度
        
        for row in range(10):
            for col in range(10):
                if self.board_state[row][col] != 0:
                    x = start_x + col * square_size
                    y = start_y + row * square_size
                    
                    # 设置棋子颜色和效果
                    if self.board_state[row][col] == 1:  # 黑子
                        color = Qt.black
                        highlight = QColor('#333333')
                    else:  # 白子
                        color = Qt.white
                        highlight = QColor('#CCCCCC')
                    
                    # 绘制棋子阴影
                    painter.setBrush(QColor(0, 0, 0, 50))
                    painter.setPen(Qt.NoPen)
                    shadow_margin = square_size // 8
                    painter.drawEllipse(
                        int(x + shadow_margin + 2),
                        int(y + shadow_margin + 2),
                        int(square_size - 2*shadow_margin),
                        int(square_size - 2*shadow_margin)
                    )
                    
                    # 绘制棋子
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(Qt.black if color == Qt.white else Qt.darkGray, 1))
                    margin = square_size // 8
                    painter.drawEllipse(
                        int(x + margin),
                        int(y + margin),
                        int(square_size - 2*margin),
                        int(square_size - 2*margin)
                    )
                    
                    # 添加高光效果
                    painter.setBrush(QBrush(highlight))
                    painter.setPen(Qt.NoPen)
                    highlight_margin = square_size // 4
                    painter.drawEllipse(
                        int(x + highlight_margin),
                        int(y + highlight_margin),
                        int(square_size // 3),
                        int(square_size // 3)
                    )

    def check_valid_moves(self, color):
        """检查指定颜色是否还有合法的落子位置"""
        for row in range(10):
            for col in range(10):
                if self.board_state[row][col] == 0:  # 对每个空位置
                    # 临时放置棋子
                    self.board_state[row][col] = color
                    # 检查是否能翻转任何棋子
                    if self.check_and_flip_pieces(row, col, color, check_only=True):
                        # 还原棋盘状态
                        self.board_state[row][col] = 0
                        return True
                    # 还原棋盘状态
                    self.board_state[row][col] = 0
        return False
    
    def check_game_over(self):
        """检查游戏是否结束并显示结果"""
        # 计算双方棋子数量
        black_count = sum(row.count(1) for row in self.board_state)
        white_count = sum(row.count(2) for row in self.board_state)
        
        # 显示结果
        msg = QMessageBox()
        msg.setWindowTitle('游戏结束')
        
        if black_count > white_count:
            result = f'黑方胜利！\n黑子：{black_count}\n白子：{white_count}'
        elif white_count > black_count:
            result = f'白方胜利！\n黑子：{black_count}\n白子：{white_count}'
        else:
            result = f'平局！\n黑子：{black_count}\n白子：{white_count}'
            
        msg.setText(result)
        msg.exec_()
        
        # 重置游戏
        self.reset_game()
        
    def reset_game(self):
        """重置游戏状态"""
        self.board_state = [[0] * 10 for _ in range(10)]
        center = 4
        self.board_state[center][center] = 1
        self.board_state[center+1][center+1] = 1
        self.board_state[center][center+1] = 2
        self.board_state[center+1][center] = 2
        self.current_turn = 1
        self.update()

    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        self.update()  # 重绘棋盘

    def start_pvp_mode(self):
        """切换到人人对战模式"""
        self.is_ai_mode = False
        self.reset_game()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    board = ChessBoard()
    board.show()
    sys.exit(app.exec_())
