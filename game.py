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


def run_battle(hero: Hero, enemies: list[Enemy]) -> bool:
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
    else:
        log.append("Поражение… Герой пал в бою.")

    print("\nЖурнал боя:")
    for entry in log:
        print(entry)

    return hero.is_alive()


def main() -> None:
    hero = Hero("Герой", hp=100, attack=20, defense=5)

    enemies_first = [
        Enemy("Слабый гоблин", hp=30, attack=10, defense=2),
        Enemy("Сильный орк", hp=50, attack=15, defense=3),
    ]

    if not run_battle(hero, enemies_first):
        return

    # Лут после первого боя
    if random.random() < 0.5:
        hero.attack += 2
        print("Вы получили предмет: +2 к атаке.")
    else:
        hero.defense += 2
        print("Вы получили предмет: +2 к защите.")

    print("\nЛагерь. Ваши действия?")
    camp_choice = input("1) Отдохнуть (+30 HP) 2) Получить бафф (+3 к защите)\n")
    if camp_choice == "1":
        hero.heal(30)
        print(f"{hero.name} отдыхает и восстанавливает 30 HP.")
    else:
        hero.defense += 3
        print(f"{hero.name} получает бафф: +3 к защите.")

    upgrade_choice = input("Выберите повышение: 1) +5 HP 2) +2 к атаке\n")
    if upgrade_choice == "1":
        hero.max_hp += 5
        hero.hp += 5
        print("Максимальное HP увеличено на 5.")
    else:
        hero.attack += 2
        print("Атака увеличена на 2.")

    boss = [Enemy("Дракон", hp=120, attack=25, defense=8)]
    run_battle(hero, boss)


if __name__ == "__main__":
    main()

