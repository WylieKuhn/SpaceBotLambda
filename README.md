# SpaceBotLambda
A discord bot being built to deploy space facts to your discord server on demand!    

## Current Features
- Get ISS flyover date & time with telescope coordinates using GPS coordinates!
- Get a list of people in space and what craft they are on!  
- See current near-earth objects!
  
## Upcoming Features  
- See upcoming spacecraft launches!  
  
## Things To Know
- I am not storing any private user data. The gps coordinates passed in the `/issflyover` command are used by the bot to get the data and nothing else. I am not storing this data in a database anywhere.  
- I don't store or keep any user data from discord interactions past what is required to make the lambda work properly. I do not store them in a database. They get passed to the lambda, the lambda uses them, the lambda then shuts off and waits for the next time it recieves data.  
