## load
scoreboard objectives add <objective> minecraft.custom:minecraft.leave_game

## tick
execute as @a[tag=!<first_join_tag>] run function <namespace>:<first_join_function>
tag @a[scores={left=1..}] remove <return_join_tag>
execute as @a[tag=!<return_join_tag>,tag=<first_join_tag>,scores={<objective>=1..}] run function namespace:<return_function>

## <first_join_function> 
tag @s add <first_join_tag>
tellraw @s ["",{"text":"Welcome "},{"selector":"@s","color":"yellow"},{"text":"!"}]

## <return_function>
tag @s add <return_join_tag>
tellraw @s ["",{"text":"Welcome back "},{"selector":"@s","color":"yellow"},{"text":"!"}]
scoreboard players reset @s <objective>