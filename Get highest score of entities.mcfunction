## <load_reload>
scoreboard objectives add <objective> dummy

## <find_highest_score>
execute as @e[sort=random,tag=<entity_filter>] run scoreboard players operation $maximum_score <objective> = @s <objective>
scoreboard players operation $maximum_score <objective> > @e[tag=<entity_filter>] <objective>
execute as @e[tag=<entity_filter>] if score @s <objective> = $maximum_score <objective> run say I have the highest score!