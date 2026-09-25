import pygame as pyg
import serverside as servside
import clientside as cliside
import os
import threading as th
import sys
import platform as plt

#       model : 1.0.s (static)
#           this model does not save the users data (chips, cards, ect.), thus why Its called static.
#           for that we need to figure out how databases work (I dont wanna do that yet).
#           also most databases cost money and since we need a database for both servers and users, it would become really slow as well.
#           maybe look into it later Idk, but I will use a static version for now

pyg.init()
canvas = pyg.display.set_mode((1200, 675), pyg.RESIZABLE)
clock = pyg.time.Clock()
server = servside.server()
client = cliside.client("Ege")
def newpath(path = str):
    if plt.system() == "Windows":
        return os.getcwd().encode() + path.encode()
    elif plt.system() == "Darwin":
        return os.getcwd().encode() + str(path.replace("\\", "/")).encode()


class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pyg.image.load(filename).convert_alpha()

    def get_image(self, corner1, corner2):
        rect = pyg.Rect(corner1[0], corner1[1], corner2[0], corner2[1])
        image = self.sheet.subsurface(rect)
        return image


class Cards:
    def __init__(self, dispsurface = canvas, sprites = bytes, setstate = int):
        self.sprites = SpriteSheet(sprites)
        self.dispsurface = dispsurface
        self.setstate = setstate

    def display(self, cardcode, location, scale, state):
        card = self.sprites.get_image((cardcode[0]*18, cardcode[1]*22), (18, 22))
        if state == self.setstate:
            self.dispsurface.blit(pyg.transform.scale(card, (card.get_width()*scale, card.get_height()*scale)), (location[0], location[1]))

    

class Button:
    def __init__(self, dispsurface = canvas, sprites = bytes, setstate = int):
        self.canvas = dispsurface
        self.spritesheet = sprites
        self.pressed = 0
        self.setstate = setstate
    
    def display(self, sprtcords = list, dsplycords = tuple, scale = int, screenstate = int):
        button = SpriteSheet(self.spritesheet).get_image(sprtcords[0][0], sprtcords[0][1])
        button = pyg.transform.scale(button, (button.get_width()*scale, button.get_height()*scale))

        button_h = SpriteSheet(self.spritesheet).get_image(sprtcords[1][0], sprtcords[1][1])
        button_h = pyg.transform.scale(button_h, (button_h.get_width()*scale, button_h.get_height()*scale))

        button_d = SpriteSheet(self.spritesheet).get_image(sprtcords[2][0], sprtcords[2][1])
        button_d = pyg.transform.scale(button_d, (button_d.get_width()*scale, button_d.get_height()*scale))


        mousepos = pyg.mouse.get_pos()
        if self.setstate == screenstate:
            
            if mousepos[0] >= dsplycords[0] and mousepos[0] <= dsplycords[0] + button.get_width() and mousepos[1] >= dsplycords[1] and mousepos[1] <= dsplycords[1] + button.get_height():
                """
                if button.get_rect().collidepoint(mousepos[0], mousepos[1]):
                """
                if pyg.mouse.get_pressed()[0]:
                    self.canvas.blit(button_d, dsplycords)
                    self.pressed = 1
                else:
                    self.canvas.blit(button_h, dsplycords)
                    self.pressed = 0
            else:
                self.canvas.blit(button, dsplycords)


class textinpbox:
    def __init__(self, dispsurface = canvas, fontsize = 28, colors = [(0, 212, 56), (153, 3, 16)], setstate = int):
        self.Font = pyg.font.Font(None, fontsize)
        self.usertext = ""
        self.passiveRGB = colors[0]
        self.activeRGB = colors[1]
        self.active = False
        self.setstate = setstate
        self.canvas = dispsurface

    def display(self, dsplycords = tuple, scale = int, screenstate = int):
        self.InpRect = pyg.Rect(dsplycords[0][0], dsplycords[0][1], dsplycords[1][0], dsplycords[1][1])
        text_surface = self.Font.render(self.usertext, True, (255, 255, 255))
        if self.setstate == screenstate:
            self.TextInpOutline = pyg.Rect(dsplycords[0][0] - 4, dsplycords[0][1] - 4, dsplycords[1][0] + 8, dsplycords[1][1] + 8)
            self.InpRect.w = max(100, text_surface.get_width()+10)
            self.TextInpOutline.w = max(108, text_surface.get_width()+18)
            pyg.draw.rect(self.canvas, (0,0,0), self.TextInpOutline)
            if self.active:
                pyg.draw.rect(self.canvas, self.activeRGB, self.InpRect)
            else:
                pyg.draw.rect(self.canvas, self.passiveRGB, self.InpRect)

            canvas.blit(text_surface, (self.InpRect.x+5, self.InpRect.y+4))
    

class Chips:
    def __init__(self, dispsurface = canvas, sprites = bytes, setstate = int):
        self.canvas = dispsurface
        self.spritesheet = sprites
        self.setstate = setstate
        self.converterlib = {
            1 : (1,1),
            2 : (1,2), 
            3 : (1,3),
            4 : (1,4),
            5 : (2,1),
            6 : (2,2),
            7 : (2,3),
            8 : (2,4)
        }

    """     CHIP MATRIX
                1, 5
                2, 6
                3, 7
                4, 8
    """

    #   a chip is 128 x 120 pixels
    def display(self, chiptype = int, dsplycords = tuple, amount = int, scale = int, screenstate = int):
        if screenstate == self.setstate:
            ctype = self.converterlib[chiptype]
            typespritecords = [[(ctype[0]-1)*128, (ctype[1]-1)*120], [128,120]]
            chip = SpriteSheet(self.spritesheet).get_image(typespritecords[0], typespritecords[1])
            chip = pyg.transform.scale(chip, (chip.get_width()*scale, chip.get_height()*scale))
            a = amount
            while a > 0:
                self.canvas.blit(chip, (dsplycords[0], dsplycords[1] + scale*(a)*10))
                a -= 1

def strtservth():
    senderth = th.Thread(target=server.sender)
    receiverth = th.Thread(target=server.reciever)
    joinhqueueth = server.joinhqueue


#   ex : display([[x1, y1], [x2, y2]], (xd, yd), 5)
        
def start():
    run = True
    # Cards are 22 x 18 pixels, ratio is 11/9; the area for the cards is 234 x 110.
    state = 1
    #   1 : mainmenu, 2 : entering details to join, 3 : poker table, 4 : host details, 5 : hosting and joined as admin (can set anyones chip count in terminal)
    hostB = Button(canvas, newpath("\\assets\\sprtsheet.png"), 1)
    joinB = Button(canvas, newpath("\\assets\\sprtsheet.png"), 1)
    mainmenu = pyg.image.load(newpath("\\assets\\Mainmenu.png"))
    Chip = Chips(canvas, newpath("\\assets\\chips.png"), 2)
    textbox = textinpbox(canvas, 28, [(0, 212, 56), (153, 3, 16)], 2)
    while run:
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                run = False
            if event.type == pyg.MOUSEBUTTONUP:
                if joinB.pressed == 1:
                    state = 2

                if textbox.InpRect.collidepoint(event.pos):
                    textbox.active = True
                else:
                    textbox.active = False


            if event.type == pyg.KEYDOWN:
                if textbox.active:
                    if event.key == pyg.K_BACKSPACE:
                        textbox.usertext = textbox.usertext[:-1]
                    elif event.key == 13:
                        textbox.active = False
                    else:
                        textbox.usertext += event.unicode

                if event.key == pyg.K_p and not textbox.active:
                    run = False
                    pyg.quit()
                    quit()

                
            if event.type == pyg.KEYDOWN:
                pass


        if state == 1:
            canvas.blit((pyg.transform.scale(mainmenu, (canvas.get_width(), canvas.get_height()))), (0,0))
        elif state == 2:
            canvas.fill((0, 130, 60))


        S = 2.5
        joinB.display([
                    [[0,110], [115, 36]],
                    [[0, 146], [115, 36]],
                    [[0, 182], [115, 36]]
                    ], (canvas.get_width()/2 - 115*S/2, canvas.get_height()/2 - 36*S/2), S, state)
        
        hostB.display([
                    [[119,110], [115, 36]],
                    [[119, 146], [115, 36]],
                    [[119, 182], [115, 36]]
                    ], (canvas.get_width()/2 - 115*S/2, canvas.get_height()/2 - 36*S/2 + 110), S, state)

        #Chip.display(8, (200, 200), 10, 0.75, state)
        #Chip.display(6, (240, 280), 5, 0.3, state)
        #Chip.display(2, (260, 300), 5, 0.3, state)

        textbox.display(([500,300],(100,30)), 1, state)

        pyg.display.flip()
    pyg.quit()

if __name__ == "__main__":
    start()