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
    def normal_attack(self, target: 'Character', log: list[str]) -> None:
        damage = max(1, self.attack - target.defense)
        target.take_damage(damage)
        log.append(f"{self.name} attacks {target.name} for {damage} damage.")

    def strong_attack(self, target: 'Character', log: list[str]) -> None:
        if random.random() < 0.7:  # 70% chance to hit
            damage = max(1, self.attack * 2 - target.defense)
            target.take_damage(damage)
            log.append(
                f"{self.name} performs a strong attack on {target.name} for {damage} damage."
            )
        else:
            log.append(f"{self.name}'s strong attack missed!")

    def heal_action(self, log: list[str]) -> None:
        amount = int(self.max_hp * 0.3)
        self.heal(amount)
        log.append(f"{self.name} heals for {amount} HP.")


class Enemy(Character):
    def attack_action(self, target: Character, log: list[str]) -> None:
        damage = max(1, self.attack - target.defense)
        target.take_damage(damage)
        log.append(f"{self.name} attacks {target.name} for {damage} damage.")


def battle() -> None:
    hero = Hero("Warrior", hp=100, attack=20, defense=5)
    enemies = [
        Enemy("Weak Goblin", hp=30, attack=10, defense=2),
        Enemy("Strong Orc", hp=50, attack=15, defense=3),
    ]

    log: list[str] = []

    while hero.is_alive() and any(e.is_alive() for e in enemies):
        # Hero turn
        print(f"\n{hero.name} HP: {hero.hp}/{hero.max_hp}")
        for idx, enemy in enumerate(enemies):
            status = f"{enemy.hp}/{enemy.max_hp}" if enemy.is_alive() else "defeated"
            print(f"{idx + 1}. {enemy.name} HP: {status}")

        target = next(e for e in enemies if e.is_alive())

        action = input("Choose action: 1) attack 2) strong attack 3) heal\n")
        if action == "1":
            hero.normal_attack(target, log)
        elif action == "2":
            hero.strong_attack(target, log)
        elif action == "3":
            hero.heal_action(log)
        else:
            print("Invalid choice, performing normal attack.")
            hero.normal_attack(target, log)

        if not target.is_alive():
            log.append(f"{target.name} is defeated!")

        # Enemies' turn
        for enemy in enemies:
            if enemy.is_alive():
                enemy.attack_action(hero, log)
                if not hero.is_alive():
                    log.append(f"{hero.name} has fallen!")
                    break

    if hero.is_alive():
        log.append("Victory! All enemies are defeated.")
    else:
        log.append("Defeat! The hero has perished.")

    print("\nBattle log:")
    for entry in log:
        print(entry)


if __name__ == "__main__":
    battle()
