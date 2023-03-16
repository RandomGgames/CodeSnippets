## load
scoreboard objectives add left minecraft.custom:minecraft.leave_game

## tick
execute as @a[tag=!joined] run function namespace:first_join
tag @a[scores={left=1..}] remove return
execute as @a[tag=!return,tag=joined,scores={joined=1..}] run function namespace:return

## first_join 
tag @s add joined
tellraw @s ["",{"text":"Welcome "},{"selector":"@s","color":"yellow"},{"text":"!"}]

## return
tag @s add return
tellraw @s ["",{"text":"Welcome back "},{"selector":"@s","color":"yellow"},{"text":"!"}]
scoreboard players reset @s left