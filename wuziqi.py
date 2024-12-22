import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt

class WuziqiBoard(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化一个空的15x15棋盘（五子棋标准棋盘）
        self.board_state = [[0] * 15 for _ in range(15)]
        self.current_turn = 1  # 黑子先手
        self.initUI()

    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建重新开始按钮
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
        self.restart_button.setStyleSheet(button_style)
        
        # 添加按钮到布局
        button_layout.addWidget(self.restart_button)
        
        # 连接按钮信号
        self.restart_button.clicked.connect(self.reset_game)
        
        # 添加按钮布局到主布局
        main_layout.addLayout(button_layout)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 设置窗口属性
        self.setWindowTitle('五子棋')
        self.setGeometry(300, 300, 800, 850)
        
        # 设置按钮区域背景色
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setStyleSheet("""
            QWidget {
                background: #4A148C;
                padding: 10px;
            }
        """)
        
        main_layout.addWidget(button_container)
        main_layout.addStretch(1)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.drawBoard(painter)
        self.drawPieces(painter)
        painter.end()

    def drawBoard(self, painter):
        # 计算棋盘大小
        board_size = int(min(self.width(), self.height() - 100) * 0.8)
        square_size = board_size // 14  # 15条线需要14个格子
        
        # 计算棋盘在窗口中的位置
        start_x = (self.width() - board_size) // 2
        start_y = ((self.height() - 100) - board_size) // 2 + 100
        
        # 绘制棋盘外边框
        painter.setPen(Qt.black)
        painter.setBrush(QColor('#2C3E50'))
        painter.drawRect(
            int(start_x - square_size*0.2),
            int(start_y - square_size*0.2),
            int(board_size + square_size*0.4),
            int(board_size + square_size*0.4)
        )
        
        # 绘制棋盘背景
        painter.fillRect(start_x, start_y, board_size, board_size, QColor('#F5DEB3'))
        
        # 绘制格子线
        painter.setPen(QPen(QColor('#4A4A4A'), 1))
        for i in range(15):
            # 绘制垂直线
            x = start_x + i * square_size
            painter.drawLine(x, start_y, x, start_y + board_size)
            # 绘制水平线
            y = start_y + i * square_size
            painter.drawLine(start_x, y, start_x + board_size, y)

    def drawPieces(self, painter):
        board_size = int(min(self.width(), self.height() - 100) * 0.8)
        square_size = board_size // 14
        start_x = (self.width() - board_size) // 2
        start_y = ((self.height() - 100) - board_size) // 2 + 100
        
        for row in range(15):
            for col in range(15):
                if self.board_state[row][col] != 0:
                    x = start_x + col * square_size - square_size//2
                    y = start_y + row * square_size - square_size//2
                    
                    # 设置棋子颜色
                    color = Qt.black if self.board_state[row][col] == 1 else Qt.white
                    highlight = QColor('#333333') if self.board_state[row][col] == 1 else QColor('#CCCCCC')
                    
                    # 绘制阴影
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

    def mousePressEvent(self, event):
        board_size = int(min(self.width(), self.height() - 100) * 0.8)
        square_size = board_size // 14
        start_x = (self.width() - board_size) // 2
        start_y = ((self.height() - 100) - board_size) // 2 + 100
        
        # 获取鼠标点击的位置
        pos = event.pos()
        
        # 检查点击是否在棋盘范围内
        if (start_x <= pos.x() <= start_x + board_size and 
            start_y <= pos.y() <= start_y + board_size):
            
            # 转换为棋盘坐标，并进行四舍五入到最近的交叉点
            col = round((pos.x() - start_x) / square_size)
            row = round((pos.y() - start_y) / square_size)
            
            # 检查是否在棋盘范围内
            if 0 <= row < 15 and 0 <= col < 15:
                if self.board_state[row][col] == 0:
                    if ((self.current_turn == 1 and event.button() == Qt.LeftButton) or 
                        (self.current_turn == 2 and event.button() == Qt.RightButton)):
                        self.make_move(row, col)

    def make_move(self, row, col):
        self.board_state[row][col] = self.current_turn
        if self.check_win(row, col):
            self.game_over()
        else:
            self.current_turn = 3 - self.current_turn
        self.update()

    def check_win(self, row, col):
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        color = self.board_state[row][col]
        
        for dx, dy in directions:
            count = 1
            # 正向检查
            r, c = row + dx, col + dy
            while 0 <= r < 15 and 0 <= c < 15 and self.board_state[r][c] == color:
                count += 1
                r += dx
                c += dy
            
            # 反向检查
            r, c = row - dx, col - dy
            while 0 <= r < 15 and 0 <= c < 15 and self.board_state[r][c] == color:
                count += 1
                r -= dx
                c -= dy
                
            if count >= 5:
                return True
        return False

    def game_over(self):
        winner = "黑方" if self.current_turn == 1 else "白方"
        msg = QMessageBox()
        msg.setWindowTitle('游戏结束')
        msg.setText(f'{winner}获胜！')
        msg.exec_()
        self.reset_game()

    def reset_game(self):
        self.board_state = [[0] * 15 for _ in range(15)]
        self.current_turn = 1
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    board = WuziqiBoard()
    board.show()
    sys.exit(app.exec_()) 