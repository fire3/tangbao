import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt

class ChessBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # 初始化棋盘状态数组：0表示空，1表示黑子，2表示白子
        self.board_state = [[0] * 10 for _ in range(10)]
        # 设置初始棋子
        center = 4
        self.board_state[center][center] = 1
        self.board_state[center+1][center+1] = 1
        self.board_state[center][center+1] = 2
        self.board_state[center+1][center] = 2
        # 添加当前回合标记：1表示黑子回合，2表示白子回合
        self.current_turn = 1  # 黑子先手

    def initUI(self):
        # 设置窗口标题和初始大小
        self.setWindowTitle('黑白棋')
        self.setGeometry(300, 300, 800, 800)  # 设置更大的初始窗口
        # 设置渐变背景色
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #4A148C,
                    stop: 0.5 #311B92,
                    stop: 1 #1A237E
                );
            }
        """)

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
        board_size = int(min(self.width(), self.height()) * 0.8)  # 转换为整数
        square_size = board_size // 10
        start_x = (self.width() - board_size) // 2
        start_y = (self.height() - board_size) // 2
        
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
                # 只能在空位置放置棋子
                if self.board_state[row][col] == 0:
                    # 黑子回合只能放黑子，白子回合只能放白子
                    if (self.current_turn == 1 and event.button() == Qt.LeftButton) or \
                       (self.current_turn == 2 and event.button() == Qt.RightButton):
                        # 临时放置棋子检查是否可以翻转
                        self.board_state[row][col] = self.current_turn
                        if self.check_and_flip_pieces(row, col, self.current_turn, check_only=True):
                            # 确实可以翻转，执行实际的翻转操作
                            self.check_and_flip_pieces(row, col, self.current_turn)
                            # 切换回合
                            self.current_turn = 3 - self.current_turn
                            self.update()  # 重绘棋盘
                            # 检查游戏是否结束
                            self.check_game_over()
                        else:
                            # 不能翻转，撤销落子
                            self.board_state[row][col] = 0
    
    def drawBoard(self, painter):
        # 计算棋盘大小（取窗口宽高的较小值的80%）
        board_size = int(min(self.width(), self.height()) * 0.8)  # 转换为整数
        square_size = board_size // 10
        
        # 计算棋盘在窗口中的位置（居中）
        start_x = (self.width() - board_size) // 2
        start_y = (self.height() - board_size) // 2
        
        # 绘制棋盘外边框（深色边框）
        painter.setPen(Qt.black)
        painter.setBrush(QColor('#2C3E50'))  # 深色背景
        painter.drawRect(
            int(start_x - square_size*0.2),  # 转换为整数
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
        board_size = int(min(self.width(), self.height()) * 0.8)  # 转换为整数
        square_size = board_size // 10
        start_x = (self.width() - board_size) // 2
        start_y = (self.height() - board_size) // 2
        
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
        # 检查双方是否都无法继续落子
        black_can_move = self.check_valid_moves(1)
        white_can_move = self.check_valid_moves(2)
        
        if not black_can_move and not white_can_move:
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    board = ChessBoard()
    board.show()
    sys.exit(app.exec_())
