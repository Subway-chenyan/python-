import pygame
import sys
import traceback
import myplant
import enemy
import bullet
import supply
from pygame.locals import *
from random import *

pygame.init()
pygame.mixer.init()

bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption("飞机大战")

background = pygame.image.load("images/background.png").convert()


BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
# #载入游戏音乐
pygame.mixer.music.load("sound/backmusic.mp3")
pygame.mixer.music.set_volume(0.2)
# bomb_sound = pygame.mixer.Sound("sound/bomb.mp3")
# bomb_sound.set_volume(0.2)
# gameover = pygame.mixer.Sound("sound/gameover.mp3")
# gameover.set_volume(0.2)

def add_small_enemies(group1, group2, num):
    for i in range(num):
        e1 = enemy.smallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)

def add_mid_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.midEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)

def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.bigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)

def inc_speed(target, inc):
    for each in target:
        each.speed += inc

def main():
    pygame.mixer.music.play(-1)
    score = 0
    level = 1
    score_font = pygame.font.Font("font/font.ttf", 36)
    #全屏炸弹
    bomb_image = pygame.image.load("images/bomb.png").convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font("font/font.ttf", 48)
    bomb_num = 3
    #每30s生成一个补给包
    bullet_supply = supply.Bullet_Supply(bg_size)
    bomb_supply = supply.Bomb_Supply(bg_size)
    SUPPLY_TIME = USEREVENT
    pygame.time.set_timer(SUPPLY_TIME, 10*1000)

    #超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1
    is_double_bullet = False
    #设置生命次数
    life_num = 3
    life_image = pygame.image.load("images/life.png")
    life_rect = life_image.get_rect()

    #标志是否暂停游戏
    paused = False
    pause_nor_image = pygame.image.load("images/pause_nor.png").convert_alpha()
    pause_pressed_image = pygame.image.load("images/pause_pressed.png").convert_alpha()
    resume_nor_image = pygame.image.load("images/resume_nor.png").convert_alpha()
    resume_pressed_image = pygame.image.load("images/resume_pressed.png").convert_alpha()
    paused_rect = pause_nor_image.get_rect()
    paused_rect.left, paused_rect.top = width - paused_rect.width - 10, 10
    pause_image = pause_nor_image
    # 重新开始结束游戏
    again = pygame.image.load("images/again.png").convert_alpha()
    gameover = pygame.image.load("images/gameover.png").convert_alpha()
    again_rect = again.get_rect()
    gameover_rect = gameover.get_rect()
    #生成我方飞机
    me = myplant.Myplane(bg_size)
    #切换飞机图片
    transPlane = True
    #延迟变量
    delay=100
    #生成敌机
    enemies = pygame.sprite.Group()
    #摧毁图片索引
    small_destroy = 0
    mid_destroy = 0
    big_destroy = 0
    my_destroy = 0

    small_enenmies = pygame.sprite.Group()
    add_small_enemies(small_enenmies, enemies, 15)

    mid_enenmies = pygame.sprite.Group()
    add_mid_enemies(mid_enenmies, enemies, 4)

    big_enenmies = pygame.sprite.Group()
    add_big_enemies(big_enenmies, enemies, 1)

    #生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 4
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(me.rect.midtop))

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 8
    for i in range(BULLET2_NUM//2):
        bullet2.append(bullet.Bullet2((me.rect.centerx-33, me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx+30, me.rect.centery)))
    clock = pygame.time.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                # 重新开始 结束游戏
                if event.button == 1 and gameover_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                if event.button == 1 and again_rect.collidepoint(event.pos):
                    main()

                if event.button == 1 and paused_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                        pygame.mixer.music.pause()
                    else:
                        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
                        pygame.mixer.music.unpause()

            elif event.type == MOUSEMOTION:

                if paused_rect.collidepoint(event.pos):
                    if paused:
                        pause_image = resume_pressed_image
                    else:
                        pause_image = pause_pressed_image
                else:
                    if paused:
                        pause_image = resume_nor_image
                    else:
                        pause_image = pause_nor_image
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each.active = False

            elif event.type == SUPPLY_TIME:
                if randint(0, 2):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()

            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)

        #根据用户得分增加难度
        if level == 1 and score > 50000:
            level = 2
            #增加3小2中1大
            add_small_enemies(small_enenmies, enemies, 3)
            add_mid_enemies(mid_enenmies, enemies, 2)
            add_big_enemies(big_enenmies, enemies, 1)
            #提升小型速度
            inc_speed(small_enenmies, 1)
        elif level == 2 and score > 200000:
            level = 3
            #增加3小2中1大
            add_small_enemies(small_enenmies, enemies, 5)
            add_mid_enemies(mid_enenmies, enemies, 3)
            add_big_enemies(big_enenmies, enemies, 2)
            #提升小型速度
            inc_speed(small_enenmies, 1)
            inc_speed(mid_enenmies, 1)
        elif level == 3 and score > 600000:
            level = 4
            #增加3小2中1大
            add_small_enemies(small_enenmies, enemies, 5)
            add_mid_enemies(mid_enenmies, enemies, 3)
            add_big_enemies(big_enenmies, enemies, 2)
            #提升小型速度
            inc_speed(small_enenmies, 1)
            inc_speed(mid_enenmies, 1)
        elif level == 4 and score > 1000000:
            level = 5
            #增加3小2中1大
            add_small_enemies(small_enenmies, enemies, 5)
            add_mid_enemies(mid_enenmies, enemies, 3)
            add_big_enemies(big_enenmies, enemies, 2)
            #提升小型速度
            inc_speed(small_enenmies, 1)
            inc_speed(mid_enenmies, 1)
        screen.blit(background, (0, 0))
    #游戏动态程序

        if paused or life_num == 0:
            pygame.time.set_timer(SUPPLY_TIME, 0)
            pygame.mixer.music.pause()
            screen.blit(again, ((width - again_rect.width)//2, height//2 - 20))
            screen.blit(gameover, ((width - gameover_rect.width) // 2, height // 2 + 20))
        else:
            # 检测键盘操作
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_w] or key_pressed[K_UP]:
                me.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                me.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                me.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                me.moveRight()

            #绘制全屏炸弹并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, me):
                    bomb_num += 1
                    bomb_supply.active = False

            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me):
                    is_double_bullet = True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 10*1000)
                    bullet_supply.active = False

            #绘制大型敌机
            for each in big_enenmies:
                if each.active:
                    each.move()
                    if transPlane and (delay % 5 == 0):
                        screen.blit(each.image1, each.rect)
                    else:
                        screen.blit(each.image2, each.rect)

                    #绘制血槽
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.right, each.rect.top - 5),
                                     2)
                    #当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.bigEnemy.energy

                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),
                                     2)
                else:
                    #毁灭

                    if not(delay % 3):
                        screen.blit(each.destroy_images[big_destroy], each.rect)
                        big_destroy = (big_destroy + 1) % 6
                        if big_destroy == 0:
                            each.reset()
                            score += 10000


          #绘制中小型机
            for each in mid_enenmies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.right, each.rect.top - 5),
                                     2)
                    # 当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.midEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),
                                     2)
                else:

                    if not(delay % 3):
                        screen.blit(each.destroy_images[mid_destroy], each.rect)
                        mid_destroy = (mid_destroy + 1) % 4
                        if mid_destroy == 0:
                            each.reset()
                            score += 6000

            for each in small_enenmies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:

                    if not(delay % 3):
                        screen.blit(each.destroy_images[small_destroy], each.rect)
                        small_destroy = (small_destroy + 1) % 4
                        if small_destroy == 0:
                            each.reset()
                            score += 1000

            #检测我方飞机是否被撞
            enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
            if enemies_down:
                me.active = False

                for e in enemies_down:
                    e.active = False
            #绘制我方飞机
            if me.active:
                transPlane = not transPlane
                if transPlane and (delay % 5 == 0):
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:

                if not (delay % 3):
                    screen.blit(me.destroy_images[my_destroy], me.rect)
                    my_destroy = (my_destroy + 1) % 4
                    if my_destroy == 0:
                        life_num -= 1
                        me.reset()

            #绘制子弹
            if not(delay % 10):
                if is_double_bullet:
                    bullets = bullet2
                    bullets[bullet2_index].reset((me.rect.centerx-33, me.rect.centery))
                    bullets[bullet2_index+1].reset((me.rect.centerx+30, me.rect.centery))
                    bullet2_index = (bullet2_index + 2) % BULLET2_NUM
                else:
                    bullets = bullet1
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM

            #发射子弹检测是否击中敌机
            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemy_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemy_hit:
                        b.active = False
                        for e in enemy_hit:
                            if e not in small_enenmies:
                                screen.blit(e.image_hit, e.rect)
                            e.energy -= 1
                            if e.energy == 0:
                                e.active = False



        delay -= 1
        if not delay:
            delay = 100
        screen.blit(pause_image, paused_rect)
        score_text = score_font.render("Score : %s" % str(score), True, BLACK)
        screen.blit(score_text, (10, 5))
        # 绘制炸弹数量
        bomb_text = bomb_font.render(" * %d" % bomb_num, True, RED)
        text_rect = bomb_text.get_rect()
        screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
        screen.blit(bomb_text, (20 + bomb_rect.width, height - 5 - text_rect.height))
        # 绘制生命次数

        life_text = score_font.render("* %d" % life_num, True, RED)
        life_text_rect = life_text.get_rect()
        screen.blit(life_image, (width - life_text_rect.width - 30 - life_rect.width, height - 5 - life_rect.height))
        screen.blit(life_text, (width - life_text_rect.width - 20, height - 5 - life_text_rect.height))


        pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()