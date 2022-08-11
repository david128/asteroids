import math
import random
import numpy as np
import cv2
import random
import time
import pygame
import collections

pygame.init()


#game vars
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
shipImage = pygame.image.load("ship.png")
ast100Img = pygame.image.load("ast100.png")
ast50Img = pygame.image.load("ast50.png")
ast25Img = pygame.image.load("ast25.png")
bg = pygame.image.load("starbg.png")
screenW = 800
screenH = 800

#pygame vars
pygame.display.set_caption("Asteroids")
win = pygame.display.set_mode((screenW, screenH))
clock = pygame.time.Clock()

multiplier = 1.25


# intersection
def ccw(A, B, C):
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)


# Return true if line segments AB and CD intersect
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


# point with x and y coords
class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


# base GameObject class
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

    # used to reset the pos when goes off screen to other side of screen
    def checkPos(self):
        if self.x < -50:
            self.x = screenW + 50
        elif self.x > screenW + 50:
            self.x = -50
        if self.y < -50:
            self.y = screenH + 50
        elif self.y > screenH + 50:
            self.y = -50


# Player class
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
        # returns the min distance from lines of ship to point supplied
        return min(bd, ld, rd)

    # function that returns squared of value
    def sqr(self, x):
        return x * x

    #returns distance squared
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
        # updates the angle and finds the rotated points of the ship
        self.rotatedSurface = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRectangle = self.rotatedSurface.get_rect()
        self.rotatedRectangle.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w / 2, self.y - self.sine * self.h / 2)
        rx = self.x + self.w / 2 * -self.cosine - self.h / 2 * self.sine
        ry = self.y + self.w / 2 * self.sine + self.h / 2 * -self.cosine
        self.bl = (rx, ry)
        rx = self.x + self.w / 2 * -self.cosine + self.h / 2 * self.sine
        ry = self.y + self.w / 2 * self.sine - self.h / 2 * -self.cosine
        self.br = (rx, ry)

    # left and right turns keep angle in 0-360 range
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
        # max v of 3.5
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
        # if not provided x and y then spawn in random loc
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

    def drawAt(self, win, x, y):
        win.blit(self.img, (x, y))


class Bullet(GameObject):

    def __init__(self, ph, pc, ps):
        self.x, self.y = ph  # x and y initialised at player head
        self.cosine = pc
        self.sine = ps
        self.size = 3
        self.xVelocity = 10 * pc
        self.yVelocity = 10 * ps
        super().__init__()

    def draw(self, win):
        pygame.draw.rect(win, (255, 255, 255), [self.x, self.y, self.size, self.size])


# asteroid base class
class Asteroid(NonPlayerObject):
    def __init__(self, x, y, xV, yV):
        self.rect = self.img.get_rect()
        super().__init__(x, y, xV, yV)

    def move(self):
        super().move()
        self.rect.center = (self.x, self.y)

    def hit(self):
        return self.amount


class SmallAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV):
        self.size = 25
        self.img = ast25Img
        self.speed = 1.25 * multiplier
        self.amount = 100
        super().__init__(x, y, xV, yV)

    def hit(self):
        return self.amount


class MediumAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV, newAsteroids):
        self.size = 50
        self.img = ast50Img
        self.speed = 1.0 * multiplier
        self.newAsteroids = newAsteroids
        self.amount = 50
        super().__init__(x, y, xV, yV)

    def hit(self):
        # spawn 2 small asteroids
        self.newAsteroids.append(SmallAsteroid(self.x, self.y, self.xVelocity, self.yVelocity))
        a = SmallAsteroid(self.x, self.y, 0, 0)
        a.randomVelocity(random.choice([-1, 1]), random.choice([-1, 1]))
        self.newAsteroids.append(a)
        return self.amount


class LargeAsteroid(Asteroid):
    def __init__(self, x, y, xV, yV, newAsteroids):
        self.img = ast100Img
        self.size = self.img.get_width()
        self.speed = 0.75 * multiplier
        self.newAsteroids = newAsteroids
        self.amount = 20
        super().__init__(x, y, xV, yV)

    def hit(self):
        # spawn two medium asteroids
        self.newAsteroids.append(MediumAsteroid(self.x, self.y, self.xVelocity, self.yVelocity, self.newAsteroids))
        a = MediumAsteroid(self.x, self.y, 0, 0, self.newAsteroids)
        a.randomVelocity(random.choice([-1, 1]), random.choice([-1, 1]))
        self.newAsteroids.append(a)
        return self.amount


def radarIsClose(v):
    if 0 < v < 150:
        return True


def radarIsEmpty(v):
    if v == 0:
        return True


class AsteroidsGame():

    def __init__(self, setting):
        self.chosenAction = 0
        self.astCount = 1
        self.delta = 0
        self.asteroidSpawnTime = 0
        self.spawnCount = 0
        self.totalAsteroids = 0
        self.player = Player()
        #default settings
        self.evaluate = self.evaluateLives
        self.actionSet = self.multiActions
        self.resetGame = self.resetGameNormal
        if setting == 1:
            multiplier = 1.0
            self.resetGame = self.resetGameEasy
        elif setting == 2:
            multiplier = 1.0
            self.actionSet = self.noShootActions
            self.evaluate = self.evaluateAvoid
        elif setting == 3:
            multiplier = 1.0
            self.actionSet = self.aimActions
        elif setting ==4:
            self.evaluate =  self.evaluateIRL
        self.resetGame()

    # global vars
    run = True
    gameover = False
    bullets = []
    asteroids = []
    newAsteroids = []
    score = 0
    count = 0
    lives = 3
    livesFlag = False
    # debug variables
    debug = False
    debugLines = []
    radarLines = []
    shapeLines = []

    def resetGameEasy(self):
        # reset variables
        self.score = 0
        self.lives = 3
        self.count = 0
        self.gameover = False
        self.player.reset()
        self.asteroids.clear()
        self.bullets.clear()
        self.spawnCount = self.astCount
        self.totalAsteroids = self.spawnCount
        self.asteroidSpawnTime = 300
        if self.astCount > 7:
            self.resetGame = self.resetGameNormal

    def resetGameNormal(self):
        # reset variables
        self.score = 0
        self.lives = 3
        self.count = 0
        self.gameover = False
        self.player.reset()
        self.asteroids.clear()
        self.bullets.clear()
        self.spawnCount = 8
        self.totalAsteroids = self.spawnCount
        self.asteroidSpawnTime = 300

    def redrawWindow(self):
        win.blit(bg, (0, 0))
        font = pygame.font.SysFont('arial', 20)
        livesText = font.render('Lives: ' + str(self.lives), 1, (255, 255, 255))
        scoreText = font.render('Score: ' + str(self.score), 1, (255, 255, 255))

        # draw player, bullets and asteroids
        self.player.draw(win)
        for b in self.bullets:
            if b.isOffScreen():
                self.bullets.pop(self.bullets.index(b))
            else:
                b.draw(win)
        for a in self.asteroids:
            a.drawAt(win, a.x - a.size / 2, a.y - a.size / 2)

        # draw text
        win.blit(livesText, (25, 25))
        win.blit(scoreText, (screenW - 150, 25))

        # if debug mode is on draw debug lines
        if self.debug:
            for d in self.radarLines:
                pygame.draw.line(win, (255, 255, 0), (self.player.x, self.player.y), (d.x, d.y))
            for d in self.debugLines:
                pygame.draw.line(win, (255, 0, 0), (self.player.x, self.player.y), (d.x, d.y))
                pass
            for d in self.shapeLines:
                pygame.draw.line(win, (255, 100, 0), (d[0].x, d[0].y), (d[1].x, d[1].y))


        pygame.display.update()

    # general col check bounding box to box
    def collisionCheck(self, ax, ay, asize, bx, by, bsize):
        ahalf = asize / 2
        bhalf = bsize / 2
        if (bx >= ax - ahalf and bx <= ax + ahalf) or (bx + bhalf >= ax - ahalf and bx + bsize - bhalf <= ax + ahalf):
            if (by >= ay - ahalf and by <= ay + ahalf) or (by + bhalf >= ay - ahalf and by + bhalf <= ay + ahalf):
                return True

    # a more thourough and expenisve col check for player to asteroid using pixel perfect col
    def colCheckPlayerAsteroid(self, a, pr):
        # general col detection
        if pr.colliderect(a.rect):
            # pixel collision
            pm = pygame.mask.from_surface(self.player.rotatedSurface.convert_alpha())
            am = pygame.mask.from_surface(a.img.convert_alpha())
            self.outline = pm.outline()
            self.outline2 = am.outline()

            offset = (
                a.x - a.size / 2 - self.player.rotatedRectangle.x, a.y - a.size / 2 - self.player.rotatedRectangle.y)
            if pm.overlap(am, offset):
                return True
        return False

    def update(self):
        clock.tick()
        # print(str(clock.get_fps()))
        self.count += 1

        if not self.gameover:
            # if there are more asteroids to spawn
            if self.spawnCount > 0:
                # if it has been a certain amount of time since last spawn, spawn another
                if self.count % self.asteroidSpawnTime == 0:
                    self.spawnCount -= 1
                    self.asteroids.append(
                        random.choice([SmallAsteroid(0, 0, 0, 0), MediumAsteroid(0, 0, 0, 0, self.newAsteroids),
                                       LargeAsteroid(0, 0, 0, 0, self.newAsteroids)]))
            else:
                # if there are no asteroids on screen then move to next "level""
                if len(self.asteroids) == 0:
                    incr = max(1, int(float(self.totalAsteroids) * 0.1))
                    self.totalAsteroids += incr
                    self.spawnCount = self.totalAsteroids
                    # move to next level of curriculum if scored greater than equal 20 pts per asteroid
                    if self.score >= self.astCount * 620:
                        self.astCount += 1
                    if self.asteroidSpawnTime > 100:
                        self.asteroidSpawnTime -= 2

            # update bullets,asteroids
            for b in self.bullets:
                b.move()
            for a in self.asteroids:
                a.move()
                a.checkPos()
                # col check between asteroid and player
                if self.colCheckPlayerAsteroid(a, self.player.rotatedRectangle):
                    self.lives -= 1
                    self.livesFlag = True
                    self.asteroids.pop(self.asteroids.index(a))
                    break

                # bullet collisions
                for b in self.bullets:
                    if self.collisionCheck(a.x, a.y, a.size, b.x, b.y, b.size):
                        self.score += a.hit()
                        self.asteroids.pop(self.asteroids.index(a))
                        self.bullets.pop(self.bullets.index(b))
                        break

            # add the new asteroids to list
            for n in self.newAsteroids:
                self.asteroids.append(n)
            self.newAsteroids.clear()

            # update player
            self.player.move()
            self.player.slow()
            self.player.checkPos()
            self.player.waitTime -= 1

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

    # simple distance
    def distance(self, ax, ay):
        dx, dy = self.player.x - ax, self.player.y - ay
        dist = math.hypot(dx, dy)
        return dist

    def checkLineIntersection(self, x1, y1, x2, y2, asteroid):
        # check for intersection between line and line at asteroid origin
        frontVertical1 = Point(asteroid.x + asteroid.size / 2, asteroid.y - asteroid.size / 2)
        frontVertical2 = Point(asteroid.x + asteroid.size / 2, asteroid.y + asteroid.size / 2)
        bottomHorizontal1 = Point(asteroid.x - asteroid.size / 2, asteroid.y - asteroid.size / 2)
        bottomHorizontal2 = Point(asteroid.x + asteroid.size / 2, asteroid.y - asteroid.size / 2)
        backVertical1 = Point(asteroid.x - asteroid.size / 2, asteroid.y - asteroid.size / 2)
        backVertical2 = Point(asteroid.x - asteroid.size / 2, asteroid.y + asteroid.size / 2)
        topHorizontal1 = Point(asteroid.x - asteroid.size / 2, asteroid.y + asteroid.size / 2)
        topHorizontal2 = Point(asteroid.x + asteroid.size / 2, asteroid.y + asteroid.size / 2)
        p1 = Point(x1, y1)
        p2 = Point(x2, y2)

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

        # set angle to player's angle
        angle = self.player.angle
        lines = 16  # number of radar lines
        radius = 400.0  # radius of radar
        radar = [0.0] * lines  # radar array, init to 0 each time

        # sort the list so that nearest is at the front and will be first added to radar
        self.asteroids = sorted(self.asteroids, key=lambda a: self.distance(a.x, a.y))
        # loop through N,NE,E,SE,S,SW,W,NW directions and check for asteroids if the player can "see" them
        for i in range(lines):
            # find the end point of the player's vision
            x2 = self.player.x + radius * math.sin(math.radians(angle))
            y2 = self.player.y + radius * math.cos(math.radians(angle))
            angle += 360.0 / lines  # next line
            if self.debug:
                self.radarLines.append(Point(x2, y2))  # add to debug to be drawn
            # check all asteroids for intersection
            for a in self.asteroids:
                if self.checkLineIntersection(self.player.x, self.player.y, x2, y2, a):
                    # set the value to the distance
                    radar[i] = (self.player.findDistanceToPoint(a.x, a.y) - a.size / 2.0) / (radius + 25)
                    if self.debug:
                        self.debugLines.append(Point(x2, y2))  # add this to be drawn
                    break
        self.radar = radar  # store radar
        # observation object to be returned including information about the player
        o = [(self.player.x + 50) / 900, (self.player.y + 50) / 900, self.player.velocityX / 3.6,
             self.player.velocityY / 3.6, self.player.angle / 360]
        # add radar info to observation
        o = o + list(radar)
        return o

    def action(self, action, k, alwaysRender):
        self.delta = self.score
        for i in range(k):
            self.actionSet(action)
            self.update()
            if alwaysRender:
                    self.redrawWindow()
            else:
                if self.debug:
                    self.redrawWindow()
        # get change in score
        self.delta = self.score - self.delta

    def hrlAction(self,aim, action,k,renderMode):
        self.delta = self.score
        for i in range(k):
            if aim:
                self.aimActions(action)
            else:
                self.noShootActions(action)
            self.update()
            if renderMode:
                    self.redrawWindow()
            else:
                if self.debug:
                    self.redrawWindow()
        # get change in score
        self.delta = self.score - self.delta

    def noShootActions(self, action):
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
            # do nothing
            pass

    # reduuced set of Actions
    def simpleActions(self, action):
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
            pass  # do nothing

    def noShootActions(self, action):
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
            # do nothing
            pass

    # set of actions for aiming
    def aimActions(self, action):
        if action == 0:
            self.player.turnLeft()
        elif action == 1:
            self.player.turnRight()
        elif action == 2:
            if self.player.shoot():
                self.bullets.append(Bullet(self.player.head, self.player.cosine, self.player.sine))
        elif action == 3:
            # do nothing
            pass

    # set of every action
    def multiActions(self, action):
        self.chosenAction = action
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


    def evaluateLives(self):
        reward =self.delta
        if self.livesFlag:
            reward = reward - 1000
            self.livesFlag = False  # reset flag
        return reward

    def evaluateAvoid(self):
        reward = self.evaluateLives()
        reward += 0.1
        return reward

    def evaluateIRL(self):
        # if aiming and shooting
        reward = self.evaluateLives()
        # reward for shooting
        if not radarIsEmpty(self.radar[8]) and 5 <= self.chosenAction <= 10:
            reward += 1

        # reward for moving forward when empty
        if ((radarIsClose(self.radar[0]) or radarIsClose(self.radar[1]) or radarIsClose(self.radar[15])) and
                (radarIsEmpty(self.radar[7]) or radarIsEmpty(self.radar[8]) or radarIsEmpty(self.radar[9]))):
            reward += 0.1

        #neg reward for being to close to edges
        if self.player.x < 50 or self.player.x > 750 or self.player.y < 50 or self.player.y >750 :
            reward -= 0.1
        return reward

    # check if is done
    def is_done(self):
        if self.lives <= 0:
            self.gameover = True
            return True
        else:
            return False
