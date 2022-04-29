import pygame
import threading
from Constant import *

class Control(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.pressed_once = False

    def update(self):
        pass

    def hover(self):
        pass

    def exit(self):
        pass

    def click(self):
        pass
    
    def stop_click(self):
        pass


class MousePointer(pygame.sprite.Sprite):
    """Simple class that provides an invisible rect for the pointer
    Used for easily identify collisions with the mouse pointer

    Methods
    -------
    update(self) :
        Updates the position of the rect in the coordenates of the mouse    
    """

    def __init__(self,size:tuple):
        super().__init__()

        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x, self.rect.y = pygame.mouse.get_pos()


class CircularButton(Control):

    def __init__(self,x,y,radius:int,image_size:int,image_path:str='',border:bool=True,background:tuple=DARK_BLACK,hover_background:tuple=LIGHT_BLACK_1,click_background:tuple=GREEN,id='Circle'):
        super().__init__()
        self.id = id
        self.actual_background = background
        self.button_background = background
        self.button_hover_background = hover_background
        self.button_click_background = click_background

        self.border = border
        self.radius = radius
        self.image_size = image_size
        self.click_function = None
        
        # Controlls that only 1 time the button gets pressed
        self.pressed_once = False
        self.ignore_multiple_click = False

        # The main surface gets created
        self.image = pygame.Surface((radius*2,radius*2))
        self.image.fill(DARK_BLACK)
        self.rect = self.image.get_rect(x=x,y=y,width=radius*2,height=radius*2)

        # Icon of button
        self.icon = None
        if image_path:
            self.icon = pygame.image.load(image_path)
            self.icon_rect = self.icon.get_rect(x=x,y=y,width=image_size,height=image_size)
            self.icon = pygame.transform.scale(self.icon,(image_size,image_size))

        # Circle of the outline
        if border: pygame.draw.circle(self.image,WHITE,(self.radius,self.radius), self.radius,width=1)

    def update(self):
        # Background and icon
        pygame.draw.circle(self.image,self.actual_background,(self.radius,self.radius), self.radius-1 if self.border else self.radius)
        if self.icon != None: self.image.blit(self.icon,(self.radius-self.image_size/2,self.radius-self.image_size/2))

    def hover(self):
        self.actual_background = self.button_hover_background

    def exit(self):
        self.actual_background = self.button_background

    def set_ignore_multiple_click(self):
        self.ignore_multiple_click = True

    def click(self):
        if not self.pressed_once:
            self.actual_background = self.button_click_background
            action_thread = threading.Thread(target=self.click_function())
            action_thread.start()
            if not self.ignore_multiple_click: self.pressed_once = True

class Text():

    def __init__(self,position,text:str='Some Text',small_font=False):
        self.text = text
        self.position = position
        self.small_font = small_font
        if small_font: self.render = SMALL_FONT.render(self.text, True, WHITE)
        else: self.render = FONT.render(self.text, True, WHITE)

    def update(self,new_text):
        self.text = new_text
        if self.small_font: self.render = SMALL_FONT.render(self.text, True, WHITE)
        else: self.render = FONT.render(self.text, True, WHITE)

    def print(self,window):
        window.blit(self.render,self.position)


class Slider():

    def __init__(self,x:int,y:int,width:int,min:int=0,max:int=1):
        super().__init__()
        self.slider_background = DARK_BLACK
        self.corner_radius = 5
        self.width = width

        # The main surface gets created
        self.slider_surface = pygame.Surface((width,self.corner_radius*4))
        self.slider_surface.fill(DARK_BLACK)
        self.rect = self.slider_surface.get_rect(x=x,y=y,width=width,height=self.corner_radius*4)

        # Values of the slider between the limits
        self.value = 0.5

        # Coordenates values
        self.y_center = self.corner_radius*2
        self.reference_rectangle_width = self.width/2 - self.corner_radius

        # Drag circular button
        self.drag_button_group = pygame.sprite.Group()
        self.drag_button = CircularButton(self.rect.x+(self.rect.width/2)-self.corner_radius*2, self.rect.y, self.corner_radius*2, 0, background=WHITE, hover_background=WHITE, click_background=GRAY, border=False, id='Drag Button')
        self.drag_button.set_ignore_multiple_click() # Allow to drag the button while keep pressing the click
        self.drag_button_group.add(self.drag_button)

        # Base geometric shapes
        pygame.draw.circle(self.slider_surface,WHITE,(  self.corner_radius,             self.y_center), self.corner_radius)
        pygame.draw.circle(self.slider_surface,WHITE,(  self.width-self.corner_radius,  self.y_center), self.corner_radius,width=1)
        pygame.draw.rect(self.slider_surface,WHITE,[    self.corner_radius,             self.y_center-self.corner_radius,  self.rect.width-self.corner_radius*2,  self.corner_radius*2 ],width=1)
        # Circle to hide the intersection between the right circle corner and the rect
        pygame.draw.rect(self.slider_surface,DARK_BLACK,[self.width-self.corner_radius*2, self.corner_radius*1.5-1, self.corner_radius*1.5, (self.corner_radius*2)-2])
        # Texts
        self.value_text = Text((self.rect.x+(self.width/2)-(FONT.size('0.500')[0]/2), self.rect.y+(self.corner_radius*4)+10),"0.500")
        self.texts = [
            Text((self.rect.x+5, self.rect.y+(self.corner_radius*4)+8.5),"0's",small_font=True),
            Text((self.rect.x+self.width-self.corner_radius-15, self.rect.y+(self.corner_radius*4)+8.5),"1's",small_font=True),
            self.value_text
        ]

        # Defines the limits of the drag button
        self.min_limit = self.rect.x
        self.max_limit = self.rect.x+self.rect.width - self.corner_radius*2


    def draw(self,window):
        for text in self.texts:
            text.print(window)
        
        window.blit(self.slider_surface,self.rect)
        pygame.draw.rect(window,WHITE,[self.rect.x + self.corner_radius,self.rect.y+self.corner_radius,self.reference_rectangle_width,self.corner_radius*2])

    def update_value(self):
        if self.reference_rectangle_width > 0.0:
            self.value = self.reference_rectangle_width/(self.width-self.corner_radius*2)
        else: self.value = 0.0
        self.value_text.update('{:.3f}'.format(self.value))

    def get_drag_button(self):
        return self.drag_button

    def move_drag_button(self,x):
        x -= self.corner_radius*2
        if (x <= self.max_limit) and (x >= self.min_limit):
            self.reference_rectangle_width = x - self.rect.x
            self.drag_button.rect.x = x
            self.update_value()

class Input(Control):

    def __init__(self,x,y,height,width:int=200,padding:int=5,label:str='Label',value:str='',allow_focus=False,background_color=LIGHT_BLACK_1):
        super().__init__()
        # The main surface gets created
        self.image = pygame.Surface((width,height))
        self.image.fill(DARK_BLACK)
        self.rect = self.image.get_rect(x=x,y=y,width=width,height=height)

        self.on_focus = False
        self.allow_focus = allow_focus

        self.clicked_function = lambda:print('clicked')
        self.new_character_function = None
        self.already_clicked = False

        # Label
        self.label_text = label
        self.label = Text((0,(height-FONT.size(label)[1])/2),label)
        self.label.print(self.image)
        # Background rectangle
        self.background_color = background_color
        self.background_rect_rect = pygame.Rect(FONT.size(label)[0]+2*padding,padding,width-FONT.size(label)[0]-2*padding,height-2*padding)
        # Input text
        self.value = value
        self.value_text = Text((self.rect.x+self.background_rect_rect.x+padding, self.rect.y+padding),self.value)
    #
    # Control methods
    #
    def draw(self,window):
        pygame.draw.rect(self.image,self.background_color,self.background_rect_rect)
        pygame.draw.rect(self.image,BLUE if self.on_focus else LIGHT_BLACK_1 ,self.background_rect_rect,1)
        self.value_text.print(window)

    def click(self):
        if not self.already_clicked:
            self.clicked_function()
            self.already_clicked = True

    def stop_click(self):
        self.already_clicked = False

    def has_on_focus(self):
        return self.allow_focus

    #
    # Auxiliar functions
    # 
    def set_on_focus(self):
        self.on_focus = True

    #
    # External configuration methods
    # 
    def new_character(self,character):
        if character == -1: 
            if len(self.value) : self.value = self.value[:-1]
        else: self.value += character
        self.value_text.update(self.value)
        # Executes a function if specified when a new character gets processed into the value text
        if self.new_character_function != None: self.new_character_function()

    def set_click_function(self,function):
        self.clicked_function = function

class Section():

    def __init__(self,x,y,width,padding,title):
        self.header_surface = pygame.Surface((width,30))
        self.header_surface.fill(LIGHT_BLACK_1)
        self.header_rect = self.header_surface.get_rect(x=x,y=y,width=width,height=30)

        # The title of the section
        self.title_text = Text((padding,9),title,small_font=True)
        self.title_text.print(self.header_surface)
    
    def draw(self,window):
        window.blit(self.header_surface,self.header_rect)