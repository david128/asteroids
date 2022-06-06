import math
import random

import numpy as np
import cv2

import random

import time

font = cv2.FONT_HERSHEY_COMPLEX_SMALL

import pygame
import collections

pygame.init()

screenW = 800
screenH = 800
NEARASTEROIDS = 5

shipImage = pygame.image.load("ship.png")
ast100Img = pygame.image.load("ast100.png")
ast50Img = pygame.image.load("ast50.png")
ast25Img = pygame.image.load("ast25.png")
bg = pygame.image.load("starbg.png")

pygame.display.set_caption("Asteroids")
win = pygame.display.set_mode((screenW, screenH))

clock = pygame.time.Clock()


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

    def checkPos(self):
        if self.x < -50:
            self.x = screenW + 50
        elif self.x > screenW + 50:
            self.x = -50
        if self.y < -50:
            self.y = screenH + 50
        elif self.y > screenH + 50:
            self.y = -50


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
        if (abs(self.velocityX) <= 0.01):
            self.velocityX = 0
        if (abs(self.velocityY) <= 0.01):
            self.velocityY = 0

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
        self.dead = True
        self.waitTime = 1000
        super().__init__(x, y, xV, yV)

    def update(self, ):
        if self.dead:
            # makes the player wait 25 frames before firing again
            if self.waitTime <= 0:
                self.dead = False
                self.randomSpawn()
            else:
                self.waitTime -= 1

    def die(self, respawnTime):
        self.dead = True
        self.waitTime = respawnTime


class Bullet(GameObject):

    def __init__(self, ph, pc, ps):
        self.x, self.y = ph
        self.cosine = pc
        self.sine = ps
        self.size = 3
        self.xVelocity = 10 * pc
        self.yVelocity = 10 * ps
        super().__init__()

    def draw(self, win):
        pygame.draw.rect(win, (255, 255, 255), [self.x, self.y, self.size, self.size])


class AlienBullet(GameObject):
    def __init__(self, ax, ay, px, py):
        self.x = ax
        self.y = ay
        self.size = 3
        rx = random.randrange(1, 50)
        ry = random.randrange(1, 50)

        self.dx, self.dy = (px + ry) - self.x, (py + ry) - self.y
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

    def incrementScore(self, amount):
        self.score += amount

    def hit(self):
        return self.amount


class SmallAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV):
        self.size = 25
        self.img = ast25Img
        self.speed = 1.5
        self.amount = 100
        super().__init__(x, y, xV, yV)

    def hit(self):
        return self.amount


class MediumAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV, newAsteroids):
        self.size = 50
        self.img = ast50Img
        self.speed = 1.25
        self.newAsteroids = newAsteroids
        self.amount = 50
        super().__init__(x, y, xV, yV)

    def hit(self):
        self.newAsteroids.append(SmallAsteroid(self.x, self.y, self.xVelocity, self.yVelocity))
        a = SmallAsteroid(self.x, self.y, 0, 0)
        a.randomVelocity(random.choice([-1, 1]), random.choice([-1, 1]))
        self.newAsteroids.append(a)
        return self.amount


class LargeAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV, newAsteroids):
        self.img = ast100Img
        self.size = self.img.get_width()
        self.speed = 1.0
        self.newAsteroids = newAsteroids
        self.amount = 20
        super().__init__(x, y, xV, yV)

    def hit(self):
        self.newAsteroids.append(MediumAsteroid(self.x, self.y, self.xVelocity, self.yVelocity, self.newAsteroids))
        a = MediumAsteroid(self.x, self.y, 0, 0, self.newAsteroids)
        a.randomVelocity(random.choice([-1, 1]), random.choice([-1, 1]))
        self.newAsteroids.append(a)
        return self.amount


class AsteroidsGame():

    def __init__(self):
        self.alienRespawnTime = 1000
        self.asteroidSpawnTime = 150
        self.player = Player()
        self.alien = Alien(0, 0, 0, 0)

    run = True
    gameover = False
    bullets = []
    alienBullets = []
    asteroids = []
    newAsteroids = []
    score = 0
    count = 0
    lives = 3
    livesFlag = False

    def resetGame(self):
        score = 0
        lives = 3
        count = 0
        self.alienRespawnTime = 200
        self.player.reset()
        self.asteroids.clear()
        self.bullets.clear()
        self.alienBullets.clear()

    def redrawWindow(self):
        win.blit(bg, (0, 0))
        font = pygame.font.SysFont('arial', 20)
        livesText = font.render('Lives: ' + str(self.lives), 1, (255, 255, 255))
        scoreText = font.render('Score: ' + str(self.score), 1, (255, 255, 255))
        self.player.draw(win)
        if not self.alien.dead:
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
        win.blit(scoreText, (screenW - 100, 25))
        pygame.display.update()

    def collisionCheck(self, ax, ay, asize, bx, by, bsize):
        if (bx >= ax and bx <= ax + asize) or (bx + bsize >= ax and bx + bsize <= ax + asize):
            if (by >= ay and by <= ay + asize) or (by + bsize >= ay and by + bsize <= ay + asize):
                return True

    def update(self):
        #clock tick removed to allow for faster playing
        #clock.tick(60)
        self.count += 1

        if not self.gameover:
            if self.count % self.asteroidSpawnTime == 0:
                self.asteroids.append(
                    random.choice([SmallAsteroid(0, 0, 0, 0), MediumAsteroid(0, 0, 0, 0, self.newAsteroids),
                                   LargeAsteroid(0, 0, 0, 0, self.newAsteroids)]))

            if not self.alien.dead:
                self.alien.move()
                if self.count % 150 == 0:
                    self.alienBullets.append(AlienBullet(self.alien.x, self.alien.y, self.player.x, self.player.y))
            else:
                self.alien.update()

            for b in self.bullets:
                b.move()
            for a in self.asteroids:
                a.checkPos()
                a.move()
                if self.collisionCheck(a.x, a.y, a.size, self.player.x, self.player.y, self.player.img.get_width()):
                    print("Collision")
                    self.lives -= 1
                    self.livesFlag = True
                    self.asteroids.pop(self.asteroids.index(a))
                    break

                # collision between alien and asteroids
                if not self.alien.dead:
                    if self.collisionCheck(a.x, a.y, a.size, self.alien.x, self.alien.y, self.alien.img.get_width()):
                        self.alien.die(self.alienRespawnTime)

                # collision check with alien bullets
                for ab in self.alienBullets:
                    if self.collisionCheck(a.x, a.y, a.size, ab.x, ab.y, ab.size):
                        self.asteroids.pop(self.asteroids.index(a))
                        self.alienBullets.pop(self.alienBullets.index(ab))

                # bullet collisions
                for b in self.bullets:
                    if self.collisionCheck(a.x, a.y, a.size, b.x, b.y, b.size):
                        self.score += a.hit()
                        self.asteroids.pop(self.asteroids.index(a))
                        self.bullets.pop(self.bullets.index(b))

            for ab in self.alienBullets:
                ab.move()
                if self.collisionCheck(self.player.x, self.player.y, self.player.img.get_width(),ab.x, ab.y, ab.size):
                    print("ab Collision")
                    self.lives -= 1
                    self.livesFlag = True
                    self.alienBullets.pop(self.alienBullets.index(ab))
                    break


            for n in self.newAsteroids:
                self.asteroids.append(n)
            self.newAsteroids.clear()



            inputs = pygame.key.get_pressed()
            if inputs[pygame.K_LEFT]:
                self.player.turnLeft()
            if inputs[pygame.K_RIGHT]:
                self.player.turnRight()
            if inputs[pygame.K_UP]:
                self.player.moveForward()
            else:
                self.player.slow()
            if inputs[pygame.K_SPACE]:
                if self.player.shoot():
                    self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))

            self.player.move()

            self.player.checkPos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        self.player.waitTime -= 1

    def distance(self, ax, ay):
        dx, dy = self.player.x - ax, self.player.y - ay
        dist = math.hypot(dx, dy)
        return dist

    def observe(self):
        # return all asteroids within 100units of player
        near = collections.deque(maxlen=NEARASTEROIDS)
        self.asteroids = sorted(self.asteroids, key=lambda a: self.distance(a.x, a.y))
        self.alienBullets =sorted(self.alienBullets, key=lambda a: self.distance(a.x, a.y))
        for i in range(NEARASTEROIDS):
            # fill the near list with nearest asteroids
            if (len(self.asteroids) > i):
                near.append(
                    [self.asteroids[i].x, self.asteroids[i].y, self.asteroids[i].size, self.asteroids[i].xVelocity,
                     self.asteroids[i].yVelocity])
            else:
                # else if not enough exist fill with empty
                near.append([-1, -1, -1, 0, 0])

        o = [self.player.x, self.player.y, self.player.velocityX, self.player.velocityY, self.player.cosine,
             self.player.sine]
        if len(self.alienBullets) ==0:
            o = o+ [-1,-1,0,0]
        else:
            ab = self.alienBullets[0]
            o = o+ [ab.x,ab.y,ab.xVelocity,ab.yVelocity]
        for ast in near:
            o = o + list(ast)

        return o

    def action(self, action):

        self.delta = self.score
        if action == 0:
            self.player.moveForward()
        elif action == 1:
            self.player.moveForward()
            self.player.turnLeft()
        elif action == 2:
            self.player.moveForward()
            self.player.turnRight()
        else:
            # not moving forward so slow
            self.player.slow()

        if action == 3:
            self.player.turnLeft()
        elif action == 4:
            self.player.turnRight()
        elif action == 5:
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        self.update()
        # get change in score
        self.delta = self.score - self.delta

    def evaluate(self):
        reward = self.delta
        if self.livesFlag:
            reward = reward - 100
        self.livesFlag = False  # reset flag
        return reward

    def is_done(self):
        if self.lives <= 0:
            gameover = True
            return True
        else:
            return False
