import tkinter as tk
from time import time
from math import sqrt
from random import randint, choices

# COMMENT JOUER :
# z : déplacement ver le haut
# q : déplacement ver la gauche
# s : déplacement ver le bas
# d : déplacement ver la droite
# e : changement d'arme
# espace : dash (rend invincible)
# clique gauche : tire (possible de la maintenir)
# clique droit : fais apparaitre un ennemi qui vous poursuis

# Si vous êtes touché, vous êtes invincible pendant 2 secondes
# A chaque niveau passé, vous pouvez : 
#    Soit gagner une arme (aléatoire) : 
#        Si vous posséder déjà l'arme, ses munitions sont ravitailler
#        Si vous ne l'aviez pas, vous la gagnez avec toutes ses munitions
#        Probabilité de chaque arme : 
#            Machine Gun : 28%
#            Super Gun : 27%
#            Shotgun : 28%
#            Super Shotgun : 13%
#            Mega Shotgun : 4%
#   Soit améliorer vos statistiques (aléatoire) : 
#       Soit vous allez plus vite
#       Soit vous régénérer un point de vide

class Enemy:
    def __init__(self, root, canvas, player, enemies, x, y, enemy_type):
        self.root = root
        self.canvas = canvas
        self.player = player
        self.enemies = enemies
        self.x = x
        self.y = y

        self.enemy_stat = {"basic" : {"size":20, "speed":4, "health":20, "color":"green"}, 
                           "tank"  : {"size":50, "speed":2, "health":80, "color":"purple"}, }

        self.enemy_type = enemy_type
        self.health = self.enemy_stat[self.enemy_type]["health"]
        self.size = self.enemy_stat[self.enemy_type]["size"]
        self.color = self.enemy_stat[self.enemy_type]["color"]
        self.id = self.canvas.create_oval(x, y, x + self.size, y + self.size, fill=self.color)

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
            self.canvas.itemconfig(self.id, fill=self.enemy_stat[self.enemy_type]["color"])
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
                dx = (dx / dist) * self.enemy_stat[self.enemy_type]["speed"]
                dy = (dy / dist) * self.enemy_stat[self.enemy_type]["speed"]

            for other in self.enemies:
                if other.id == self.id:
                    continue
                ox1, oy1, ox2, oy2 = self.canvas.coords(other.id)
                cox, coy = (ox1 + ox2) / 2, (oy1 + oy2) / 2
                
                sep_x = cex - cox
                sep_y = cey - coy
                sep_dist = sqrt(sep_x**2 + sep_y**2)
                
                if sep_dist < self.enemy_stat[self.enemy_type]["size"]+5 and sep_dist > 0:
                    dx += (sep_x / sep_dist) * (30*(1/sep_dist))
                    dy += (sep_y / sep_dist) * (30*(1/sep_dist))

            self.canvas.move(self.id, dx, dy)

            self.root.after(20, self.follow)
        else:
            return

class TopDownShooter:
    def __init__(self, root):
        self.root = root
        self.root.title("Top-Down Shooter")

        self.width = 1000
        self.height = 1000
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        self.playing = True
        self.immortality = False
        self.dashing_step = 0
        self.dashing_directions = []
        self.dashing = False

        self.player = self.canvas.create_oval((self.width//2)-20, (self.height//2)-20, (self.width//2)+20, (self.height//2)+20, fill="blue")
        self.movement_speed = 5
        self.health = 3
        self.health_bar = self.canvas.create_text(5, 5, text=f"{self.health}/3", font=("Arial", 55), fill="red", anchor="nw")

        self.enemies = []
        self.current_level = 0
        self.create_levels(10)
        self.start_game()

        self.mouse_x = 0 
        self.mouse_y = 0

        self.unlockable_guns =   ["Machine Gun", "Super Gun", "Shotgun", "Super Shotgun", "Mega Shotgun"]
        self.gun_probabilities = [28, 27, 28, 13, 4]
        self.weapon_stat = {"Gun" :            {"Type":"Gun",     "MaxAmmo":"Inf", "ShootCooldown":450,  "Speed":7,  "Damage":10, "BulletSize":5},
                            "Machine Gun" :    {"Type":"Gun",     "MaxAmmo":1000,  "ShootCooldown":90,   "Speed":20, "Damage":3,  "BulletSize":5},
                            "Super Gun" :      {"Type":"Gun",     "MaxAmmo":25,    "ShootCooldown":750,  "Speed":4,  "Damage":20, "BulletSize":15},
                            "Shotgun" :        {"Type":"Shotgun", "MaxAmmo":50,    "ShootCooldown":600,  "Speed":9,  "Damage":10, "BulletSize":[5, 10, 5],                                                 "SpreadOffset":[-5, 0, 5]},
                            "Super Shotgun" :  {"Type":"Shotgun", "MaxAmmo":30,    "ShootCooldown":800,  "Speed":10, "Damage":10, "BulletSize":[5, 7, 9, 11, 9, 7, 5],                                     "SpreadOffset":[-6, -4, -2, 0, 2, 4, 6]},
                            "Mega Shotgun" :   {"Type":"Shotgun", "MaxAmmo":20,    "ShootCooldown":1000, "Speed":10, "Damage":10, "BulletSize":[x for x in range(1, 21, 1)]+[x for x in range(21, 0, -1)], "SpreadOffset":[x for x in range(-20, 21, 1)]},
                            "Cheat Shotgun" :  {"Type":"Shotgun", "MaxAmmo":"Inf", "ShootCooldown":100,  "Speed":10, "Damage":10, "BulletSize":[x for x in range(1, 21, 1)]+[x for x in range(21, 0, -1)], "SpreadOffset":[x for x in range(-20, 21, 1)]}}

        self.used_gun = 0
        self.inventory = [{"Name":"Gun", "Ammo":"inf"}]
        
        self.weapon_text = self.canvas.create_text(5, 70, text=f"{self.inventory[self.used_gun]['Name']} : {self.inventory[self.used_gun]['Ammo']}/{self.weapon_stat[self.inventory[self.used_gun]['Name']]['MaxAmmo']}", font=("Arial", 35), fill="black", anchor="nw")

        self.movement_active = {"Up": False, "Down": False, "Left": False, "Right": False}

        self.last_shot_time = 0
        self.last_hit = 0

        self.shooting = False

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

        self.root.bind("<space>", self.dash)

        self.move()
        self.damage()

    def create_levels(self, numberOflevels):
        self.levels = []
        for i in range(1, numberOflevels+1):
            self.levels.append(i+randint(-(i//4), i//4))

    def start_game(self):
        if self.current_level == len(self.levels) and len(self.enemies) == 0:
            self.playing = False
            self.open_popup("Victoire", "Vous avez gagné !!! Félicitation !!")
        if self.playing:
            if len(self.enemies) == 0:
                for _ in range(self.levels[self.current_level]):
                    self.enemies.append(Enemy(self.root, self.canvas, self.player, self.enemies, randint(0, self.width), randint(0, self.height), self.random_enemy_type()))
                if self.current_level != 0:
                    self.reward()
                self.current_level += 1
            self.root.after(100, self.start_game)

    def open_popup(self, title, text):
        popup = tk.Toplevel(root)
        popup.title(title)
        popup.geometry("250x100")
        
        label = tk.Label(popup, text=text)
        label.pack(pady=10)

        bouton_fermer = tk.Button(popup, text="Arrêter de jouer", command=lambda: (popup.destroy(), self.root.destroy()))
        bouton_fermer.pack()

    def random_enemy_type(self):
        random = randint(0, 100)
        if 0 <= random <= 20:
            return "tank"
        else:
            return "basic"
        
    def reward(self):
        reward = randint(1, 2)
        if reward == 1:
            self.gun_reward()
        else:
            self.stat_reward()
    
    def gun_reward(self):
        random_gun = choices(self.unlockable_guns, weights=self.gun_probabilities)[0]
        for gun in self.inventory:
            if gun["Name"] == random_gun:
                gun["Ammo"] = self.weapon_stat[random_gun]["MaxAmmo"]
                self.canvas.itemconfig(self.weapon_text, text=f"{self.inventory[self.used_gun]['Name']} : {self.inventory[self.used_gun]['Ammo']}/{self.weapon_stat[self.inventory[self.used_gun]['Name']]['MaxAmmo']}")
                return
        self.inventory.append({"Name":random_gun, "Ammo": self.weapon_stat[random_gun]["MaxAmmo"]})

    def stat_reward(self):
        reward = randint(1, 2)
        if reward == 1:
            self.movement_speed += 1
        else:
            self.health += 1
            self.canvas.itemconfig(self.health_bar, text=f"{self.health}/3")

    def mouse_position(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def dash(self, event):
        if self.dashing_step == 0 and not self.dashing:
            self.dashing = True
            self.immortality = True
            self.canvas.itemconfig(self.player, fill="white")
            if self.movement_active["Up"] == True:
                self.dashing_directions.append("up")
            if self.movement_active["Down"] == True:
                self.dashing_directions.append("down")
            if self.movement_active["Left"] == True:
                self.dashing_directions.append("left")
            if self.movement_active["Right"] == True:
                self.dashing_directions.append("right")
        elif self.dashing_step == 15:
            self.dashing_directions = []
            self.immortality = False
            self.dashing = False
            self.dashing_step = 0
            self.canvas.itemconfig(self.player, fill="green")
            self.move()
            return

        if self.dashing:
            for direction in self.dashing_directions:
                px1, py1, px2, py2 = self.canvas.coords(self.player)
                if direction == "up" and py1 > 0:
                    self.canvas.move(self.player, 0, -self.movement_speed*2)
                if direction == "down" and py2 < self.height:
                    self.canvas.move(self.player, 0, self.movement_speed*2)
                if direction == "left" and px1 > 0:
                    self.canvas.move(self.player, -self.movement_speed*2, 0)
                if direction == "right" and px2 < self.width:
                    self.canvas.move(self.player, self.movement_speed*2, 0)

            self.dashing_step += 1
            self.root.after(10, lambda : self.dash(event))

    def damage(self):
        if self.playing:
            x1, y1, x2, y2 = self.canvas.coords(self.player)

            for enemy in self.enemies:
                a1, b1, a2, b2 = self.canvas.coords(enemy.id)
                if not (x2 < a1 or a2 < x1 or y2 < b1 or b2 < y1) and not self.immortality:
                    self.health -= 1
                    if self.health == 0:
                        self.open_popup("Perdu", "Vous êtes malheureusement mort")
                        self.playing = False
                    self.last_hit = time()
                    self.canvas.itemconfig(self.health_bar, text=f"{self.health}/3")
                    self.immortality = True
                    self.canvas.itemconfig(self.player, fill="white")

            if time()-self.last_hit >= 2 and not self.dashing:
                self.immortality = False
                self.canvas.itemconfig(self.player, fill="green")
            
            self.root.after(10, self.damage)
    
    def move(self):
        if not self.playing or self.dashing:
            return
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
        if self.shooting and self.playing and self.inventory[self.used_gun]["Ammo"] != 0:
            if self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Type"] == "Gun":
                self.gun()
            elif self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Type"] == "Shotgun":
                self.shotgun()

            if hasattr(self, "shoot_id"):
                self.root.after_cancel(self.shoot_id)

            self.shoot_id = self.root.after(self.weapon_stat[self.inventory[self.used_gun]["Name"]]["ShootCooldown"], lambda: self.shoot_projectile(event))
        
    def shotgun(self):
        current_time = time()*1000
        if current_time - self.last_shot_time <= self.weapon_stat[self.inventory[self.used_gun]["Name"]]["ShootCooldown"]:
            return
        self.last_shot_time = current_time

        if self.inventory[self.used_gun]["Ammo"] != "inf":
            self.inventory[self.used_gun]["Ammo"] -= 1
        self.canvas.itemconfig(self.weapon_text, text=f"{self.inventory[self.used_gun]['Name']} : {self.inventory[self.used_gun]['Ammo']}/{self.weapon_stat[self.inventory[self.used_gun]['Name']]['MaxAmmo']}")

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

        for i in range(len(self.weapon_stat[self.inventory[self.used_gun]["Name"]]["SpreadOffset"])):
            new_dx = norm_dx + perp_dx * (self.weapon_stat[self.inventory[self.used_gun]["Name"]]["SpreadOffset"][i] / 50)
            new_dy = norm_dy + perp_dy * (self.weapon_stat[self.inventory[self.used_gun]["Name"]]["SpreadOffset"][i] / 50)

            # Re-normalize the final direction
            length = sqrt(new_dx**2 + new_dy**2)
            step_x = (new_dx / length) * self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Speed"]
            step_y = (new_dy / length) * self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Speed"]

            bullet_size = self.weapon_stat[self.inventory[self.used_gun]["Name"]]["BulletSize"][i]
            projectile = self.canvas.create_oval(cx-bullet_size, cy-bullet_size, cx+bullet_size, cy+bullet_size, fill="red")

            def move_projectile(proj=projectile, sx=step_x, sy=step_y):
                self.canvas.move(proj, sx, sy)
                px1, py1, px2, py2 = self.canvas.coords(proj)

                for enemy in self.enemies[:]:  # Iterate over a copy of the list
                    ex1, ey1, ex2, ey2 = self.canvas.coords(enemy.id)
                    if px1 < ex2 and px2 > ex1 and py1 < ey2 and py2 > ey1:
                        if enemy.take_damage(self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Damage"]):
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
        if current_time - self.last_shot_time <= self.weapon_stat[self.inventory[self.used_gun]["Name"]]["ShootCooldown"]:
            return
        self.last_shot_time = current_time

        if self.inventory[self.used_gun]["Ammo"] != "inf":
            self.inventory[self.used_gun]["Ammo"] -= 1
        self.canvas.itemconfig(self.weapon_text, text=f"{self.inventory[self.used_gun]['Name']} : {self.inventory[self.used_gun]['Ammo']}/{self.weapon_stat[self.inventory[self.used_gun]['Name']]['MaxAmmo']}")

        x1, y1, x2, y2 = self.canvas.coords(self.player)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = self.mouse_x - cx, self.mouse_y - cy
            
        if dx == 0 and dy == 0:
            return
            
        step_x = self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Speed"] if dx > 0 else -self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Speed"] if dx < 0 else 0
        step_y = self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Speed"] if dy > 0 else -self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Speed"] if dy < 0 else 0
            
        if abs(dx) > abs(dy):
            step_y = step_y * (abs(dy) / abs(dx))
        else:
            step_x = step_x * (abs(dx) / abs(dy))
            
        bullet_size = self.weapon_stat[self.inventory[self.used_gun]["Name"]]["BulletSize"]
        projectile = self.canvas.create_oval(cx-bullet_size, cy-bullet_size, cx+bullet_size, cy+bullet_size, fill="red")
            
        def move_projectile(proj=projectile, sx=step_x, sy=step_y):
            self.canvas.move(proj, sx, sy)
            px1, py1, px2, py2 = self.canvas.coords(proj)

            for enemy in self.enemies[:]:  # Iterate over a copy of the list
                ex1, ey1, ex2, ey2 = self.canvas.coords(enemy.id)
                if px1 < ex2 and px2 > ex1 and py1 < ey2 and py2 > ey1:
                    if enemy.take_damage(self.weapon_stat[self.inventory[self.used_gun]["Name"]]["Damage"]):
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
        if self.used_gun == len(self.inventory):
            self.used_gun = 0
        self.canvas.itemconfig(self.weapon_text, text=f"{self.inventory[self.used_gun]['Name']} : {self.inventory[self.used_gun]['Ammo']}/{self.weapon_stat[self.inventory[self.used_gun]['Name']]['MaxAmmo']}")

    # def create_ennemi(self, event):
    #     self.enemies.append(Enemy(self.root, self.canvas, self.player, self.enemies, event.x, event.y, "basic", 20))

if __name__ == "__main__":
    root = tk.Tk()
    app = TopDownShooter(root)
    root.mainloop()