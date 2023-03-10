scoreboard players set @e[tag=objective] objective 0
#Set a marker with the tag objective's score based on how close a player is
execute as @e[tag=objective] at @s if entity @a[distance=..40] run scoreboard players set @s objective 1
execute as @e[tag=objective] at @s if entity @a[distance=..30] run scoreboard players set @s objective 2
execute as @e[tag=objective] at @s if entity @a[distance=..25] run scoreboard players set @s objective 3
execute as @e[tag=objective] at @s if entity @a[distance=..20] run scoreboard players set @s objective 4
execute as @e[tag=objective] at @s if entity @a[distance=..15] run scoreboard players set @s objective 5
execute as @e[tag=objective] at @s if entity @a[distance=..10] run scoreboard players set @s objective 6
execute as @e[tag=objective] at @s if entity @a[distance=..5] run scoreboard players set @s objective 7

#Set the entitiy with the lowest scores to -1 and teleport the player to a random one
scoreboard players set minimum objective 99999
scoreboard players operation minimum objective < @e[tag=objective] objective
execute as @e[tag=objective] if score @s objective = minimum objective run scoreboard players set @s objective -1
tp @s @e[tag=objective,limit=1,sort=random,scores={objective=-1}]