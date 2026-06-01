# dodge-the-ball

TO ADD:

-Add a play button which will include all the game mode button inside of it for cleaner main menu
-Shield bash — while shield powerup is active, touching a ball destroys it instead of blocking death. Makes shield feel more active
-Magnet powerup — briefly pulls the target square toward your cursor, making it easier to collect. Short duration, high reward
-Milestone achievements — "First Blood", "Survivor" (score 50), "Untouchable" (use no powerups), shown on game over screen and stored in JSON. No external library needed(add more achivements as well)
-Daily high score — separate leaderboard tab that only tracks today's best per mode, resets at midnight. Uses the date as a key in scores.json
-Screensaver/attract mode — after 8s idle on menu, an AI-controlled dot plays the game autonomously in the background. Looks impressive, costs very little
-Transition animations — fade to black between screens instead of instant cuts. Single Surface alpha overlay, ~20 frames
-Keybinding display — small legend in the corner during gameplay showing ESC=pause, P=pause, Q=quit
-Add a high contrast mode