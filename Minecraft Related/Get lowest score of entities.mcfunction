## <load_reload>
scoreboard objectives add <objective> dummy

## <find_lowest_score>
execute as @e[sort=random,tag=<entity_filter>] run scoreboard players operation $minimum_score <objective> = @s <objective>
scoreboard players operation $minimum_score <objective> < @e[tag=<entity_filter>] <objective>
execute as @e[tag=<entity_filter>] if score @s <objective> = $minimum_score <objective> run say I have the lowest score!