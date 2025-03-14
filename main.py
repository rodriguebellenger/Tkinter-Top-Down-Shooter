import tkinter as tk
from time import time

class Enemy:
    def __init__(self, canvas, x, y, enemy_type, health):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.health = health
        self.size = 20  # Size of the enemy
        self.color = "green" if enemy_type == "basic" else "purple"
        self.id = self.canvas.create_oval(x, y, x + self.size, y + self.size, fill=self.color)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.canvas.delete(self.id)
            return True
        return False

class MovableCircleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Top-Down Shooter")

        self.width = 1000
        self.height = 1000
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        self.used_gun = 0
        self.weapon_stat = [{"Name":"Gun",         "ShootCooldown":0.2 , "Speed":10},
                            {"Name":"Machine Gun", "ShootCooldown":0.05, "Speed":17}]
        
        self.weapon_text = self.canvas.create_text(5, self.height-25, text=f"{self.weapon_stat[self.used_gun]['Name']}", font=("Arial", 16), fill="black", anchor="nw")
        
        self.player = self.canvas.create_oval((self.width//2)-20, (self.height//2)-20, (self.width//2)+20, (self.height//2)+20, fill="blue")
        
        self.movement_speed = 5
        self.movement_active = {"Up": False, "Down": False, "Left": False, "Right": False}

        self.last_shot_time = 0

        self.enemies = []
        
        self.root.bind("<KeyPress-z>", self.start_move_up)
        self.root.bind("<KeyRelease-z>", self.stop_move_up)
        self.root.bind("<KeyPress-s>", self.start_move_down)
        self.root.bind("<KeyRelease-s>", self.stop_move_down)
        self.root.bind("<KeyPress-q>", self.start_move_left)
        self.root.bind("<KeyRelease-q>", self.stop_move_left)
        self.root.bind("<KeyPress-d>", self.start_move_right)
        self.root.bind("<KeyRelease-d>", self.stop_move_right)

        self.root.bind("<KeyPress-e>", self.switch_weapon)

        self.root.bind("<Button-1>", self.shoot_projectile)
        self.root.bind("<Button-3>", self.create_ennemi)
    
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

    def shoot_projectile(self, event):
        current_time = time()
        if current_time - self.last_shot_time < self.weapon_stat[self.used_gun]["ShootCooldown"]:
            return
        self.last_shot_time = current_time

        # On trouve les deux coins du joueur
        x1, y1, x2, y2 = self.canvas.coords(self.player)
        # On calcul le centre
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        # On fait la différence entre ces coordonnée et les coordonnées du clic
        dx, dy = event.x - cx, event.y - cy
        
        if dx == 0 and dy == 0:
            return
        
        step_x = self.weapon_stat[self.used_gun]["Speed"] if dx > 0 else -self.weapon_stat[self.used_gun]["Speed"] if dx < 0 else 0
        step_y = self.weapon_stat[self.used_gun]["Speed"] if dy > 0 else -self.weapon_stat[self.used_gun]["Speed"] if dy < 0 else 0
        
        if abs(dx) > abs(dy):
            step_y = int(step_y * (abs(dy) / abs(dx)))
        else:
            step_x = int(step_x * (abs(dx) / abs(dy))) 
        
        projectile = self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="red")
        
        def move_projectile():
            self.canvas.move(projectile, step_x, step_y)
            px1, py1, px2, py2 = self.canvas.coords(projectile)

            for enemy in self.enemies[:]:  # Iterate over a copy of the list
                ex1, ey1, ex2, ey2 = self.canvas.coords(enemy.id)
                if px1 < ex2 and px2 > ex1 and py1 < ey2 and py2 > ey1:
                    if enemy.take_damage(1):
                        self.enemies.remove(enemy)
                    self.canvas.delete(projectile)  # Remove projectile on impact
                    return
                
            if 0 < px1 < self.width and 0 < py1 < self.height:
                self.root.after(10, move_projectile)
            else:
                self.canvas.delete(projectile)
        
        move_projectile()
    
    def switch_weapon(self, event):
        self.used_gun += 1
        if self.used_gun == len(self.weapon_stat):
            self.used_gun = 0
        self.canvas.itemconfig(self.weapon_text, text=f"{self.weapon_stat[self.used_gun]['Name']}")

    def create_ennemi(self, event):
        self.enemies.append(Enemy(self.canvas, event.x, event.y, "basic", 20))

if __name__ == "__main__":
    root = tk.Tk()
    app = MovableCircleApp(root)
    app.move()
    root.mainloop()