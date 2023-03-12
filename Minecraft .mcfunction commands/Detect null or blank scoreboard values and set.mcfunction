#{PLAYER}: The player selector. @a for example.
#{OBJECTIVE}: The scoreboard objective. objective1 for example.
#{VALUE}: The value to set for the player. 0 for example.
execute unless score {PLAYER} {OBJECTIVE} = {PLAYER} {OBJECTIVE} run scoreboard players set {PLAYER} {OBJECTIVE} {VALUE}