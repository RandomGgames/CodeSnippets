## load 
# adds the objective
scoreboard objectives add Id dummy


## tick
# runs the id function as all players without an id
execute as @a[tag=!Id] run function namespace:id


## id
# gives the player a unique id
execute store result score @s Id run scoreboard players add $max Id 1
tag @s add Id

## summon
# sets @s's id to $current's id 
scoreboard players operation $current Id = @s Id
# summons a marker then runs a function as it
execute summon marker run function namespace:compare


## compare
# sets the marker's id to a random player's id
scoreboard players operation @s Id = @a[limit=1,sort=random] Id
# checks if the marker's id matches the player's id who ran the summon function
execute if predicate namespace:predicate run say Our scores match! 