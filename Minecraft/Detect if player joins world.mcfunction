##Load
scoreboard objectives add join minecraft.custom:minecraft.leave_game

##Tick
execute as @a unless score @s join = @s join run scoreboard players set @s join -1
execute as @a[scores={join=-1}] run function minecraft:join
execute as @a[scores={join=1..}] run function minecraft:join

##Join
scoreboard players set @s join 0
#Do whatever you want to the player. Some examples:
tp @s ~ ~ ~
clear @s
team join lobby