import pygame
from pygame.locals import *

pygame.init()


screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Button Demo')

font = pygame.font.SysFont('Source Sans Pro', 30)

#define colours
bg = (204, 102, 0)
blue = (255, 255, 0)
black = (0, 0, 0)

#define global variable
clicked = False
counter = 0

class button():

	#colours for button and text
	button_col = (217,154,79)
	hover_col = (236,161,84)
	click_col = ((203,160,82))
	text_col = black
	width = 120
	height = 50

	def __init__(self, x, y, text):
		self.x = x
		self.y = y
		self.text = text

	def draw_button(self):

		global clicked
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#create pygame Rect object for the button
		button_rect = Rect(self.x, self.y, self.width, self.height)

		#check mouseover and clicked conditions
		if button_rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				clicked = True
				pygame.draw.rect(screen, self.click_col, button_rect)
			elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
				clicked = False
				action = True
			else:
				pygame.draw.rect(screen, self.hover_col, button_rect)
		else:
			pygame.draw.rect(screen, self.button_col, button_rect)


		#add text to button
		text_img = font.render(self.text, True, self.text_col)
		text_len = text_img.get_width()
		screen.blit(text_img, (self.x + int(self.width / 2) - int(text_len / 2), self.y + 15))
		return action
