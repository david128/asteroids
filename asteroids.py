import math
import random

import numpy as np
import cv2
import matplotlib.pyplot as plt
import PIL.Image as Image
import gym
import random

from gym import Env, spaces
import time

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

import pygame
pygame.init()



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






class AsteroidsGame(Env):


    def __init__(self):
        super(AsteroidsGame,self).__init__()

    run = True
    gameover = False
    bullets = []
    alienBullets = []
    asteroids = []
    newAsteroids = []
    score = 0
    count = 0
    lives = 3

    class GameObject(object):
        def __init__(self):
            self.x
            self.y

        def move(self):
            self.x += self.xVelocity
            self.y -= self.yVelocity

        def isOffScreen(self):
            if self.x < -50 or self.x > screenW + 50 or self.y < -50 or self.y > screenH + 50:
                return True

    class Player(GameObject):
        def __init__(self):
            self.img = shipImage
            self.w = self.img.get_width()
            self.h = self.img.get_height()
            self.x = screenW / 2
            self.y = screenH / 2
            self.angle = 0
            self.rotatedSurface = pygame.transform.rotate(self.img, self.angle)
            self.rotatedRectangle = self.rotatedSurface.get_rect()
            self.rotatedRectangle.center = (self.x, self.y)
            self.cosine = math.cos(math.radians(self.angle + 90))
            self.sine = math.sin(math.radians(self.angle + 90))
            self.head = (self.x + self.cosine * self.w / 2, self.y - self.sine * self.h / 2)
            self.velocityX = 0
            self.velocityY = 0
            self.waitTime = 0
            print(self.waitTime)
            super().__init__()

        def shoot(self):
            # makes the player wait 25 frames before firing again
            if self.waitTime <= 0:
                self.waitTime = 25
                return True
            return False

        def draw(self, win):
            win.blit(self.rotatedSurface, self.rotatedRectangle)

        def updateAngle(self):
            self.rotatedSurface = pygame.transform.rotate(self.img, self.angle)
            self.rotatedRectangle = self.rotatedSurface.get_rect()
            self.rotatedRectangle.center = (self.x, self.y)
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
            if (self.velocityX < 100):
                self.velocityX += self.cosine * 0.1
            if (self.velocityY < 100):
                self.velocityY -= self.sine * 0.1

        def slow(self):
            # slow down
            self.velocityX = self.velocityX - 0.01 * self.velocityX
            self.velocityY = self.velocityY - 0.01 * self.velocityY
            # stop completely if approaching 0
            if (abs(self.velocityX) <= 0.1):
                self.velocityX = 0
            if (abs(self.velocityY) <= 0.1):
                self.velocityY = 0

        def checkPos(self):
            if self.x < -50:
                self.x = screenW + 50
            elif self.x > screenW + 50:
                self.x = -50
            if self.y < -50:
                self.y = screenH + 50
            elif self.y > screenH + 50:
                self.y = -50

        def reset(self):
            self.x = screenW / 2
            self.y = screenH / 2
            self.angle = 0
            self.updateAngle()

    class NonPlayerObject(GameObject):
        def __init__(self, x, y, xV, yV):
            self.x = x
            self.y = y
            self.xVelocity = xV
            self.yVelocity = yV
            if (x == 0 and y == 0):
                self.randomSpawn()

        def randomSpawn(self):
            # find random pos to spawn asteroid at
            self.spawnPos = random.choice([(random.choice([-50, screenW + 50]), random.randrange(0, screenH)),
                                           (random.randrange(0, screenW), random.choice([-50, screenH + 50]))])
            self.x, self.y = self.spawnPos
            # choose the correct direction
            if (self.x < screenW / 2):
                # on left side
                xdir = 1
            else:
                xdir = -1
            if (self.y < screenH / 2):
                # on top side
                ydir = 1
            else:
                ydir = -1
            # choose a random xV and yV
            self.randomVelocity(xdir, ydir)

        def randomVelocity(self, xDir, yDir):
            r = random.uniform(0.25, 0.75)
            self.xVelocity = r * self.speed * xDir
            self.yVelocity = (1 - r) * self.speed * yDir

        def move(self):
            self.x += self.xVelocity
            self.y += self.yVelocity

        def draw(self, win):
            win.blit(self.img, (self.x, self.y))

    class Alien(NonPlayerObject):
        def __init__(self, x, y, xV, yV):
            self.img = shipImage
            self.speed = 1.5
            self.randomSpawn()
            super().__init__(x, y, xV, yV)

    player = Player()
    alien = Alien(0, 0, 0, 0)

    class Bullet(GameObject):

        def __init__(self):
            self.x, self.y = self.player.head
            self.cosine = self.player.cosine
            self.sine = self.player.sine
            self.size = 3
            self.xVelocity = 10 * self.cosine
            self.yVelocity = 10 * self.sine
            super().__init__()

        def draw(self, win):
            pygame.draw.rect(win, (255, 255, 255), [self.x, self.y, self.size, self.size])

    class AlienBullet(GameObject):
        def __init__(self):
            self.x = self.alien.x
            self.y = self.alien.y
            self.size = 3

            self.dx, self.dy = self.player.x - self.x, self.player.y - self.y
            self.dist = math.hypot(self.dx, self.dy)
            self.dx, self.dy = self.dx / self.dist, self.dy / self.dist
            self.xVelocity = self.dx * 5
            self.yVelocity = self.dy * -5

            super().__init__()

        def draw(self, win):
            pygame.draw.rect(win, (255, 255, 255), [self.x, self.y, self.size, self.size])





    class Asteroid(NonPlayerObject):
        def __init__(self, x, y, xV, yV):
            super().__init__(x, y, xV, yV)

        def hit(self):
            pass

    class SmallAsteroid(Asteroid):
        def __init__(self, x, y, xV, yV):
            self.size = 25
            self.img = ast25Img
            self.speed = 1.5
            super().__init__(x, y, xV, yV)

        def hit(self):
            super().hit()

    class MediumAsteroid(Asteroid):
        def __init__(self, x, y, xV, yV):
            self.size = 50
            self.img = ast50Img
            self.speed = 1.25
            super().__init__(x, y, xV, yV)

        def hit(self):
            self.newAsteroids.append(self.SmallAsteroid(self.x, self.y, self.xVelocity, self.yVelocity))
            a = self.SmallAsteroid(self.x, self.y, 0, 0)
            a.randomVelocity(random.choice([-1, 1]), random.choice([-1, 1]))
            self.newAsteroids.append(a)
            super().hit()

    class LargeAsteroid(Asteroid):
        def __init__(self, x, y, xV, yV):
            self.img = ast100Img
            self.size = self.img.get_width()
            self.speed = 1.0
            super().__init__(x, y, xV, yV)

        def hit(self):
            self.newAsteroids.append(self.MediumAsteroid(self.x, self.y, self.xVelocity, self.yVelocity))
            a = self.MediumAsteroid(self.x, self.y, 0, 0)
            a.randomVelocity(random.choice([-1, 1]), random.choice([-1, 1]))
            self.newAsteroids.append(a)
            super().hit()



    def resetGame(self):
        score = 0
        lives = 3
        count = 0
        self.player.reset()
        self.asteroids.clear()
        self.bullets.clear()
        self.alienBullets.clear()

    def redrawWindow(self):
        win.blit(bg, (0, 0))
        font = pygame.font.SysFont('arial', 20)
        livesText = font.render('Lives: ' + str(self.lives), 1, (255, 255, 255))
        self.player.draw(win)
        self.alien.draw(win)
        for b in self.bullets:
            if b.isOffScreen():
                self.bullets.pop(self.bullets.index(b))
            else:
                b.draw(win)
        for ab in self.alienBullets:
            if ab.isOffScreen():
                self.alienBullets.pop(self.alienBullets.index(ab))
            else:
                ab.draw(win)

        for a in self.asteroids:
            a.draw(win)
        win.blit(livesText, (25, 25))
        pygame.display.update()

    def collisionCheck(ax, ay, asize, bx, by, bsize):
        if (bx >= ax and bx <= ax + asize) or (bx + bsize >= ax and bx + bsize <= ax + asize):
            if (by >= ay and by <= ay + asize) or (by + bsize >= ay and by + bsize <= ay + asize):
                return True



    def reset(self):
        pass

    def step(self):
        clock.tick(60)
        self.count += 1
        if not self.gameover:
            if self.count % 100 == 0:
                self.asteroids.append(
                    random.choice([self.SmallAsteroid(0, 0, 0, 0), self.MediumAsteroid(0, 0, 0, 0), self.LargeAsteroid(0, 0, 0, 0)]))
            if self.count % 150 == 0:
                self.alienBullets.append(self.AlienBullet())

            for b in self.bullets:
                b.move()
            for a in self.asteroids:
                a.move()
                if self.collisionCheck(a.x, a.y, a.size, self.player.x, self.player.y, self.player.img.get_width()):
                    print("Collision")
                    self.lives -= 1
                    self.asteroids.pop(self.asteroids.index(a))
                    break

                # bullet collisions
                for b in self.bullets:
                    if self.collisionCheck(a.x, a.y, a.size, b.x, b.y, b.size):
                        a.hit()
                        print("b")
                        self.asteroids.pop(self.asteroids.index(a))
                        self.bullets.pop(self.bullets.index(b))

            for n in self.newAsteroids:
                self.asteroids.append(n)
            self.newAsteroids.clear()

            for ab in self.alienBullets:
                ab.move()

            self.player.move()
            self.alien.move()
            self.player.checkPos()

            inputs = pygame.key.get_pressed()
            if inputs[pygame.K_LEFT]:
                self.player.turnLeft()
            if inputs[pygame.K_RIGHT]:
                self.player.turnRight()
            if inputs[pygame.K_UP]:
                self.player.moveForward()
            else:
                self.player.slow()

            if inputs[pygame.K_BACKSPACE]:
                self.resetGame()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.gameover:
                        if self.player.shoot():
                            self.bullets.append(self.Bullet())

        self.player.waitTime -= 1

        if self.lives <= 0:
            gameover = True

        self.redrawWindow()


