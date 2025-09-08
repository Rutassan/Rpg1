"""Simplified 2D version of the RPG game using pygame.

This module introduces a basic graphical interface with selectable hero
classes (Warrior, Mage and Rogue), simple sprites, hit point bars and a
button based combat system.  Events and the shop are also displayed in
2D windows.  The underlying game logic remains close to the original
text version but everything is now shown on screen instead of printed in
the terminal.

The module is intentionally compact – graphics are represented by plain
rectangles and most animations are realised via short flashing effects
or floating text numbers.

The code is written so that it can be executed in environments without a
real display (e.g. in automated tests) by setting the SDL video driver to
"dummy" before running the game:

    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

"""

from __future__ import annotations

import random
from typing import List

import pygame


# ---------------------------------------------------------------------------
# Constants and globals initialised in ``main``.

WIDTH, HEIGHT = 800, 400

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
GREY = (60, 60, 60)

SCREEN: pygame.Surface  # set in main
CLOCK: pygame.time.Clock
FONT: pygame.font.Font
BIG_FONT: pygame.font.Font


# ---------------------------------------------------------------------------
# Helper classes


class Button:
    """Simple clickable rectangle with text."""

    def __init__(self, rect: tuple[int, int, int, int], text: str):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        txt = FONT.render(self.text, True, BLACK)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class FloatingText:
    """Small piece of text that floats upward for a short time."""

    def __init__(self, text: str, pos: pygame.Vector2, color: tuple[int, int, int]):
        self.image = FONT.render(text, True, color)
        self.pos = pygame.Vector2(pos)
        self.timer = 60

    def update(self) -> None:
        self.pos.y -= 1
        self.timer -= 1

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.pos)

    def alive(self) -> bool:
        return self.timer > 0


# ---------------------------------------------------------------------------
# Core character classes


class Character:
    def __init__(self, name: str, hp: int, attack: int, defense: int, pos: tuple[int, int]):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.pos = pygame.Vector2(pos)
        self.width = 60
        self.height = 80
        self.flash_timer = 0

    # ------------------------------------------------------------------
    def is_alive(self) -> bool:
        return self.hp > 0

    # ------------------------------------------------------------------
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.width, self.height)

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (200, 200, 200), self.rect())

        # HP bar
        ratio = self.hp / self.max_hp
        bar_back = pygame.Rect(self.pos.x, self.pos.y - 12, self.width, 6)
        pygame.draw.rect(surface, RED, bar_back)
        bar_front = pygame.Rect(self.pos.x, self.pos.y - 12, self.width * ratio, 6)
        pygame.draw.rect(surface, GREEN, bar_front)

        # Flash effect when taking damage
        if self.flash_timer > 0:
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill(RED)
            overlay.set_alpha(120)
            surface.blit(overlay, self.pos)
            self.flash_timer -= 1

    # ------------------------------------------------------------------
    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        self.flash_timer = 10

    # ------------------------------------------------------------------
    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)


class Hero(Character):
    def __init__(self, name: str, hp: int, attack: int, defense: int, gold: int, pos: tuple[int, int]):
        super().__init__(name, hp, attack, defense, pos)
        self.gold = gold

    # --------------------------------------------------------------
    def normal_attack(self, target: "Character", effects: List[FloatingText]) -> None:
        damage = max(1, self.attack - target.defense)
        # Rogue critical strike
        if isinstance(self, Rogue) and random.random() < 0.3:
            damage *= 2
            effects.append(FloatingText(f"-{damage} (крит)", target.pos - (0, 20), RED))
        else:
            effects.append(FloatingText(f"-{damage}", target.pos - (0, 20), RED))
        target.take_damage(damage)

    # --------------------------------------------------------------
    def strong_attack(self, target: "Character", effects: List[FloatingText]) -> None:
        if random.random() < 0.7:  # 70% chance to hit
            if isinstance(self, Mage):
                base = int(self.attack * 2.5)
            else:
                base = self.attack * 2
            damage = max(1, base - target.defense)
            effects.append(FloatingText(f"-{damage}", target.pos - (0, 20), RED))
            target.take_damage(damage)
        else:
            effects.append(FloatingText("промах", target.pos - (0, 20), WHITE))

    # --------------------------------------------------------------
    def heal_action(self, effects: List[FloatingText]) -> None:
        amount = int(self.max_hp * 0.3)
        self.heal(amount)
        effects.append(FloatingText(f"+{amount}", self.pos - (0, 20), GREEN))


class Warrior(Hero):
    def __init__(self, pos: tuple[int, int]):
        super().__init__("Воин", hp=120, attack=25, defense=8, gold=20, pos=pos)


class Mage(Hero):
    def __init__(self, pos: tuple[int, int]):
        super().__init__("Маг", hp=80, attack=18, defense=3, gold=20, pos=pos)


class Rogue(Hero):
    def __init__(self, pos: tuple[int, int]):
        super().__init__("Разбойник", hp=90, attack=20, defense=4, gold=20, pos=pos)


class Enemy(Character):
    def attack_action(self, target: Character, effects: List[FloatingText]) -> None:
        damage = max(1, self.attack - target.defense)
        effects.append(FloatingText(f"-{damage}", target.pos - (0, 20), RED))
        target.take_damage(damage)


# ---------------------------------------------------------------------------
# UI helper functions


def present_choice(message: str, options: List[str]) -> int:
    """Display a simple window with a message and several choice buttons.

    Returns the index of the clicked button or -1 if the window was closed.
    """

    buttons: List[Button] = []
    start_x = (WIDTH - (len(options) * 190 - 10)) // 2
    for i, opt in enumerate(options):
        buttons.append(Button((start_x + i * 190, 220, 180, 40), opt))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, btn in enumerate(buttons):
                    if btn.is_clicked(event.pos):
                        return idx

        SCREEN.fill(GREY)
        text = BIG_FONT.render(message, True, WHITE)
        SCREEN.blit(text, text.get_rect(center=(WIDTH // 2, 150)))
        for btn in buttons:
            btn.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(60)


def present_message(message: str) -> None:
    present_choice(message, ["Ок"])


# ---------------------------------------------------------------------------
# Game specific sequences: events, shop and battle


def random_event(hero: Hero) -> None:
    event = random.choice(["wanderer", "chest", "dawn"])
    if event == "wanderer":
        choice = present_choice(
            "Таинственный путник",
            ["Отдать 5 HP за 10 золота", "Отказаться"],
        )
        if choice == 0 and hero.hp > 5:
            hero.take_damage(5)
            hero.gold += 10
            present_message("Вы получили 10 золота.")
    elif event == "chest":
        choice = present_choice("Вы находите сундук", ["Открыть", "Пройти мимо"])
        if choice == 0:
            if random.random() < 0.5:
                bonus = random.choice(["attack", "defense"])
                if bonus == "attack":
                    hero.attack += 2
                    present_message("+2 к атаке")
                else:
                    hero.defense += 2
                    present_message("+2 к защите")
            else:
                hero.take_damage(3)
                present_message("Пусто! -3 HP")
    else:  # dawn
        choice = present_choice("Наступает рассвет", ["+1 к атаке", "+5 HP"])
        if choice == 0:
            hero.attack += 1
            present_message("Атака увеличена")
        else:
            hero.heal(5)
            present_message("Восстановлено 5 HP")


def open_shop(hero: Hero) -> None:
    items = [
        {"name": "Стальной меч", "attack": 2, "cost": 10},
        {"name": "Щит стража", "defense": 2, "cost": 12},
        {"name": "Амулет жизни", "hp": 10, "cost": 15},
    ]

    offer = random.sample(items, 2)

    def describe(item: dict) -> str:
        if "attack" in item:
            return f"+{item['attack']} к атаке"
        if "defense" in item:
            return f"+{item['defense']} к защите"
        return f"+{item['hp']} HP"

    options = [
        f"{offer[0]['name']} ({describe(offer[0])}) - {offer[0]['cost']} золота",
        f"{offer[1]['name']} ({describe(offer[1])}) - {offer[1]['cost']} золота",
        "Выход",
    ]

    choice = present_choice(f"Магазин. Золото: {hero.gold}", options)
    if choice in (0, 1):
        item = offer[choice]
        if hero.gold >= item["cost"]:
            hero.gold -= item["cost"]
            if "attack" in item:
                hero.attack += item["attack"]
            elif "defense" in item:
                hero.defense += item["defense"]
            else:
                hero.max_hp += item["hp"]
                hero.hp += item["hp"]
            present_message("Покупка совершена")
        else:
            present_message("Недостаточно золота")


def camp(hero: Hero) -> None:
    choice = present_choice(
        "Лагерь. Ваши действия?", ["Отдохнуть (+30 HP)", "Бафф (+3 к защите)"]
    )
    if choice == 0:
        hero.heal(30)
        present_message("Вы отдыхаете")
    else:
        hero.defense += 3
        present_message("Защита увеличена")


def upgrade(hero: Hero) -> None:
    choice = present_choice("Выберите повышение", ["+5 HP", "+2 к атаке"])
    if choice == 0:
        hero.max_hp += 5
        hero.hp += 5
    else:
        hero.attack += 2


def run_battle(hero: Hero, enemies: List[Enemy]) -> bool:
    """Main battle loop rendered via pygame."""

    buttons = [
        Button((50, HEIGHT - 70, 120, 40), "Атака"),
        Button((200, HEIGHT - 70, 150, 40), "Сильная атака"),
        Button((380, HEIGHT - 70, 120, 40), "Лечение"),
    ]

    effects: List[FloatingText] = []
    action: str | None = None

    while hero.is_alive() and any(e.is_alive() for e in enemies):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].is_clicked(event.pos):
                    action = "attack"
                elif buttons[1].is_clicked(event.pos):
                    action = "strong"
                elif buttons[2].is_clicked(event.pos):
                    action = "heal"

        if action:
            target = next(e for e in enemies if e.is_alive())
            if action == "attack":
                hero.normal_attack(target, effects)
            elif action == "strong":
                hero.strong_attack(target, effects)
            elif action == "heal":
                hero.heal_action(effects)
            action = None

            if not target.is_alive():
                effects.append(FloatingText("повержен", target.pos - (0, 20), WHITE))

            for enemy in enemies:
                if enemy.is_alive():
                    enemy.attack_action(hero, effects)
                    if not hero.is_alive():
                        break

        SCREEN.fill(GREY)
        hero.draw(SCREEN)
        for enemy in enemies:
            if enemy.is_alive():
                enemy.draw(SCREEN)

        for b in buttons:
            b.draw(SCREEN)

        for ft in effects[:]:
            ft.update()
            ft.draw(SCREEN)
            if not ft.alive():
                effects.remove(ft)

        pygame.display.flip()
        CLOCK.tick(60)

    return hero.is_alive()


# ---------------------------------------------------------------------------
# Main game flow


def choose_hero() -> Hero | None:
    buttons = [
        Button((100, 200, 150, 60), "Воин"),
        Button((325, 200, 150, 60), "Маг"),
        Button((550, 200, 150, 60), "Разбойник"),
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].is_clicked(event.pos):
                    return Warrior((100, 250))
                if buttons[1].is_clicked(event.pos):
                    return Mage((100, 250))
                if buttons[2].is_clicked(event.pos):
                    return Rogue((100, 250))

        SCREEN.fill(GREY)
        title = BIG_FONT.render("Выберите класс героя", True, WHITE)
        SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, 120)))
        for btn in buttons:
            btn.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(60)


def main() -> None:
    global SCREEN, CLOCK, FONT, BIG_FONT

    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RPG v4")
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.Font(None, 24)
    BIG_FONT = pygame.font.Font(None, 32)

    hero = choose_hero()
    if hero is None:
        pygame.quit()
        return

    enemies_first = [
        Enemy("Слабый гоблин", hp=30, attack=10, defense=2, pos=(600, 260)),
        Enemy("Сильный орк", hp=50, attack=15, defense=3, pos=(680, 260)),
    ]

    if not run_battle(hero, enemies_first):
        pygame.quit()
        return

    if random.random() < 0.5:
        hero.attack += 2
        present_message("Вы получили предмет: +2 к атаке")
    else:
        hero.defense += 2
        present_message("Вы получили предмет: +2 к защите")

    random_event(hero)
    camp(hero)
    open_shop(hero)
    upgrade(hero)

    boss = [Enemy("Дракон", hp=150, attack=28, defense=10, pos=(600, 260))]
    run_battle(hero, boss)

    present_message("Конец игры")
    pygame.quit()


if __name__ == "__main__":
    main()

