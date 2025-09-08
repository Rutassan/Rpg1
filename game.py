import random


class Character:
    def __init__(self, name: str, hp: int, attack: int, defense: int):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)


class Hero(Character):
    def __init__(self, name: str, hp: int, attack: int, defense: int, gold: int):
        super().__init__(name, hp, attack, defense)
        self.gold = gold

    def normal_attack(self, target: "Character", log: list[str]) -> None:
        damage = max(1, self.attack - target.defense)
        target.take_damage(damage)
        log.append(f"{self.name} атакует {target.name} и наносит {damage} урона!")

    def strong_attack(self, target: "Character", log: list[str]) -> None:
        if random.random() < 0.7:  # 70% шанс попасть
            damage = max(1, self.attack * 2 - target.defense)
            target.take_damage(damage)
            log.append(
                f"{self.name} выполняет сильную атаку по {target.name} и наносит {damage} урона!"
            )
        else:
            log.append(f"Сильная атака {self.name} промахивается!")

    def heal_action(self, log: list[str]) -> None:
        amount = int(self.max_hp * 0.3)
        self.heal(amount)
        log.append(f"{self.name} использует Лечение и восстанавливает {amount} HP.")


class Enemy(Character):
    def attack_action(self, target: Character, log: list[str]) -> None:
        damage = max(1, self.attack - target.defense)
        target.take_damage(damage)
        log.append(f"{self.name} наносит {damage} урона {target.name}!")


def random_event(hero: Hero) -> None:
    event = random.choice(["wanderer", "chest", "dawn"])
    if event == "wanderer":
        print("Вы встретили таинственного путника…")
        choice = input("1) Обменять 5 HP на 10 золота 2) Отказаться\n")
        if choice == "1" and hero.hp > 5:
            hero.take_damage(5)
            hero.gold += 10
            print("Герой теряет 5 HP и получает 10 золота.")
        else:
            print("Вы проходите мимо путника.")
    elif event == "chest":
        print("Вы находите сундук…")
        if random.random() < 0.5:
            bonus = random.choice(["attack", "defense"])
            if bonus == "attack":
                hero.attack += 2
                print("Вы нашли редкий предмет: +2 к атаке.")
            else:
                hero.defense += 2
                print("Вы нашли редкий предмет: +2 к защите.")
        else:
            hero.take_damage(3)
            print("Сундук оказался пустым! Герой теряет 3 HP.")
    else:
        print("Наступает рассвет.")
        choice = input("1) +1 к атаке 2) +5 HP\n")
        if choice == "1":
            hero.attack += 1
            print("Атака увеличена на 1.")
        else:
            hero.heal(5)
            print("Герой восстанавливает 5 HP.")


def open_shop(hero: Hero) -> None:
    items = [
        {"name": "Стальной меч", "attack": 2, "cost": 10},
        {"name": "Щит стража", "defense": 2, "cost": 12},
        {"name": "Амулет жизни", "hp": 10, "cost": 15},
    ]
    offer = random.sample(items, 2)
    print("\nМагазин. Ваше золото:", hero.gold)
    for idx, item in enumerate(offer, 1):
        if "attack" in item:
            desc = f"+{item['attack']} к атаке"
        elif "defense" in item:
            desc = f"+{item['defense']} к защите"
        else:
            desc = f"+{item['hp']} HP"
        print(f"{idx}) {item['name']} ({desc}) - {item['cost']} золота")
    choice = input("Выберите предмет для покупки или 0 для выхода\n")
    if choice in {"1", "2"}:
        item = offer[int(choice) - 1]
        if hero.gold >= item["cost"]:
            hero.gold -= item["cost"]
            if "attack" in item:
                hero.attack += item["attack"]
                print(
                    f"Герой покупает предмет за {item['cost']} золота: +{item['attack']} к атаке."
                )
            elif "defense" in item:
                hero.defense += item["defense"]
                print(
                    f"Герой покупает предмет за {item['cost']} золота: +{item['defense']} к защите."
                )
            else:
                hero.max_hp += item["hp"]
                hero.hp += item["hp"]
                print(
                    f"Герой покупает предмет за {item['cost']} золота: +{item['hp']} HP."
                )
        else:
            print("Недостаточно золота.")


def run_battle(hero: Hero, enemies: list[Enemy], reward_gold: int = 0) -> bool:
    log: list[str] = []

    while hero.is_alive() and any(e.is_alive() for e in enemies):
        print(f"\n{hero.name} HP: {hero.hp}/{hero.max_hp}")
        for idx, enemy in enumerate(enemies):
            status = f"{enemy.hp}/{enemy.max_hp}" if enemy.is_alive() else "повержен"
            print(f"{idx + 1}. {enemy.name} HP: {status}")

        target = next(e for e in enemies if e.is_alive())

        action = input("Выберите действие: 1) атака 2) сильная атака 3) лечение\n")
        if action == "1":
            hero.normal_attack(target, log)
        elif action == "2":
            hero.strong_attack(target, log)
        elif action == "3":
            hero.heal_action(log)
        else:
            print("Неверный выбор, выполняется обычная атака.")
            hero.normal_attack(target, log)

        if not target.is_alive():
            log.append(f"{target.name} повержен!")

        for enemy in enemies:
            if enemy.is_alive():
                enemy.attack_action(hero, log)
                if not hero.is_alive():
                    log.append(f"{hero.name} пал в бою!")
                    break

    if hero.is_alive():
        log.append("Победа! Все враги повержены.")
        if reward_gold:
            hero.gold += reward_gold
            log.append(f"{hero.name} получает {reward_gold} золота.")
    else:
        log.append("Поражение… Герой пал в бою.")

    print("\nЖурнал боя:")
    for entry in log:
        print(entry)

    return hero.is_alive()


def main() -> None:
    hero = Hero("Герой", hp=100, attack=20, defense=5, gold=20)

    enemies_first = [
        Enemy("Слабый гоблин", hp=30, attack=10, defense=2),
        Enemy("Сильный орк", hp=50, attack=15, defense=3),
    ]

    if not run_battle(hero, enemies_first, reward_gold=15):
        return

    # Лут после первого боя
    if random.random() < 0.5:
        hero.attack += 2
        print("Вы получили предмет: +2 к атаке.")
    else:
        hero.defense += 2
        print("Вы получили предмет: +2 к защите.")

    random_event(hero)

    print("\nЛагерь. Ваши действия?")
    camp_choice = input("1) Отдохнуть (+30 HP) 2) Получить бафф (+3 к защите)\n")
    if camp_choice == "1":
        hero.heal(30)
        print(f"{hero.name} отдыхает и восстанавливает 30 HP.")
    else:
        hero.defense += 3
        print(f"{hero.name} получает бафф: +3 к защите.")

    open_shop(hero)

    upgrade_choice = input("Выберите повышение: 1) +5 HP 2) +2 к атаке\n")
    if upgrade_choice == "1":
        hero.max_hp += 5
        hero.hp += 5
        print("Максимальное HP увеличено на 5.")
    else:
        hero.attack += 2
        print("Атака увеличена на 2.")

    boss = [Enemy("Дракон", hp=150, attack=28, defense=10)]
    run_battle(hero, boss, reward_gold=50)


if __name__ == "__main__":
    main()

