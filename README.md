# Rack-O Discord Bot
Rack-O bot is a way to play a simplified version of [Rack-O](https://en.wikipedia.org/wiki/Rack-O) against an AI within a Discord server.

![Example of Rack-O game](https://i.imgur.com/vDQLzYD.jpg)

<h2>Commands</h2>

| Command  | Description |
| ------------- | ------------- |
| $help  | Displays command information  |
| $play | Starts a new game of Rack-O |
|$purge|Deletes all bot messages from channel|
|$rules|Provides the rules for Rack-O|
<h2>Instructions</h2>
Once a game is started with the `$play` command, only the user who gave the command will be able to effect that instance of the game.

The player and the bot are each assigned a rack with ten slots that have been dealt cards from the Racko deck. 
There are 60 cards numbered 1-60. 
The objective is to fill your rack with cards in ascending order (Slot 0: Low, Slot 9: High). 
The first player to do so wins.
On each turn, the player whos turn it is may draw either from the top of this discard pile, or the top of the deck. 
The player must then choose which slot to place the drawn card. The card from the chosen slot is then placed in the discard pile.
