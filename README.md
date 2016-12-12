# HackableFlask
A flask app vulnerable to sql injection. Used as part of the CS in the classroom demo.

## Notes

I've hacked this app together as part of a workshop for kids in a classroom. It doesn't abide by good practices in any meaningful way. A few things that are particularly hacky are:

 - sessions: The sessions are literally just a dictionary that contains the session key as a random string and the username.
