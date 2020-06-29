import pdb
import constants
import pygame
import math
import copy
import sys
class Block(object):
    """
    Класс обработки фигур тетриса.
    """    
    def __init__(self,shape,x,y,screen,color,rotate_en):
        """
        Инициализация фигуры
        Параметры:
            - shape - Список информации о фигурах. Содержит [X,Y] координаты блоков
            - x - X Координата первого блока в фигуре
            - y - Y Координата первого блока в фигуре
            - screen  - экран прорисовки
            - color - цвет фигуры в RGB палитре
            - rotate_en - включение и выключение поворота фигуры
        """
        # Инициализация фигуры (все преобразовывается в Rect объекты)
        self.shape = []
        for sh in shape:
            bx = sh[0]*constants.BWIDTH + x
            by = sh[1]*constants.BHEIGHT + y
            block = pygame.Rect(bx,by,constants.BWIDTH,constants.BHEIGHT)
            self.shape.append(block)     
        # Установка атрибутов вращения
        self.rotate_en = rotate_en
        # Установка остальных переменных
        self.x = x
        self.y = y
        # Передвижение по X,Y координатам
        self.diffx = 0
        self.diffy = 0
        # Экран прорисовки
        self.screen = screen
        self.color = color
        # Поворот экрана
        self.diff_rotation = 0
    def draw(self):
        """
        Изображение блоков. Каждый состоит из определенного цвета и черной рамки.
        """
        for bl in self.shape:
            pygame.draw.rect(self.screen,self.color,bl)
            pygame.draw.rect(self.screen,constants.BLACK,bl,constants.MESH_WIDTH)       
    def get_rotated(self,x,y):
        """
        Вычисление новых координат, основываяь на направлении поворота    
        Параметры:
            - x - X координата переноса
            - y - Y координата переноса
        Возвращение списка с новыми (X,Y) координатами.
        """
        # Используем классическую матрицу преобразования:
        rads = self.diff_rotation * (math.pi / 180.0)
        newx = x*math.cos(rads) - y*math.sin(rads)
        newy = y*math.cos(rads) + x*math.sin(rads)
        return (newx,newy)        

    def move(self,x,y):
        """
        Перемещение, используя заданное смещение        
       Параметры:
            - x - перемещение по координате X
            - y - перемещение по координате Y
        """
        # Накопление координат X,Y и вызов функции накопления     
        self.diffx += x
        self.diffy += y  
        self._update()
    def remove_blocks(self,y):
        """
        Удалить блоки по координате Y Все блоки
        выше Y будут сдвинуты на один вниз.
        Параметры:
            - y - Y координаты для работы с ними.
        """
        new_shape = []
        for shape_i in range(len(self.shape)):
            tmp_shape = self.shape[shape_i]
            if tmp_shape.y < y:
                # Блоки выше y будут двигаться вниз и будут добавлены в список активных фигур.
                new_shape.append(tmp_shape)  
                tmp_shape.move_ip(0,constants.BHEIGHT)
            elif tmp_shape.y > y:
                # Блоки ниже y будут добавлены в список. Не будут перемещаться, так так не должны.
                new_shape.append(tmp_shape)
        # Установка нового списка блоков.
        self.shape = new_shape
    def has_blocks(self):
        """
        Возвращает true если блок имеет блоки фигуры в списке фигур.
        """    
        return True if len(self.shape) > 0 else False

    def rotate(self):
        """
        Устанавливаем градус вращения (90)
        """
        # Устанавливаем вращение и обновляем координаты всех фигур
        # Фигура вращается, если это возможно
        if self.rotate_en:
            self.diff_rotation = 90
            self._update()
    def _update(self):
        """
       Обновление позиций блоков
        """
        for bl in self.shape:
            # Получаем старые координаты x,y и вычисляем новые. 
            # Все расчеты выполняются в исходных координатах.
            origX = (bl.x - self.x)/constants.BWIDTH
            origY = (bl.y - self.y)/constants.BHEIGHT
            rx,ry = self.get_rotated(origX,origY)
            newX = rx*constants.BWIDTH  + self.x + self.diffx
            newY = ry*constants.BHEIGHT + self.y + self.diffy
            # Вычисление движений
            newPosX = newX - bl.x
            newPosY = newY - bl.y
            bl.move_ip(newPosX,newPosY)
        # Если все сдвинулось. Установить новые x,y, координаты и обнулить переменные движения
        self.x += self.diffx
        self.y += self.diffy
        self.diffx = 0
        self.diffy = 0
        self.diff_rotation = 0
    def backup(self):
        """
       Резерв текущей конфигурации фигур.
        """
        # Полностью копировать список фигур и запомнить текущую конфигурацию
        self.shape_copy = copy.deepcopy(self.shape)
        self.x_copy = self.x
        self.y_copy = self.y
        self.rotation_copy = self.diff_rotation     
    def restore(self):
        """
        Восстановить прежнюю конфигурацию
        """
        self.shape = self.shape_copy
        self.x = self.x_copy
        self.y = self.y_copy
        self.diff_rotation = self.rotation_copy
    def check_collision(self,rect_list):
        """
        Функция проверки на столкновение в списке фигур
        Параметры:
            - rect_list - функция принимает список Rect для обнаружения столкновений 
        """
        for blk in rect_list:
            collist = blk.collidelistall(self.shape)
            if len(collist):
                return True
        return False
