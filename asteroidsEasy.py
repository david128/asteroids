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


def ccw(A, B, C):
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
        self.angle = 0.0
        self.rotatedSurface = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRectangle = self.rotatedSurface.get_rect()
        self.rotatedRectangle.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w / 2, self.y - self.sine * self.h / 2)
        self.br = (self.x + self.cosine * self.w, self.y + self.sine * self.h / 2)
        self.bl = (self.x - self.cosine * self.w, self.y + self.sine * self.h / 2)
        self.velocityX = 0
        self.velocityY = 0
        self.waitTime = 0
        super().__init__()

    def findDistanceToPoint(self, x, y):
        # the 3 lines of the triangle
        bottom = (self.bl, self.br)
        left = (self.bl, self.head)
        right = (self.br, self.head)
        bd = self.findDistanceToPointFromLineSegment(x, y, bottom[0], bottom[1])
        rd = self.findDistanceToPointFromLineSegment(x, y, right[0], right[1])
        ld = self.findDistanceToPointFromLineSegment(x, y, left[0], left[1])
        return min(bd, ld, rd)


    def sqr(self, x):
        return x * x

    def dist2(self, v, w):
        return (self.sqr(v[0] - w[0]) + self.sqr(v[1] - w[1]))

    def findDistanceToPointFromLineSegment(self, x, y, line1, line2):
        len2 = self.dist2(line1, line2)
        if len2 == 0:
            return self.dist2((x, y), line1)
        t = ((x - line1[0]) * (line2[0] - line1[0]) +
             (y - line1[1]) * (line2[1] - line1[1])) / len2
        t = max(0, min(1, t))

        px = line1[0] + t * (line2[0] - line1[0])
        py = line1[1] + t * (line2[1] - line1[1])

        d2 = self.dist2((x, y), (px, py))
        return math.sqrt(d2)

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
        rx = self.x+self.w/2 * -self.cosine - self.h/2*self.sine
        ry = self.y+self.w/2 * self.sine + self.h/2* -self.cosine
        self.bl = (rx,ry)
        rx = self.x+self.w/2 * -self.cosine + self.h/2*self.sine
        ry = self.y+self.w/2 * self.sine - self.h/2* -self.cosine
        self.br = (rx,ry)

    def turnLeft(self):
        self.angle += 3.5
        if self.angle >= 360:
            self.angle -= 360

    def turnRight(self):
        self.angle -= 3.5
        if self.angle < 0:
            self.angle += 360

    def move(self):
        self.x += self.velocityX
        self.y += self.velocityY
        self.updateAngle()

    def moveForward(self):
        v = math.fabs(self.velocityX) * math.fabs(self.velocityX) + math.fabs(self.velocityY) * math.fabs(
            self.velocityY)
        v = math.sqrt(v)
        if (v < 3.5):
            self.velocityX += self.cosine * 0.1
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

    def drawAt(self, win,x,y):
        win.blit(self.img, (x, y))


class Alien(NonPlayerObject):
    def __init__(self, x, y, xV, yV):
        self.img = shipImage
        self.speed = 1.0
        self.randomSpawn()
        self.dead = True
        self.waitTime = 1000
        super().__init__(x, y, xV, yV)

    def update(self, ):
        pass
        #dont spawn

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
        self.rect = self.img.get_rect()
        super().__init__(x, y, xV, yV)

    def move(self):
        super().move()
        self.rect.center = (self.x, self.y)

    def incrementScore(self, amount):
        self.score += amount

    def hit(self):
        return self.amount


class SmallAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV):
        self.size = 25
        self.img = ast25Img
        self.speed = 1.0
        self.amount = 100
        super().__init__(x, y, xV, yV)

    def hit(self):
        return self.amount


class MediumAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV, newAsteroids):
        self.size = 50
        self.img = ast50Img
        self.speed = 0.75
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
        self.speed = 0.5
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
        self.asteroidSpawnTime = 300
        self.player = Player()
        self.alien = Alien(0, 0, 0, 0)
        self.alien.die(1)
        self.spawnCount = 5
        self.totalAsteroids = self.spawnCount


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
    totalAsteroids =5
    astCount = totalAsteroids
    debug = False
    debugLines=[]
    radarLines=[]
    shapeLines =[]

    def resetGame(self):
        score = 0
        lives = 3
        count = 0
        self.alienRespawnTime = 200
        self.player.reset()
        self.asteroids.clear()
        self.bullets.clear()
        self.alienBullets.clear()
        self.spawnCount = 5
        self.totalAsteroids = self.spawnCount


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
            a.drawAt(win, a.x - a.size / 2, a.y - a.size / 2)
        win.blit(livesText, (25, 25))
        win.blit(scoreText, (screenW - 100, 25))

        if self.debug:
            for d in self.radarLines:
                pygame.draw.line(win, (255, 255, 0), (self.player.x, self.player.y), (d.x, d.y))
            for d in self.debugLines:
                pygame.draw.line(win, (255, 0, 0), (self.player.x, self.player.y), (d.x, d.y))
            for d in self.shapeLines:
                pygame.draw.line(win, (255, 100, 0), (d[0].x, d[0].y), (d[1].x, d[1].y))

        pygame.display.update()

    def collisionCheck(self, ax, ay, asize, bx, by, bsize):
        if (bx >= ax and bx <= ax + asize) or (bx + bsize >= ax and bx + bsize <= ax + asize):
            if (by >= ay and by <= ay + asize) or (by + bsize >= ay and by + bsize <= ay + asize):
                return True

    def colCheckPlayerAsteroid(self, a,pr):
        #general col detection
        if pr.colliderect(a.rect):
            #pixel collision
            pm = pygame.mask.from_surface(self.player.rotatedSurface.convert_alpha())
            am = pygame.mask.from_surface(a.img.convert_alpha())
            self.outline =pm.outline()
            self.outline2 =am.outline()

            offset = (
            a.x - a.size / 2 - self.player.rotatedRectangle.x, a.y - a.size / 2 - self.player.rotatedRectangle.y)
            if pm.overlap(am, offset):
                if self.debug:
                    print("Collision")
                return True
        return False

    def update(self):
        # clock tick removed to allow for faster playing
        # clock.tick(60)
        self.count += 1

        if not self.gameover:
            # if there are more asteroids to spawn
            if self.astCount > 0:
                # if it has been a certain amount of time since last spawn, spawn another
                if self.count % self.asteroidSpawnTime == 0:
                    self.astCount -= 1
                    self.asteroids.append(
                        random.choice([SmallAsteroid(0, 0, 0, 0), MediumAsteroid(0, 0, 0, 0, self.newAsteroids),
                                       LargeAsteroid(0, 0, 0, 0, self.newAsteroids)]))
            else:
                # if there are no asteroids on screen then move to next "level""
                if len(self.asteroids) == 0:
                    incr = max(1, int(float(self.totalAsteroids) * 0.1))
                    self.totalAsteroids+=incr
                    self.astCount = self.totalAsteroids

            if not self.alien.dead:
                self.alien.move()
                if self.count % 200 == 0:
                    self.alienBullets.append(AlienBullet(self.alien.x, self.alien.y, self.player.x, self.player.y))
            else:
                self.alien.update()

            for b in self.bullets:
                b.move()
                b.move()
                # col check bullets with alien
                if not self.alien.dead:
                    if self.collisionCheck(self.alien.x, self.alien.y, self.alien.img.get_width(), b.x, b.y, b.size):
                        self.alien.die(self.alienRespawnTime)
                        self.score += 200
                        self.bullets.pop(self.bullets.index(b))

            for a in self.asteroids:
                a.move()
                a.checkPos()
                # col check between asteroid and player
                if self.colCheckPlayerAsteroid(a,self.player.rotatedRectangle):
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
                        break

                # bullet collisions
                for b in self.bullets:
                    if self.collisionCheck(a.x, a.y, a.size, b.x, b.y, b.size):
                        self.score += a.hit()
                        self.asteroids.pop(self.asteroids.index(a))
                        self.bullets.pop(self.bullets.index(b))
                        break

            for ab in self.alienBullets:
                ab.move()
                if self.collisionCheck(self.player.x, self.player.y, self.player.img.get_width(), ab.x, ab.y, ab.size):
                    self.lives -= 1
                    self.livesFlag = True
                    self.alienBullets.pop(self.alienBullets.index(ab))
                    break

            # add the new asteroids to list
            for n in self.newAsteroids:
                self.asteroids.append(n)
            self.newAsteroids.clear()


            self.player.move()
            self.player.slow()
            self.player.checkPos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    if not self.debug:
                        self.debug = True
                    else:
                        self.debug = False
                    print("debug: " + str(self.debug))

        self.player.waitTime -= 1

    def distance(self, ax, ay):
        dx, dy = self.player.x - ax, self.player.y - ay
        dist = math.hypot(dx, dy)
        return dist

    def checkLineIntersection(self, x1,y1,x2,y2, asteroid):
        # check for intersection between line and line at asteroid origin
        frontVertical1 = Point(asteroid.x + asteroid.size / 2, asteroid.y - asteroid.size / 2)
        frontVertical2 = Point(asteroid.x + asteroid.size / 2, asteroid.y + asteroid.size / 2)
        bottomHorizontal1 = Point(asteroid.x - asteroid.size / 2, asteroid.y - asteroid.size / 2)
        bottomHorizontal2 = Point(asteroid.x + asteroid.size / 2, asteroid.y - asteroid.size / 2)
        backVertical1 = Point(asteroid.x - asteroid.size / 2, asteroid.y - asteroid.size / 2)
        backVertical2 = Point(asteroid.x - asteroid.size / 2, asteroid.y + asteroid.size / 2)
        topHorizontal1 = Point(asteroid.x - asteroid.size / 2, asteroid.y + asteroid.size / 2)
        topHorizontal2 = Point(asteroid.x + asteroid.size / 2, asteroid.y + asteroid.size / 2)
        p1 = Point(x1,y1)
        p2 = Point(x2,y2)


        # check for intersection between line and asteroid axis
        if (intersect(p1, p2, frontVertical1, frontVertical2) or intersect(p1, p2, backVertical1, backVertical2)
                or intersect(p1, p2, bottomHorizontal1, bottomHorizontal2) or intersect(p1, p2, topHorizontal1,
                                                                                        topHorizontal2)):
            if self.debug:
                self.shapeLines.append((frontVertical1, frontVertical2))
                self.shapeLines.append((backVertical1, backVertical2))
                self.shapeLines.append((bottomHorizontal1, bottomHorizontal2))
                self.shapeLines.append((topHorizontal1, topHorizontal2))
            return True

    def observe(self):

        self.debugLines.clear()
        self.radarLines.clear()
        self.shapeLines.clear()

        angle = self.player.angle
        lines =16
        radius = 400.0
        radar = [0.0] * lines


        #sort so that nearest is at the front and will be first added to radar
        self.asteroids = sorted(self.asteroids, key=lambda a: self.distance(a.x, a.y))
        self.alienBullets = sorted(self.alienBullets, key=lambda a: self.distance(a.x, a.y))



        # loop through N,NE,E,SE,S,SW,W,NW directions and check for asteroids if the player can "see" them
        for i in range(lines):
            # find the end point of the player's vision
            x2 = self.player.x + radius* math.sin(math.radians(angle))
            y2 = self.player.y + radius* math.cos(math.radians(angle))
            angle += 360.0/lines
            # check all asteroids
            for a in self.asteroids:
                if self.debug:
                    self.radarLines.append(Point(x2, y2))
                if self.checkLineIntersection(self.player.x,self.player.y, x2,y2,a):
                    #set the value to the distance
                    radar[i]=(self.player.findDistanceToPoint(a.x,a.y) - a.size/2.0) / (radius+25)
                    if self.debug:
                        self.debugLines.append(Point(x2,y2))
                    break

        self.radar = radar
        # observation object to be returned including information about the player
        o = [(self.player.x+50)/900, (self.player.y+50)/900, self.player.velocityX/3.6, self.player.velocityY/3.6, self.player.angle/360]
        #add radar info to observation
        o = o+list(radar)
        #add information about nearest bullet
        ''''
        if len(self.alienBullets) == 0:
            o = o + [0, 0]
        else:
            ab = self.alienBullets[0]
            o = o + [ab.x, ab.y]
        '''
        return o

    def action(self, action,k,renderMode):
        self.delta = self.score
        for i in range(k):
            self.simpleActions(action)
            self.update()
            if renderMode:
                self.redrawWindow()
            else:
                print("Frame:"+ str(self.count))
        # get change in score
        self.delta = self.score - self.delta

    def simpleActions(self,action):
        if action == 0:
            self.player.moveForward()
        elif action == 1:
            self.player.turnLeft()
        elif action == 2:
            self.player.turnRight()
        elif action == 3:
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 4:
            pass # do nothing

    def multiActions(self, action):
        if action == 0:
            self.player.moveForward()
        elif action == 1:
            self.player.moveForward()
            self.player.turnLeft()
        elif action == 2:
            self.player.moveForward()
            self.player.turnRight()
        elif action == 3:
            self.player.turnLeft()
        elif action == 4:
            self.player.turnRight()
        elif action == 5:
            self.player.moveForward()
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 6:
            self.player.moveForward()
            self.player.turnLeft()
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 7:
            self.player.moveForward()
            self.player.turnRight()
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 8:
            self.player.turnLeft()
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 9:
            self.player.turnRight()
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 10:
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 11:
            # do nothing
            pass
        pass

    def evaluate(self):
        reward = self.delta
        if self.livesFlag:
            reward = reward - 1000
            self.livesFlag = False  # reset flag
        return reward

    def is_done(self):
        if self.lives <= 0:
            gameover = True
            return True
        else:
            return False
