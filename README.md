##Stravaboards

A natural extension of Strava’s gameful approach to exercise tracking. A intra-segment leaderboard, with objective athlete ratings derived from all efforts on each personally attempted segment.

###Motivation

The recent gamification of difficult endeavors to serve as motivation to progress ones' skills has changed the way society looks at challenges. Strava provides a pace based exercise tracking service that allows users to compare their efforts to other users who have tried the same segment thereby instilling a gameful mindset in their user who naturally want to be at the top of the leaderboards.

However, currently, Strava does not provide it's users with a way to compare themselves across segments. To motivate why this is a difficult question to answer consider how you would objectively compare two athletes who aren't participating in the same workouts?

###Overview

After collecting all historical effort data from Strava's API for a set of 109 segments to the north of San Fransisco (see figure below), chosen for their likelihood of not being commuter routes and loading it all into a Mongo database the data was exported to JSON and moved to an AWS instance. On the remote machine it was possible to analyze the data with pandas on Amazon's powerful hardware.

![Segment Locations]('data_collection/segment_plot.png')

One of cruxes of this problem was intelligently removing outlying efforts, not because they belonged to abnormally fast or slow athletes, but because the GPS data was incorrectly analyzed by Strava for the effort was incorrectly analyzed and there for rendered useless.
