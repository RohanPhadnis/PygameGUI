import pygame
from pygame.locals import *
from widgets import Button


class Container:

    def __init__(self, system: str = 'regular', bg_color: tuple = (0, 0, 0)):
        self.container = None
        self.surface = None
        self.widget_list = []
        self.bg_color = bg_color
        self.coordinate_system = system

    def draw(self):
        self.surface.fill(self.bg_color)
        for w in self.widget_list:
            w.draw()


class Frame(Container):

    def __init__(self, container: Container, pos: tuple = (), dims: tuple = (), system: str = 'regular', bg_color: tuple = (0, 0, 0), title: str = ''):
        super().__init__(system=system, bg_color=bg_color)
        self.container = container
        if len(pos) == 0 or len(dims) == 0:
            if len(pos) == 0:
                self.pos = (0, 0)
            if len(dims) == 0:
                if self.container.coordinate_system == 'regular':
                    self.dims = (200, 200)
                elif self.container.coordinate_system == 'relative':
                    self.dims = (20, 20)
        else:
            if self.container.coordinate_system == 'regular':
                self.pos = pos
                self.dims = dims
            elif self.container.coordinate_system == 'relative':
                self.pos = (self.container.surface.get_width() * pos[0] // 100,
                            self.container.surface.get_height() * pos[1] // 100)
                self.dims = (self.container.surface.get_width() * dims[0] // 100,
                             self.container.surface.get_height() * dims[1] // 100)
        self.surface = pygame.Surface(self.dims)
        self.title = title
        self.pack()

    def draw(self):
        super(Frame, self).draw()
        self.container.surface.blit(self.surface, self.pos)

    def process(self, event):
        try:
            event.pos = (event.pos[0] - self.pos[0], event.pos[1] - self.pos[1])
        except AttributeError:
            pass
        for w in self.widget_list:
            w.process(event)

    def pack(self):
        self.container.widget_list.append(self)

    def unpack(self):
        self.container.widget_list.remove(self)


class Tabs(Container):

    def __init__(self, container: Container, frames=None):
        super().__init__()
        if frames is None:
            frames = []
        if container.coordinate_system == 'regular':
            self.container = Frame(container, pos=(0, 0), dims=(container.surface.get_width(), container.surface.get_height()), bg_color=container.bg_color)
        elif container.coordinate_system == 'relative':
            self.container = Frame(container, pos=(0, 0),
                                   dims=(100, 100),
                                   bg_color=container.bg_color)
        self.widget_list = frames
        self.surface = pygame.surface.Surface((self.container.surface.get_width(), self.container.surface.get_height()))
        self.button_frame = Frame(self.container, pos=(0, 0))
        self.buttons = [Button(self.button_frame, text=frames[n].title, font_size=15) for n in range(len(frames))]
        for n in range(1, len(self.buttons)):
            self.buttons[n].pos = (self.buttons[n-1].pos[0] + self.buttons[n-1].dims[0], 0)
        if len(self.buttons) > 0:
            self.button_frame.dims = (self.buttons[-1].pos[0] + self.buttons[-1].dims[0], self.buttons[-1].dims[1])
        else:
            self.button_frame.dims = (0, 0)
        self.active = 0

    def add_frame(self, frame):
        self.widget_list.append(frame)
        if len(self.buttons) > 0:
            self.buttons.append(Button(self.button_frame, pos=(self.buttons[-1].pos[0] + self.buttons[-1].dims[0], 0), text=frame.title, font_size=15))
            self.button_frame.dims = (self.buttons[-1].pos[0] + self.buttons[-1].dims[0], self.buttons[-1].dims[1])
        else:
            self.buttons.append(Button(self.button_frame, text=frame.title, font_size=15))
            self.button_frame.dims = (self.buttons[-1].pos[0] + self.buttons[-1].dims[0], self.buttons[-1].dims[1])

    def draw(self):
        self.widget_list[self.active].draw()
        self.button_frame.draw()


class Window(Container):

    def __init__(self, dims: tuple, title: str = '', system: str = 'regular', bg_color: tuple = (0, 0, 0)):
        super().__init__(system=system, bg_color=bg_color)
        self.dims = dims
        self.title = title
        pygame.init()
        self.surface = pygame.display.set_mode(self.dims)
        pygame.display.set_caption(self.title)

    def draw(self):
        super(Window, self).draw()
        pygame.display.update()

    def process(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            for w in self.widget_list:
                w.process(event)