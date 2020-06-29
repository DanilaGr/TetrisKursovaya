import pygame
import pdb
import random
import math
import block
import constants
class Tetris(object):
    """
    Класс реализующий логику игры
    """
    def __init__(self,bx,by):
        """
       Инициализация объектов.
       Параметры:
            - bx - Число блоков по оси x
            - by - Число блоков по оси y
        """
        # Вычисление размера игрового поля по требуемому колличеству блоков.
        self.resx = bx*constants.BWIDTH+2*constants.BOARD_HEIGHT+constants.BOARD_MARGIN
        self.resy = by*constants.BHEIGHT+2*constants.BOARD_HEIGHT+constants.BOARD_MARGIN
        # Подготовка объектов игрового поля (белые линии)
        self.board_up    = pygame.Rect(0,constants.BOARD_UP_MARGIN,self.resx,constants.BOARD_HEIGHT)
        self.board_down  = pygame.Rect(0,self.resy-constants.BOARD_HEIGHT,self.resx,constants.BOARD_HEIGHT)
        self.board_left  = pygame.Rect(0,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,self.resy)
        self.board_right = pygame.Rect(self.resx-constants.BOARD_HEIGHT,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,self.resy)
        # Список использованных блоков
        self.blk_list    = []
        # Вычисления стартовых значений для блоков тетриса
        self.start_x = math.ceil(self.resx/2.0)
        self.start_y = constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + constants.BOARD_MARGIN
        # Данные блоков (цвета и фигуры). Фигура определяется в списке [X,Y] точек. Каждая точка
        # обозначает позицию блока. Значения true/false определяют возможность вращения
        # False запрещает True разрешает.
        self.block_data = (
            ([[0,0],[1,0],[2,0],[3,0]],constants.BLUE,True),     # I фигура
            ([[0,0],[1,0],[0,1],[-1,1]],constants.RED,True),  # S фигура
            ([[0,0],[1,0],[2,0],[2,1]],constants.BLUE,True),    # J фигура
            ([[0,0],[0,1],[1,0],[1,1]],constants.ORANGE,False), # O фигура
            ([[-1,0],[0,0],[0,1],[1,1]],constants.GREEN,True),   # Z фигура
            ([[0,0],[1,0],[2,0],[1,1]],constants.PURPLE,True),  # T фигура
            ([[0,0],[1,0],[2,0],[0,1]],constants.PURPLE,True),    # J фигура
        )
        # Вычисление количества блоков. Мы можем напрямую использовать четное число блоков 
        # но при использовании нечетного числа мы должны уменьшать его на 1 (из за поля).
        self.blocks_in_line = bx if bx%2 == 0 else bx-1
        self.blocks_in_pile = by
        # Настройки рейтинга
        self.score = 0
        # Начальная скорость
        self.speed = 1
        # Максимальный рейтинг
        self.score_level = constants.SCORE_LEVEL

    def apply_action(self):
        """
        Запустить соответствующее действие, получив событие из очереди
        
        """
        # Получение события из очереди
        for ev in pygame.event.get():
            # Проверка нажатия клавиши закрытия программы
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                self.done = True
            # Проверка событий контроля игры
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    self.active_block.move(0,constants.BHEIGHT)
                if ev.key == pygame.K_LEFT:
                    self.active_block.move(-constants.BWIDTH,0)
                if ev.key == pygame.K_RIGHT:
                    self.active_block.move(constants.BWIDTH,0)
                if ev.key == pygame.K_SPACE:
                    self.active_block.rotate()
                if ev.key == pygame.K_p:
                    self.pause()     
            # Определение завершения движения основываясь на таймере
            if ev.type == constants.TIMER_MOVE_EVENT:
                self.active_block.move(0,constants.BHEIGHT)       
    def pause(self):
        """
        Пауза и вывод на экран строки информирующей о паузе

        """
        # Вывод строки по центру экрана
        self.print_center(["PAUSE","Press \"p\" to continue"])
        pygame.display.flip()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:
                    return      
    def set_move_timer(self):
        """
        Установка таймера перемещения       
        """
        # Установка времения для запуска события перемещения (минимум 1!!!)
        speed = math.floor(constants.MOVE_TICK / self.speed)
        speed = max(1,speed)
        pygame.time.set_timer(constants.TIMER_MOVE_EVENT,speed) 
    def run(self):
        # Инициализация игры (pygame, font)
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont(pygame.font.get_default_font(),constants.FONT_SIZE)
        self.screen = pygame.display.set_mode((self.resx,self.resy))
        pygame.display.set_caption("Tetris")
        # Установка времени для запуска события движения
        self.set_move_timer()
        # Переменные контролирующие игру. Сигнал завершения используется для контроля 
        # основного цикла (меняется при событии закрытия игры), сигнал проигрыша игры (game_over)
        # меняется при помощи игровой логики и используется для вывода на экран надписи "game over"
        # Переменная new_block Используется для запроса новой фигуры 
        self.done = False
        self.game_over = False
        self.new_block = True
        # Вывод рейтинга
        self.print_status_line()
        while not(self.done) and not(self.game_over):
            # Получение фигуры и запуск игровой логики
            self.get_block()
            self.game_logic()
            self.draw_game()
        # Вывод на экран game_over и ожидание нажатие клавиши
        if self.game_over:
            self.print_game_over()
        # Изображение материалов pygame
        pygame.font.quit()
        pygame.display.quit()           
    def print_status_line(self):
        """
        Вывод строки состояния
        """
        string = ["SCORE: {0}   SPEED: {1}x".format(self.score,self.speed)]
        self.print_text(string,constants.POINT_MARGIN,constants.POINT_MARGIN)        
    def print_game_over(self):
        """
        Вывод строки об окончании игры.
        """
        # Вывод текста "Game over"
        self.print_center(["Game Over","Press \"q\" to exit"])
        # Вывод строки
        pygame.display.flip()
        # Ожидание нажатия пробела
        while True: 
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                    return
    def print_text(self,str_lst,x,y):
        """
        Вывод текста по координатам X,Y 
        Параметры:
            - str_lst - список строк для вывода. Каждая на новой линии.
            - x - Координата X первой строки
            - y - Координата Y первой строки
        """
        prev_y = 0
        for string in str_lst:
            size_x,size_y = self.myfont.size(string)
            txt_surf = self.myfont.render(string,False,(255,255,255))
            self.screen.blit(txt_surf,(x,y+prev_y))
            prev_y += size_y 
    def print_center(self,str_list):
        """
        Печать строки по центу экрана.
        
       Параметры:
            - str_lst - список строк для вывода. Каждая на новой линии.
        """
        max_xsize = max([tmp[0] for tmp in map(self.myfont.size,str_list)])
        self.print_text(str_list,self.resx/2-max_xsize/2,self.resy/2)
    def block_colides(self):
        """
        Проверка соприкасновения фигуры с другим блоком.
        Возвращение значения True, если замечено соприкасновение.
        """
        for blk in self.blk_list:
            # Проверка, не является ли фигура той же самой.
            if blk == self.active_block:
                continue 
            # Проверка на столкновение
            if(blk.check_collision(self.active_block.shape)):
                return True
        return False
    def game_logic(self):
        """
        Основная игровая логика. Обнаруживает столкновения и устанавливает новые блоки.
        """
        # Запомнить текущее состояние и применить действие 
        self.active_block.backup()
        self.apply_action()
        # Проверка на столкновение с границами игрового поля
        # Эта проверка так же включает другие блоки тетриса
        down_board  = self.active_block.check_collision([self.board_down])
        any_border  = self.active_block.check_collision([self.board_left,self.board_up,self.board_right])
        block_any   = self.block_colides()
        # Восстановление состояния при обнаружении столкновения
        if down_board or any_border or block_any:
            self.active_block.restore()
        # Попытка сдвинуть вниз для проверки на соприкасновение
        # Вставляем фигуру, если мы достигли границы или столкнулись с блоками под фигурой
        self.active_block.backup()
        self.active_block.move(0,constants.BHEIGHT)
        can_move_down = not self.block_colides()  
        self.active_block.restore()
        # Окончание игры при отсутствии возможности двигаться вниз на позиции появления.
        if not can_move_down and (self.start_x == self.active_block.x and self.start_y == self.active_block.y):
            self.game_over = True
        # Фигура вставляется по достижении границы или отсутствия возможности двигаться дальше вниз.
        if down_board or not can_move_down:     
            # Запрос новой фигуры
            self.new_block = True
            # Проверка на заполненные линии и возможность их удаления
            self.detect_line()   
    def detect_line(self):
        """
        Проверяем, заполнена ли линия, если да, то удаляем ее и устанавливаем линии выше на новые позиции.
        """
        # Попытка обнаружить заполненную строку из неподвижных блоков. 
        # Количество блоков передается в класс функции инициализации.
        for shape_block in self.active_block.shape:
            tmp_y = shape_block.y
            tmp_cnt = self.get_blocks_in_line(tmp_y)
            # Проверить, содержит ли линия заданное количество блоков.
            if tmp_cnt != self.blocks_in_line:
                continue 
            # Если замечена заполненная линия   
            self.remove_line(tmp_y)
            # Обновление рейтинга.
            self.score += self.blocks_in_line * constants.POINT_VALUE 
            # Проверка того, нужно ли нам ускорить игру. Если да, то изменяем переменные контролирующие скорость
            if self.score > self.score_level:
                self.score_level *= constants.SCORE_LEVEL_RATIO
                self.speed       *= constants.GAME_SPEEDUP_RATIO
                # Изменение скорости
                self.set_move_timer()
    def remove_line(self,y):
        """
        Удалить линии с заданными Y координатами. Блоки ниже заполненной линии не трогаются.
        Остальные блоки (yi > y) перемещаются на один уровень.
        Параметры:
            - y - Y Координаты для удаления.
        """ 
        # Перебрать все блоки и удалить блоки с координатами Y
        for block in self.blk_list:
            block.remove_blocks(y)
        # Установка нового списка блоков. Ненужные удаляются.
        self.blk_list = [blk for blk in self.blk_list if blk.has_blocks()]
    def get_blocks_in_line(self,y):
        """
        Получение количества блоков по координате Y.
        Параметры:
            - y - Y сканируемые координаты.
        """
        #Проверка списка блоков и увеличение счетчика, если блок равен координате Y
        tmp_cnt = 0
        for block in self.blk_list:
            for shape_block in block.shape:
                tmp_cnt += (1 if y == shape_block.y else 0)            
        return tmp_cnt
    def draw_board(self):
        """
        Вывод белой рамки
        """
        pygame.draw.rect(self.screen,constants.WHITE,self.board_up)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_down)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_left)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_right)
        # Обновление рейтинка         
        self.print_status_line()
    def get_block(self):
        """
        Создание нового блока, если это необходимо.
        """
        if self.new_block:
            # Получить блок и добавить его в список (на данный момент статический)
            tmp = random.randint(0,len(self.block_data)-1)
            data = self.block_data[tmp]
            self.active_block = block.Block(data[0],self.start_x,self.start_y,self.screen,data[1],data[2])
            self.blk_list.append(self.active_block)
            self.new_block = False
    def draw_game(self):
        """
        Вывод игрового экрана.
        """
        # Очистка экрана и прорисовка поля и фигур.
        self.screen.fill(constants.BLACK)
        self.draw_board()
        for blk in self.blk_list:
            blk.draw()
        # Экран буфера
        pygame.display.flip()
if __name__ == "__main__":
    Tetris(16,30).run()