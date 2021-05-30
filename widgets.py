import time
import pygame
from pygame.locals import *
from abc import ABC, abstractmethod
from containers import Container

"""
Widgets:
- Button
- Slider
- Entry
- Text Box
- Scrollbar
- Frame
- Window
- Tabs

Widget Procedures:
- draw
- event_handler

Widget Properties:
- container
- position
- width
- bg color
- fg color
- font-name
- font-size
- figure
- scroll
"""


class Widget(ABC):

    def __init__(self, container: Container, pos: tuple = (), dims: tuple = (),
                 bg_color: tuple = (255, 255, 255), font_color: tuple = (0, 0, 0), font_name: str = 'times',
                 font_size: int = 30,
                 text: str = ''):
        self.container = container
        if self.container.coordinate_system == 'regular':
            self.pos = pos
            self.dims = dims
        elif self.container.coordinate_system == 'relative':
            self.pos = [self.container.surface.get_width() * pos[0] // 100,
                        self.container.surface.get_height() * pos[1] // 100]
            self.dims = [self.container.surface.get_width() * dims[0] // 100,
                         self.container.surface.get_height() * dims[1] // 100]
        self.bg_color = bg_color
        self.font_color = font_color
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text = text
        self.figure = None
        self.pack()

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def process(self, event):
        pass

    def pack(self):
        self.container.widget_list.append(self)

    def unpack(self):
        self.container.widget_list.remove(self)


class Button(Widget):

    def __init__(self, container: Container, pos: tuple = (), dims: tuple = (), command=None,
                 bg_color: tuple = (255, 255, 255), font_color: tuple = (0, 0, 0),
                 font_name: str = 'times', font_size: int = 30, text: str = ''):
        super().__init__(container=container, pos=pos, dims=dims, bg_color=bg_color, font_color=font_color,
                         font_name=font_name, font_size=font_size,
                         text=text)
        if len(self.pos) == 0:
            self.pos = (0, 0)
        if len(self.dims) == 0:
            if self.container.coordinate_system == 'regular':
                self.dims = self.font.size(self.text)
            elif self.container.coordinate_system == 'relative':
                self.dims = (100 * self.font.size(self.text)[0] // self.container.surface.get_width(), 100 * self.font.size(self.text)[1] // self.container.surface.get_height)
        self.command = command

    def draw(self):
        self.figure = pygame.draw.rect(self.container.surface, self.bg_color, self.pos + self.dims)
        self.container.surface.blit(self.font.render(self.text, False, self.font_color), self.pos)

    def process(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.figure.collidepoint(event.pos):
            self.command()


class Slider(Widget):

    def __init__(self, container: Container, pos: tuple = (), dims: tuple = (),
                 orientation: str = 'horizontal',
                 bg_color: tuple = (255, 255, 255), font_color: tuple = (255, 255, 255), font_name: str = 'times',
                 font_size: int = 30,
                 text: str = '', scale: range = range(0, 10, 1), label: bool = True, cast: type = int):
        super().__init__(container=container, pos=pos, dims=dims, bg_color=bg_color, font_color=font_color,
                         font_name=font_name, font_size=font_size,
                         text=text)
        if len(self.pos) == 0:
            self.pos = (0, 0)
        if len(self.dims) == 0:
            if self.container.coordinate_system == 'regular':
                if orientation == 'horizontal':
                    self.dims = (10 * (scale.stop - scale.start), 10)
                elif orientation == 'vertical':
                    self.dims = (10, 10 * (scale.stop - scale.start))
            elif self.container.coordinate_system == 'relative':
                if orientation == 'horizontal':
                    self.dims = (10, 5)
                elif orientation == 'vertical':
                    self.dims = (5, 10)
        self.scale = scale
        self.clicked = False
        self.label = label
        self.cast = cast
        self.orientation = orientation
        if self.orientation == 'horizontal':
            self.current_pos = self.pos[0]
        elif self.orientation == 'vertical':
            self.current_pos = self.pos[1]

    def draw(self):
        if self.orientation == 'horizontal':
            self.figure = pygame.draw.circle(self.container.surface, self.bg_color, [self.current_pos, self.pos[1]],
                                             self.dims[1] // 2)
            pygame.draw.line(self.container.surface, self.bg_color, self.pos, [self.pos[0] + self.dims[0], self.pos[1]],
                             2)
            if self.label:
                self.container.surface.blit(self.font.render(str(self.scale.start), False, self.font_color), self.pos)
                self.container.surface.blit(self.font.render(str(self.scale.stop), False, self.font_color),
                                            [self.pos[0] + self.dims[0], self.pos[1]])
                self.container.surface.blit(
                    self.font.render('{}: {}'.format(self.text, self.get_val()), False, self.font_color),
                    [self.pos[0], self.pos[1] + self.dims[1] + self.font.get_height()])
        elif self.orientation == 'vertical':
            self.figure = pygame.draw.circle(self.container.surface, self.bg_color, [self.pos[0], self.current_pos],
                                             self.dims[0] // 2)
            pygame.draw.line(self.container.surface, self.bg_color, self.pos, [self.pos[0], self.pos[1] + self.dims[1]],
                             2)
            if self.label:
                self.container.surface.blit(self.font.render(str(self.scale.start), False, self.font_color), self.pos)
                self.container.surface.blit(self.font.render(str(self.scale.stop), False, self.font_color),
                                            [self.pos[0], self.pos[1] + self.dims[1]])
                self.container.surface.blit(
                    self.font.render('{}: {}'.format(self.text, self.get_val()), False, self.font_color),
                    [self.pos[0], self.pos[1] + self.dims[1] + self.font.get_height()])

    def process(self, event: pygame.event.Event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.figure.collidepoint(event.pos):
            self.clicked = True
        elif event.type == MOUSEBUTTONUP and event.button == 1 and self.clicked:
            self.clicked = False
        elif event.type == MOUSEMOTION and self.clicked:
            if self.orientation == 'horizontal':
                if self.pos[0] <= event.pos[0] <= self.pos[0] + self.dims[0]:
                    self.current_pos = event.pos[0]
                elif event.pos[0] > self.pos[0] + self.dims[0]:
                    self.current_pos = self.pos[0] + self.dims[0]
                elif event.pos[0] < self.pos[0]:
                    self.current_pos = self.pos[0]
            elif self.orientation == 'vertical':
                if self.pos[1] <= event.pos[1] <= self.pos[1] + self.dims[1]:
                    self.current_pos = event.pos[1]
                elif event.pos[1] > self.pos[1] + self.dims[1]:
                    self.current_pos = self.pos[1] + self.dims[1]
                elif event.pos[1] < self.pos[1]:
                    self.current_pos = self.pos[1]

    def get_val(self):
        if self.orientation == 'horizontal':
            return self.cast(
                self.scale.start + (self.scale.stop - self.scale.start) * (self.current_pos - self.pos[0]) / self.dims[
                    0])
        elif self.orientation == 'vertical':
            return self.cast(
                self.scale.start + (self.scale.stop - self.scale.start) * (self.current_pos - self.pos[1]) / self.dims[
                    1])
        return 0


class Entry(Widget):

    def __init__(self, container: Container, pos: tuple = (), dims: tuple = (),
                 bg_color: tuple = (255, 255, 255), font_color: tuple = (0, 0, 0), font_name: str = 'times',
                 font_size: int = 30, text: str = ''):
        super().__init__(container=container, pos=pos, dims=dims, bg_color=bg_color, font_color=font_color,
                         font_name=font_name, font_size=font_size,
                         text=text)
        if len(self.pos) == 0:
            self.pos = (0, 0)
        if len(self.dims) == 0:
            if self.container.coordinate_system == 'regular':
                self.dims = (100, 30)
            elif self.container.coordinate_system == 'relative':
                self.dims = (10, 5)
        self.clicked = False
        self.caps = False
        self.index = 0
        self.flash = 0
        self.freq = 0.5
        self.display = False
        self.text = list(self.text)
        self.table = {
            ord('1'): '!',
            ord('2'): '@',
            ord('3'): '#',
            ord('4'): '$',
            ord('5'): '%',
            ord('6'): '^',
            ord('7'): '&',
            ord('8'): '*',
            ord('9'): '(',
            ord('0'): ')',
            ord('-'): '_',
            ord('='): '+',
            ord('['): '{',
            ord(']'): '}',
            ord(';'): ':',
            ord("'"): '"',
            ord(','): '<',
            ord('.'): '>',
            ord('/'): '?',
        }

    def get_text(self) -> str:
        return ''.join(self.text)

    def set_text(self, text: str):
        self.text = list(text)

    def process(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.figure.collidepoint(event.pos):
                self.clicked = True
            else:
                self.clicked = False
        elif self.clicked and event.type == KEYDOWN:
            if event.key == K_LSHIFT or event.key == K_RSHIFT:
                self.caps = True
            elif event.key == K_RIGHT and self.index < len(self.text):
                self.index += 1
            elif event.key == K_LEFT and self.index > 0:
                self.index -= 1
            elif event.key == K_BACKSPACE and len(self.text) > 0 and self.index > 0:
                self.index -= 1
                self.text.pop(self.index)
            else:
                try:
                    if self.caps:
                        if chr(event.key) != chr(event.key).upper():
                            self.text.insert(self.index, chr(event.key).upper())
                        else:
                            self.text.insert(self.index, chr(event.key).translate(self.table))
                    else:
                        self.text.insert(self.index, chr(event.key))
                    self.index += 1
                except ValueError:
                    pass
        elif self.clicked and event.type == KEYUP:
            if event.key == K_RSHIFT or event.key == K_LSHIFT:
                self.caps = False

    def draw(self):
        self.figure = pygame.draw.rect(self.container.surface, self.bg_color, self.pos + self.dims)
        size = self.font.size(''.join(self.text[:self.index]))[0]
        if len(self.text) > 0:
            try:
                self.container.surface.blit(self.font.render(''.join(self.text), False, self.font_color), self.pos)
            except pygame.error:
                pass
        if self.clicked:
            if time.time() - self.flash >= self.freq:
                self.display = not self.display
                self.flash = time.time()
            if self.display:
                pygame.draw.line(self.container.surface, self.font_color,
                                 (size + self.pos[0], self.pos[1]),
                                 (size + self.pos[0], self.pos[1] + self.dims[1]), 2)