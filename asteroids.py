import math
import random

import pygame
pygame.init()

gameover = False
bullets = []
alienBullets = []
asteroids =[]
newAsteroids =[]
score = 0
count = 0
lives = 3

screenW =800
screenH =800

shipImage = pygame.image.load("ship.png")
ast100Img = pygame.image.load("ast100.png")
ast50Img = pygame.image.load("ast50.png")
ast25Img = pygame.image.load("ast25.png")
bg = pygame.image.load("starbg.png")

pygame.display.set_caption("Asteroids")
win = pygame.display.set_mode((screenW,screenH))

clock = pygame.time.Clock()





class gameObject(object):
    def __init__(self):
        self.x
        self.y

    def move(self):
        self.x += self.xVelocity
        self.y -= self.yVelocity

    def isOffScreen(self):
        if self.x <-50 or self.x > screenW+50 or self.y <-50 or self.y >screenH+50:
            return True

class Bullet(gameObject):

    def __init__(self):
        self.x,self.y = player.head
        self.cosine = player.cosine
        self.sine = player.sine
        self.size = 3
        self.xVelocity = 10*self.cosine
        self.yVelocity = 10*self.sine
        super().__init__()

    def draw(self, win):
        pygame.draw.rect(win,(255,255,255),[self.x,self.y,self.size,self.size])

class AlienBullet(gameObject):
    def __init__(self):
        self.x = alien.x
        self.y = alien.y
        self.size = 3

        self.dx, self.dy = player.x - self.x, player.y - self.y
        self.dist = math.hypot(self.dx, self.dy)
        self.dx, self.dy = self.dx / self.dist, self.dy / self.dist
        self.xVelocity = self.dx * 5
        self.yVelocity = self.dy * 5

        super().__init__()

    def draw(self, win):
        pygame.draw.rect(win,(255,255,255),[self.x,self.y,self.size,self.size])

class Player(gameObject):
    def __init__(self):
        self.img = shipImage
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.x = screenW/2
        self.y = screenH/2
        self.angle =0
        self.rotatedSurface = pygame.transform.rotate(self.img,self.angle)
        self.rotatedRectangle =self.rotatedSurface.get_rect()
        self.rotatedRectangle.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w/2, self.y -self.sine * self.h/2)
        self.velocityX =0
        self.velocityY =0
        super().__init__()

    def draw(self,win):
        win.blit(self.rotatedSurface,self.rotatedRectangle)

    def updateAngle(self):
        self.rotatedSurface = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRectangle = self.rotatedSurface.get_rect()
        self.rotatedRectangle.center = (self.x,self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w / 2, self.y - self.sine * self.h / 2)

    def turnLeft(self):
        self.angle += 5

    def turnRight(self):
        self.angle -= 5

    def move(self):
        self.x += self.velocityX
        self.y += self.velocityY
        self.updateAngle()

    def moveForward(self):
        self.velocityX += self.cosine *0.1
        self.velocityY -= self.sine *0.1

    def checkPos(self):
        if self.x <-50:
            self.x=screenW+50
        elif self.x >screenW+50:
            self.x = -50
        if self.y < -50:
            self.y = screenH + 50
        elif self.y > screenH + 50:
            self.y = -50

    def reset(self):
        self.x = screenW/2
        self.y = screenH/2
        self.angle= 0
        self.updateAngle()

class NonPlayerObject(gameObject):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        if (x == 0 and y == 0):
            self.randomSpawn()
        if (self.x < screenW / 2):
            # on left side
            self.xdir = 1
        else:
            self.xdir = -1
        if (self.y < screenH / 2):
            # on top side
            self.ydir = 1
        else:
            self.ydir = -1

    def randomSpawn(self):
        # find random pos to spawn asteroid at
        self.spawnPos = random.choice([(random.choice([-50, screenW + 50]), random.randrange(0, screenH)),
                                       (random.randrange(0, screenW), random.choice([-50, screenH + 50]))])
        self.x, self.y = self.spawnPos

    def move(self):
        self.x += self.xVelocity
        self.y += self.yVelocity

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))


class Asteroid(NonPlayerObject):
    def __init__(self, x,y):
        super().__init__(x,y)

    def hit(self):
        pass

class Alien(NonPlayerObject):
    def __init__(self,x,y):
        self.img = shipImage
        self.xVelocity = 0
        self.yVelocity = 0
        super().__init__(x,y)

class smallAsteroid(Asteroid):
    def __init__(self,x,y):
        self.size =25
        self.img = ast25Img
        self.xVelocity = 1.5
        self.yVelocity = 1.5
        super().__init__(x,y)

    def hit(self):
        super().hit()

class mediumAsteroid(Asteroid):
    def __init__(self,x,y):
        self.size =50
        self.img = ast50Img
        self.xVelocity = 1.25
        self.yVelocity = 1.25
        super().__init__(x,y)

    def hit(self):

        newAsteroids.append(smallAsteroid(self.x,self.y))
        newAsteroids.append(smallAsteroid(self.x,self.y))
        super().hit()

class largeAsteroid(Asteroid):
    def __init__(self,x,y):
        super().__init__(x,y)

        self.img = ast100Img
        self.size =self.img.get_width()
        self.xVelocity = 1
        self.yVelocity = 1

    def hit(self):
        newAsteroids.append(mediumAsteroid(self.x,self.y))
        newAsteroids.append(mediumAsteroid(self.x,self.y))
        super().hit()



def resetGame():
    score=0
    lives=3
    count=0
    player.reset()

    asteroids.clear()
    bullets.clear()
    alienBullets.clear()

def redrawWindow():
    win.blit(bg,(0,0))
    font = pygame.font.SysFont('arial',20)
    livesText = font.render('Lives: '+ str(lives),1,(255,255,255))
    player.draw(win)
    alien.draw(win)
    for b in bullets:
        if b.isOffScreen():
            bullets.pop(bullets.index(b))
        else:
            b.draw(win)
    for ab in alienBullets:
        if ab.isOffScreen():
            alienBullets.pop(alienBullets.index(ab))
        else:
            ab.draw(win)
            print("dsakdja")

    for a in asteroids:
        a.draw(win)
    win.blit(livesText,(25,25))
    pygame.display.update()

def collisionCheck(ax,ay,asize,bx,by,bsize) :
    if (bx >= ax and bx <= ax + asize) or (bx + bsize >= ax and bx + bsize <= ax + asize):
        if (by >= ay and by <= ay + asize) or (by + bsize>= ay and by + bsize <= ay + asize):
            return True




player = Player()
alien = Alien(0,0)
run = True
print("hello")
while run:
    clock.tick(60)
    count = count+1
    if not gameover:
        if count % 50 == 0:
            asteroids.append(random.choice([smallAsteroid(0,0),mediumAsteroid(0,0),largeAsteroid(0,0)]))
            alienBullets.append(AlienBullet())


        for b in bullets:
            b.move()
        for a in asteroids:
            a.move()
            if collisionCheck(a.x, a.y, a.size, player.x, player.y, player.img.get_width()):
                print("Collision")
                lives-=1
                asteroids.pop(asteroids.index(a))
                break

            #bullet collisions
            for b in bullets:
                if collisionCheck(a.x,a.y,a.size,b.x,b.y,b.size):
                    a.hit()
                    print("b")
                    asteroids.pop(asteroids.index(a))
                    bullets.pop(bullets.index(b))

        for n in newAsteroids:
            asteroids.append(n)

        player.move()
        alien.move()
        player.checkPos()

        inputs = pygame.key.get_pressed()
        if inputs[pygame.K_LEFT]:
            player.turnLeft()
        if inputs[pygame.K_RIGHT]:
            player.turnRight()
        if inputs[pygame.K_UP]:
            player.moveForward()
        if inputs[pygame.K_BACKSPACE]:
            resetGame()



    for event in pygame.event.get():
        if event.type== pygame.QUIT:
            run= False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not gameover:
                    bullets.append(Bullet())

    if lives <= 0:
        gameover=True

    redrawWindow()
pygame.quit()