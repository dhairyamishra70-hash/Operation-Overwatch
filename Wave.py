# This would be the Wave class with it's own attributes and methods


if len(enemies) == 0 and enemies_to_spawnn <= 0:

    wave += 1
    enemies_to_spawn = 5 + (wave * 2)

if enemies_to_spawn >0 and random.random() < 0.02:
    enemies.append(Enemy(wave))

    enemies_to_spawn -= 1