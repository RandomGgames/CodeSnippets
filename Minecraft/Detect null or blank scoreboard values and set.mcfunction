#<player>: The player selector. @a for example.
#<objective>: The scoreboard objective. objective1 for example.
#<value>: The value to set for the player. 0 for example.
execute unless score <player> <objective> = <player> <objective> run scoreboard players set <player> <objective> <value>