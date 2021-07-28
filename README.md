The 'CompareBot' project. 

[![Version](https://img.shields.io/badge/version-1.0-green.svg)](https://github.com/Leucist/compare_bot)
[![Version](https://img.shields.io/github/commits-since/Leucist/compare_bot/v1.0)](https://github.com/Leucist/compare_bot)

The idea is to compare photos in couples, using the Elo rating and making up the top this way.

> Author: leucist.

Some extra's needed: 

- "config.py" with the <"TOKEN=" + your bot token from Bot Father> line

- photos to compare in the same-called folder called in the format "n.jpg", where n is an int, which lies in the interval (0, amount of photos). Also the 'amount' variable (11th line) must be changed in order to be equal to the amount of the photos for comparing.

- "models.json" should be edited in order to suit the models photos and contain their info for correct work of the script. All keys and values for change are marked by the '*'.

> The "models.json" database scheme:

```
 {
  "*model-number(equal to the number of photo in its name: '/photos/"n.jpg"')":{
   "name":"*model-name",
   "surname":"*model-surname",
   "rating":1400
  }
 }
```
