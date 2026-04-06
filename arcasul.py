# Python program to build an archery game
import os
from time import time
import pygame
import random
import math

pygame.init()

# Dimensions of the game window
WIDTH, HEIGHT = 1200, 700

# Standard Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Paths
BASE_DIR = os.path.join(os.path.dirname(__file__), "poze")
balloonPath = os.path.join(BASE_DIR, "balloon.png")
archerPath  = os.path.join(BASE_DIR, "arcas_moldovean.png")
arrowPath   = os.path.join(BASE_DIR, "arrow.png")
backgroundPath = os.path.join(BASE_DIR, "fundal_joc.jpg")
castlePath = os.path.join(BASE_DIR, "castel.png")

font = pygame.font.Font('freesansbold.ttf', 20)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balloon Archer")

# To control the frame rate
clock = pygame.time.Clock()
FPS = 30


class Archer:
    # init function to set the object variables and load the image
    def __init__(self, width, height, speed):
        self.width = width
        self.height = height
        self.speed = speed

        self.archer = pygame.transform.smoothscale(
            pygame.image.load(archerPath), (self.width, self.height))
        self.archerRect = self.archer.get_rect()

        # Default position (start near bottom, within bottom half)
        self.archerRect.x = 100
        self.archerRect.y = HEIGHT - self.archerRect.h

    # Method to render the archer on the screen
    def display(self):
        screen.blit(self.archer, self.archerRect)

    # Method to update the archer position
    def update(self, xFac, yFac):
        self.archerRect.x += xFac*self.speed
        # Allow vertical movement but limit to bottom half of the screen
        self.archerRect.y += yFac * self.speed
        min_y = HEIGHT // 2
        max_y = HEIGHT - self.archerRect.h
        if self.archerRect.y < min_y:
            self.archerRect.y = min_y
        elif self.archerRect.y > max_y:
            self.archerRect.y = max_y

        # Horizontal constraints: left margin and right limit at 2/3 of screen
        min_x = 0
        max_x = (2 * WIDTH) // 3 - self.archerRect.w
        if self.archerRect.x < min_x:
            self.archerRect.x = min_x
        elif self.archerRect.x > max_x:
            self.archerRect.x = max_x


# Balloon class consists of all the
# functionalities related to the balloons
class Balloon:
    # init function to set the object variables and load the image
    def __init__(self, posx, posy, width, height, speed, text=None, text_color=BLACK,
                 wobble=True, wobble_amp=3, wobble_period_ms=1200):
        
        self.width, self.height = width, height
        self.speed = speed

        self.balloonImg = pygame.image.load(balloonPath)

        self.balloon = pygame.transform.scale(
            self.balloonImg, (self.width, self.height))

        self.balloonRect = self.balloon.get_rect()

        # store a fixed base x so wobble oscillates around it
        self.base_x = posx
        self.balloonRect.x, self.balloonRect.y = posx, posy

        # wobble (horizontal oscillation) settings
        self.wobble = wobble
        self.wobble_amp = wobble_amp
        self.wobble_period_ms = wobble_period_ms
        self.wobble_phase = random.random() * 2 * math.pi

        # Optional text drawn over the balloon
        self.text = text
        self.text_color = text_color
        self.time = time()  # store creation time for potential future use (e.g., timed disappearance)

    # Method to render the balloon on the screen
    def display(self):
        screen.blit(self.balloon, self.balloonRect)

        # Draw optional text centered on the balloon
        if self.text is not None:
            try:
                text_surf = font.render(str(self.text), True, self.text_color)
                text_rect = text_surf.get_rect(center=self.balloonRect.center)
                screen.blit(text_surf, text_rect)
            except Exception as e:
                print(f"Error rendering balloon text: {e}")

    # Method to update the position of the balloon
    def update(self):
        # move up/down
        if time() - self.time > 1:  # change direction every 2 seconds
            self.speed *= -1
            self.balloonRect.y -= self.speed
            self.time = time()

        # horizontal wobble around base_x
        if self.wobble and self.wobble_period_ms > 0:
            t = pygame.time.get_ticks()
            angle = self.wobble_phase + (2 * math.pi * (t % self.wobble_period_ms) / self.wobble_period_ms)
            dx = int(self.wobble_amp * math.sin(angle))
            self.balloonRect.x = self.base_x + dx
                
        # If the balloon crosses the upper edge of the screen,
        # we put it back at the lower edge
        if self.balloonRect.y < 0:
            self.balloonRect.y = HEIGHT+10


# Arrow class consists of all the functions related to the arrows
class Arrow:
    # init function to set the object variables and load the image
    def __init__(self, posx, posy, width, height, speed):
        self.width, self.height = width, height
        self.speed = speed
        # Used to track if the arrow has hit any balloon
        self.hit = 0    

        self.arrow = pygame.transform.scale(pygame.image.load(arrowPath), (width, height))
        self.arrowRect = self.arrow.get_rect()

        # arrow coordinates
        self.arrowRect.x, self.arrowRect.y = posx, posy

    # Method to render the arrow on the screen
    def display(self):
        screen.blit(self.arrow, self.arrowRect)

    # Method to update the position of the arrow
    def update(self):
        self.arrowRect.x += self.speed

    # Method to update the hit variable
    def updateHit(self):
        self.hit = 1

    def getHit(self):
        return self.hit


class TextProblema:
    """Class to represent the multiplication problem text displayed on the castle."""
    def __init__(self, text, text_color=BLACK, blink=False, blink_interval_ms=100):
        self.text = text
        self.text_color = text_color
        self.blink = blink
        self.blink_interval_ms = blink_interval_ms

    def display(self):
        try:
            text_surf = font.render(str(self.text), True, self.text_color)
            text_rect = text_surf.get_rect(center=(screen.get_width() // 2, 0 + text_surf.get_height()))
            pygame.draw.rect(screen, (48, 141, 70), (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, 40), 7, 17)
            # Determine visibility based on time if blinking enabled
            visible = True
            if self.blink:
                t = pygame.time.get_ticks()
                visible = ((t // self.blink_interval_ms) % 2) == 0
            if visible:
                screen.blit(text_surf, text_rect)
        except Exception as e :
            print(f"Error rendering text problema: {e}")

class Castle:
    """Castle object that loads, scales and draws a castle image with optional text."""
    def __init__(self, path, max_width=150, x=20, y_offset=-50, text="Castel"):
        self.path = path
        self.text = text
        # self.text_color = text_color
        # self.blink = blink
        # self.blink_interval_ms = blink_interval_ms
        try:
            _img = pygame.image.load(self.path).convert_alpha()
        except Exception:
            self.image = None
            self.rect = pygame.Rect(0, 0, 0, 0)
            return

        # compute target width and scale preserving aspect ratio
        target_w = min(max_width, WIDTH // 6)
        ow, oh = _img.get_size()
        scale_h = int(oh * (target_w / ow)) if ow else oh
        self.image = pygame.transform.smoothscale(_img, (target_w, max(1, scale_h)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = HEIGHT//2 - self.rect.h//2 + y_offset

    def display(self, surface):
        if not self.image:
            return
        surface.blit(self.image, (self.rect.x, self.rect.y))


# Spawn the balloons
def populateBalloons(bWidth, bHeight, bSpeed, bCount, raspuns=None, optiuni=None):
    listOfBalloons = []
    
    # For the given count, spawn balloons at random
    # positions in the right third of the screen, bottom half,
    # ensuring a small gap between balloons (min_spacing pixels).
    min_spacing = 40
    max_attempts = 300

    # TODO sa fac asezarea baloanelor mai bine, sa tina cont de pozitionarea pe axa y mai bine,
    #       sa nu se suprapuna baloanele, 
    
    # helper to try find a free spot
    def find_spot():
        attempts = 0
        while attempts < max_attempts:
            x = random.randint((2*WIDTH)//3, WIDTH - bWidth)
            y = random.randint(HEIGHT // 2, HEIGHT - bHeight)
            rect = pygame.Rect(x, y, bWidth, bHeight)
            ok = True
            for b in listOfBalloons:
                # Check only y-axis overlap - ensure there's at least min_spacing between balloons vertically
                # Balloons can share x coordinates but must not overlap on y axis
                if (rect.bottom > b.balloonRect.top - min_spacing and 
                    rect.top < b.balloonRect.bottom + min_spacing):
                    ok = False
                    break
            if ok:
                return x, y
            attempts += 1
        # fallback: return last tried coordinates even if crowded
        return x, y

    # create bCount-1 option balloons
    for _ in range(bCount - 1):
        # pick optional text for this balloon
        text = None
        if optiuni:
            try:
                text = optiuni.pop()  # get an option from the list (will raise IndexError if empty)
            except Exception:
                text = None

        sx, sy = find_spot()
        listOfBalloons.append(Balloon(sx, sy, bWidth, bHeight, bSpeed, text=text))

    # create the answer balloon, also ensuring spacing
    ax, ay = find_spot()
    listOfBalloons.append(Balloon(ax, ay, bWidth, bHeight, bSpeed, text=raspuns))

    return listOfBalloons


# Game Over Screen. Waits for the user to replay or quit
def gameOver():
    gameOver = True

    while gameOver:
        gameOverText = font.render("GAME OVER", True, GREEN)
        retryText = font.render("R - Replay    Q - Quit", True, GREEN)

        # render the text on the screen using the pygame blit function
        screen.blit(gameOverText, (WIDTH//2-200, HEIGHT//2-100))
        screen.blit(retryText, (WIDTH//2-200, HEIGHT//2-80))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                # replay
                if event.key == pygame.K_r:  
                    return True
                # quit
                if event.key == pygame.K_q:  
                    return False

        pygame.display.update()


# Game Manager
def show_menu():
    """Display a simple menu to choose character (boy/girl) and select number checkboxes 2..9.
    Returns: (texts_list, gender) where texts_list is list of strings to use on balloons.
    """
    running = True
    gender = 'boy'

    # checkbox states for numbers 2..9
    nums = list(range(2, 10))
    checked = {n: False for n in nums}

    start_btn = pygame.Rect(WIDTH//2 - 60, HEIGHT - 120, 120, 50)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # radio buttons for gender
                # boy rect
                boy_rect = pygame.Rect(WIDTH//2 - 150, 120, 20, 20)
                girl_rect = pygame.Rect(WIDTH//2 + 80, 120, 20, 20)
                if boy_rect.collidepoint((mx, my)):
                    gender = 'boy'
                if girl_rect.collidepoint((mx, my)):
                    gender = 'girl'

                # checkboxes
                for i, n in enumerate(nums):
                    col = WIDTH//2 - 180 + (i%4)*120
                    row = 200 + (i//4)*60
                    box = pygame.Rect(col, row, 30, 30)
                    if box.collidepoint((mx, my)):
                        checked[n] = not checked[n]

                # start
                if start_btn.collidepoint((mx, my)):
                    selected = [str(n) for n, v in checked.items() if v]
                    if not selected:
                        # nu am selecteat nimic, nu pornim jocul
                        selected = []
                    return selected, gender

        # draw menu
        screen.fill((30, 30, 40))
        title = font.render("... Arcașii Veseli ...", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        # Gender radio
        screen.blit(font.render("Alege-ți personajul:", True, WHITE), (WIDTH//2 - 150, 80))
        boy_rect = pygame.Rect(WIDTH//2 - 150, 120, 20, 20)
        girl_rect = pygame.Rect(WIDTH//2 + 80, 120, 20, 20)
        pygame.draw.rect(screen, WHITE, boy_rect, 2)
        pygame.draw.rect(screen, WHITE, girl_rect, 2)
        if gender == 'boy':
            pygame.draw.circle(screen, WHITE, boy_rect.center, 6)
        else:
            pygame.draw.circle(screen, WHITE, girl_rect.center, 6)
        screen.blit(font.render("Prinț", True, WHITE), (boy_rect.right + 10, boy_rect.y - 4))
        screen.blit(font.render("Prințesă", True, WHITE), (girl_rect.right + 10, girl_rect.y - 4))

        # checkboxes for numbers
        screen.blit(font.render("Selecteaza tabelele de inmultire:", True, WHITE), (WIDTH//2 - 180, 160))
        for i, n in enumerate(nums):
            col = WIDTH//2 - 180 + (i%4)*120
            row = 200 + (i//4)*60
            box = pygame.Rect(col, row, 30, 30)
            pygame.draw.rect(screen, WHITE, box, 2)
            if checked[n]:
                pygame.draw.line(screen, WHITE, (col+4, row+15), (col+12, row+24), 3)
                pygame.draw.line(screen, WHITE, (col+12, row+24), (col+26, row+6), 3)
            screen.blit(font.render(str(n), True, WHITE), (col+40, row-2))

        # start button
        pygame.draw.rect(screen, (50, 150, 50), start_btn)
        screen.blit(font.render("Start", True, WHITE), (start_btn.x + 30, start_btn.y + 12))

        pygame.display.update()
        clock.tick(FPS)

class TabelInmultire:
    """Class to generate multiplication problems for the castle text."""
    def __init__(self, tabele):
        self.__tabele = tabele
        self.__NR_OPTIUNI = 3

    def __str__(self):
        return f"{self.a} x {self.b} = "

    def genereaza_problema(self):
        """Generate a multiplication problem based on the selected tables."""

        factor1 = int(random.choice(self.__tabele))
        factor2 = random.randint(1, 10)
        tabel_dict = {"intrebare": f"{factor1} x {factor2} = ", "raspuns": factor1 * factor2, "optiuni": []}
        
        # Generate wrong options
        for _ in range(self.__NR_OPTIUNI):
            wrong = random.randint(1, 100)
            
            # cautam un produs care sa fie gresit, adica diferit de cel corect
            while wrong == factor1 * factor2:
                wrong = random.randint(1, 100)
            
            tabel_dict["optiuni"].append(wrong)
        
        # Shuffle the options
        random.shuffle(tabel_dict["optiuni"])
        
        print(f"Generated problem: {tabel_dict['intrebare']} with answer {tabel_dict['raspuns']} and options {tabel_dict['optiuni']}")
        
        return tabel_dict



def main(selected_texts=None, gender='boy'):
    
    print(" Selected texts for balloons:", selected_texts)
    
    tabel = TabelInmultire(selected_texts)
    problema = tabel.genereaza_problema()
    
    score = 0
    lives = 5
    running = True

    # Set archer image based on gender selection (fall back if file missing)
    global archerPath
    if gender == 'girl':
        candidate = os.path.join(BASE_DIR, "arcas_sissi.png")
        if os.path.exists(candidate):
            archerPath = candidate

    archer = Archer(80, 80, 7)
    # Used to control the archer
    xFac, yFac = 0, 0    

    numBalloons = len(problema["optiuni"]) + 1  # one for the correct answer

    listOfBalloons = populateBalloons(30, 40, 1, numBalloons, raspuns=problema["raspuns"], optiuni=problema["optiuni"])
    listOfArrows = []

    try:
        _bg = pygame.image.load(backgroundPath)
        background = pygame.transform.smoothscale(_bg, screen.get_size())
        # background = pygame.transform.scale(_bg, (WIDTH, HEIGHT))
    except Exception as e:
        background = None
        print(e)

    # Create castle object (will handle missing file)
    # Enable slow blinking: blink every 800 ms
    castle_obj = Castle(castlePath, max_width=150, x=20, y_offset=-10)
    problema_obj = TextProblema(problema["intrebare"], text_color=BLACK, blink=True, blink_interval_ms=800)

    while running:
        # Background
        if background is not None:
            screen.blit(background, (0, 0))
        else:
            screen.fill(GREEN)  

        # Draw castle object (if image loaded)
        if castle_obj is not None:
            castle_obj.display(screen)
            
        if problema_obj is not None:
            problema_obj.display()

        # Representing each life with an arrow tilted by 45 degrees
        # for i in range(lives):
        #     screen.blit(pygame.transform.rotate(pygame.transform.scale(
        #         pygame.image.load(arrowPath), (20, 30)), 45), (i*30, 10))

        # Rendering the score
        scoreText = font.render(f"Score: {score}", True, WHITE)
        screen.blit(scoreText, (10, HEIGHT-50))

        if len(listOfBalloons) == 0:
            listOfBalloons = populateBalloons(30, 40, 1, numBalloons, raspuns=problema["raspuns"], optiuni=problema["optiuni"])

        # When all the lives are over
        if lives <= 0:
            running = gameOver()

            # Clearing the lists
            listOfBalloons.clear()
            listOfArrows.clear()

            # Resetting the variables
            lives = 5
            score = 0
            listOfBalloons = populateBalloons(30, 40, 1, numBalloons, raspuns=problema["raspuns"], optiuni=problema["optiuni"])

        # Display and update all the balloons
        for balloon in listOfBalloons:
            balloon.update()
            balloon.display()

        # Display and update all the arrows
        for arrow in listOfArrows:
            arrow.update()
            arrow.display()

        # Display and update the archer
        archer.display()
        archer.update(xFac, yFac)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Key press event
            if event.type == pygame.KEYDOWN:
                # Replay button
                if event.key == pygame.K_r:     
                    listOfBalloons = populateBalloons(30, 40, 1, numBalloons, raspuns=problema["raspuns"], optiuni=problema["optiuni"])
                    score = 0
                # Right arrow key => move rightwards => xFac = 1
                if event.key == pygame.K_RIGHT:  
                    xFac = 1
                # Left arrow key => move leftwards => xFac = -1
                if event.key == pygame.K_LEFT:  
                    xFac = -1
                # Down arrow key => move downwards => yFac = 1
                if event.key == pygame.K_DOWN:  
                    yFac = 1
                # Up arrow key => move upwards => yFac = -1
                if event.key == pygame.K_UP:    
                    yFac = -1
                    # Fire button
                    if event.key == pygame.K_SPACE:  
                        # Only fire if no arrows are currently on screen
                        if len(listOfArrows) == 0:
                            listOfArrows.append(Arrow(archer.archerRect.x, archer.archerRect.y+archer.archerRect.h/2-15, 60, 30, 10))

            # Key release event
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    xFac = 0
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    yFac = 0

        # Check for any collision between the arrows and the balloons
        for arrow in listOfArrows:
            for balloon in listOfBalloons:
                if pygame.Rect.colliderect(arrow.arrowRect, balloon.balloonRect):
                    # Changes the arrow's 'hit' from 0 to 1
                    arrow.updateHit()   
                    # Remove the balloon form the list
                    listOfBalloons.pop(listOfBalloons.index(balloon))
                    # Increase the score
                    score += 1     

        # Delete the arrows that crossed end of the screen
        for arrow in listOfArrows:
            if arrow.arrowRect.x > WIDTH:
                # if not arrow.getHit():
                    # If the arrow's state is 0, then a life is deducted
                    # lives -= 1 
                listOfArrows.pop(listOfArrows.index(arrow))

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    # Show the menu first; if user closes menu, quit
    selections, gender = show_menu()

    if selections:
        main(selected_texts=selections, gender=gender)
    pygame.quit()