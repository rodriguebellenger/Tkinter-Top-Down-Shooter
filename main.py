import tkinter as tk
from time import time
from math import sqrt

# COMMENT JOUER :
# z : déplacement ver le haut
# q : déplacement ver la gauche
# s : déplacement ver le bas
# d : déplacement ver la droite
# e : changement d'arme
# clique gauche : tire (possible de la maintenir)
# clique droit : fais apparaitre un ennemi qui vous poursuis

class Enemy:
    def __init__(self, root, canvas, player, enemies, x, y, enemy_type, health):
        self.root = root
        self.canvas = canvas
        self.player = player
        self.enemies = enemies
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.health = health
        self.size = 20  # Size of the enemy
        self.color = "green" if enemy_type == "basic" else "purple"
        self.id = self.canvas.create_oval(x, y, x + self.size, y + self.size, fill=self.color)

        self.state = "follow"
        self.follow_duration = 3

        self.damage_animation()
        self.follow()

    def take_damage(self, damage):
        self.health -= damage
        self.canvas.itemconfig(self.id, fill="red")
        if self.health <= 0:
            self.canvas.delete(self.id)
            return True
        return False
    
    def damage_animation(self):
        color = self.canvas.itemcget(self.id, "fill")
        if color == "red":
            self.canvas.itemconfig(self.id, fill="green")
        self.root.after(200, self.damage_animation)

    def follow(self):
        if self.canvas.find_withtag(self.id):
            px1, py1, px2, py2 = self.canvas.coords(self.player)
            cpx, cpy = (px1 + px2) / 2, (py1 + py2) / 2

            ex1, ey1, ex2, ey2 = self.canvas.coords(self.id)
            cex, cey = (ex1 + ex2) / 2, (ey1 + ey2) / 2
            
            dx = cpx - cex
            dy = cpy - cey
            dist = sqrt(dx**2 + dy**2)
            
            if dist > 0:
                dx = (dx / dist) * 4
                dy = (dy / dist) * 4

            for other in self.enemies:
                if other.id == self.id:
                    continue
                ox1, oy1, ox2, oy2 = self.canvas.coords(other.id)
                cox, coy = (ox1 + ox2) / 2, (oy1 + oy2) / 2
                
                sep_x = cex - cox
                sep_y = cey - coy
                sep_dist = sqrt(sep_x**2 + sep_y**2)
                
                if sep_dist < 25 and sep_dist > 0:
                    dx += (sep_x / sep_dist) * (30*(1/sep_dist))
                    dy += (sep_y / sep_dist) * (30*(1/sep_dist))

            self.canvas.move(self.id, dx, dy)

            self.root.after(20, self.follow)
        else:
            return

class MovableCircleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Top-Down Shooter")

        self.width = 1000
        self.height = 1000
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        self.mouse_x = 0 
        self.mouse_y = 0

        self.used_gun = 0
        self.weapon_stat = [{"Name":"Gun",           "Type":"Gun",     "ShootCooldown":450,  "Speed":7,  "Damage":10, "BulletSize":5},
                            {"Name":"Machine Gun",   "Type":"Gun",     "ShootCooldown":90,   "Speed":20, "Damage":3,  "BulletSize":5},
                            {"Name":"Super Gun",     "Type":"Gun",     "ShootCooldown":750,  "Speed":4,  "Damage":20, "BulletSize":15},
                            {"Name":"Shotgun",       "Type":"Shotgun", "ShootCooldown":600,  "Speed":9, "Damage":10, "BulletSize":5, "SpreadOffset":[-5, 0, 5]},
                            {"Name":"Super Shotgun", "Type":"Shotgun", "ShootCooldown":1000, "Speed":10, "Damage":10, "BulletSize":5, "SpreadOffset":[-6, -4, -2, 0, 2, 4, 6]},
                            {"Name":"Mega Shotgun",  "Type":"Shotgun", "ShootCooldown":1000, "Speed":10, "Damage":10, "BulletSize":5, "SpreadOffset":[x for x in range(-20, 21, 1)]}]
        
        self.weapon_text = self.canvas.create_text(5, self.height-25, text=f"{self.weapon_stat[self.used_gun]['Name']}", font=("Arial", 16), fill="black", anchor="nw")
        
        self.player = self.canvas.create_oval((self.width//2)-20, (self.height//2)-20, (self.width//2)+20, (self.height//2)+20, fill="blue")
        
        self.movement_speed = 5
        self.movement_active = {"Up": False, "Down": False, "Left": False, "Right": False}

        self.last_shot_time = 0

        self.shooting = False

        self.enemies = []

        self.root.bind("<Motion>", self.mouse_position)
        self.root.bind("<B1-Motion>", self.mouse_position)
        
        self.root.bind("<KeyPress-z>", self.start_move_up)
        self.root.bind("<KeyRelease-z>", self.stop_move_up)
        self.root.bind("<KeyPress-s>", self.start_move_down)
        self.root.bind("<KeyRelease-s>", self.stop_move_down)
        self.root.bind("<KeyPress-q>", self.start_move_left)
        self.root.bind("<KeyRelease-q>", self.stop_move_left)
        self.root.bind("<KeyPress-d>", self.start_move_right)
        self.root.bind("<KeyRelease-d>", self.stop_move_right)

        self.root.bind("<KeyPress-e>", self.switch_weapon)

        self.root.bind("<ButtonPress-1>", self.start_shooting)
        self.root.bind("<ButtonRelease-1>", self.stop_shooting)
        self.root.bind("<B1-Motion>", self.shoot_projectile, add="+")

        self.root.bind("<Button-3>", self.create_ennemi)

    def mouse_position(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
    
    def move(self):
        px1, py1, px2, py2 = self.canvas.coords(self.player)
        if self.movement_active["Up"] and py1 > 0:
            self.canvas.move(self.player, 0, -self.movement_speed)
        if self.movement_active["Down"] and py2 < self.height:
            self.canvas.move(self.player, 0, self.movement_speed)
        if self.movement_active["Left"] and px1 > 0:
            self.canvas.move(self.player, -self.movement_speed, 0)
        if self.movement_active["Right"] and px2 < self.width:
            self.canvas.move(self.player, self.movement_speed, 0)
        self.root.after(10, self.move)
    
    def start_move_up(self, event):
        self.movement_active["Up"] = True
    
    def stop_move_up(self, event):
        self.movement_active["Up"] = False
    
    def start_move_down(self, event):
        self.movement_active["Down"] = True
    
    def stop_move_down(self, event):
        self.movement_active["Down"] = False
    
    def start_move_left(self, event):
        self.movement_active["Left"] = True
    
    def stop_move_left(self, event):
        self.movement_active["Left"] = False
    
    def start_move_right(self, event):
        self.movement_active["Right"] = True
    
    def stop_move_right(self, event):
        self.movement_active["Right"] = False

    def start_shooting(self, event):
        self.shooting = True
        self.shoot_projectile(event)

    def stop_shooting(self, event):
        self.shooting = False

    def shoot_projectile(self, event):
        if self.shooting:
            if self.weapon_stat[self.used_gun]["Type"] == "Gun":
                self.gun()
            elif self.weapon_stat[self.used_gun]["Type"] == "Shotgun":
                self.shotgun()
            self.root.after(self.weapon_stat[self.used_gun]["ShootCooldown"], lambda: self.shoot_projectile(event))
        else:
            return
        
    def shotgun(self):
        current_time = time()*1000
        if current_time - self.last_shot_time <= self.weapon_stat[self.used_gun]["ShootCooldown"]:
            return
        self.last_shot_time = current_time

        x1, y1, x2, y2 = self.canvas.coords(self.player)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = self.mouse_x - cx, self.mouse_y - cy

        if dx == 0 and dy == 0:
            return
            
        length = sqrt(dx**2 + dy**2)
        norm_dx = dx / length
        norm_dy = dy / length

        perp_dx = -norm_dy
        perp_dy = norm_dx

        for offset in self.weapon_stat[self.used_gun]["SpreadOffset"]:
            new_dx = norm_dx + perp_dx * (offset / 50)
            new_dy = norm_dy + perp_dy * (offset / 50)

            # Re-normalize the final direction
            length = sqrt(new_dx**2 + new_dy**2)
            step_x = (new_dx / length) * self.weapon_stat[self.used_gun]["Speed"]
            step_y = (new_dy / length) * self.weapon_stat[self.used_gun]["Speed"]

            # Create projectile
            projectile = self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="red")

            def move_projectile(proj=projectile, sx=step_x, sy=step_y):
                self.canvas.move(proj, sx, sy)
                px1, py1, px2, py2 = self.canvas.coords(proj)

                for enemy in self.enemies[:]:  # Iterate over a copy of the list
                    ex1, ey1, ex2, ey2 = self.canvas.coords(enemy.id)
                    if px1 < ex2 and px2 > ex1 and py1 < ey2 and py2 > ey1:
                        if enemy.take_damage(self.weapon_stat[self.used_gun]["Damage"]):
                            self.enemies.remove(enemy)
                        self.canvas.delete(proj)  # Remove projectile on impact
                        return

                if 0 < px1 < self.width and 0 < py1 < self.height:
                    self.root.after(10, lambda: move_projectile(proj, sx, sy))
                else:
                    self.canvas.delete(proj)

            move_projectile()
            
    def gun(self):
        current_time = time()*1000
        if current_time - self.last_shot_time <= self.weapon_stat[self.used_gun]["ShootCooldown"]:
            return
        self.last_shot_time = current_time

        x1, y1, x2, y2 = self.canvas.coords(self.player)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = self.mouse_x - cx, self.mouse_y - cy
            
        if dx == 0 and dy == 0:
            return
            
        step_x = self.weapon_stat[self.used_gun]["Speed"] if dx > 0 else -self.weapon_stat[self.used_gun]["Speed"] if dx < 0 else 0
        step_y = self.weapon_stat[self.used_gun]["Speed"] if dy > 0 else -self.weapon_stat[self.used_gun]["Speed"] if dy < 0 else 0
            
        if abs(dx) > abs(dy):
            step_y = step_y * (abs(dy) / abs(dx))
        else:
            step_x = step_x * (abs(dx) / abs(dy))
            
        projectile = self.canvas.create_oval(cx-self.weapon_stat[self.used_gun]["BulletSize"], cy-self.weapon_stat[self.used_gun]["BulletSize"], cx+self.weapon_stat[self.used_gun]["BulletSize"], cy+self.weapon_stat[self.used_gun]["BulletSize"], fill="red")
            
        def move_projectile(proj=projectile, sx=step_x, sy=step_y):
            self.canvas.move(proj, sx, sy)
            px1, py1, px2, py2 = self.canvas.coords(proj)

            for enemy in self.enemies[:]:  # Iterate over a copy of the list
                ex1, ey1, ex2, ey2 = self.canvas.coords(enemy.id)
                if px1 < ex2 and px2 > ex1 and py1 < ey2 and py2 > ey1:
                    if enemy.take_damage(self.weapon_stat[self.used_gun]["Damage"]):
                        self.enemies.remove(enemy)
                    self.canvas.delete(proj)  # Remove projectile on impact
                    return

            if 0 < px1 < self.width and 0 < py1 < self.height:
                self.root.after(10, lambda: move_projectile(proj, sx, sy))
            else:
                self.canvas.delete(proj)

        move_projectile()
    
    def switch_weapon(self, event):
        self.used_gun += 1
        if self.used_gun == len(self.weapon_stat):
            self.used_gun = 0
        self.canvas.itemconfig(self.weapon_text, text=f"{self.weapon_stat[self.used_gun]['Name']}")

    def create_ennemi(self, event):
        self.enemies.append(Enemy(self.root, self.canvas, self.player, self.enemies, event.x, event.y, "basic", 20))

if __name__ == "__main__":
    root = tk.Tk()
    app = MovableCircleApp(root)
    app.move()
    root.mainloop()