## <load_reload>
scoreboard objectives add <objective> minecraft.custom:minecraft.leave_game

## <every_tick>
execute as @a unless score @s <objective> = @s <objective> run scoreboard players set @s <objective> -1
execute as @a[scores={<objective>=-1}] at @s run function <namespace>:<first_join_function>
execute as @a[scores={<objective>=1..}] at @s run function <namespace>:<return_join_function>

## <first_join_function> 
scoreboard players set @s <objective> 0
tellraw @s ["",{"text":"Welcome "},{"selector":"@s","color":"yellow"},{"text":"!"}]

## <return_join_function>
scoreboard players set @s <objective> 0
tellraw @s ["",{"text":"Welcome back "},{"selector":"@s","color":"yellow"},{"text":"!"}]