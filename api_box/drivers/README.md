# Files..

1. **PikaClasses**

This is where the pika code resides. It will be cleaned and consolidated in the future. 
The rpc_subscriber file uses the RunSubscriber class from this module. 

----

1. **rpc_subscriber**

This is a subscriber driver for the Classes module which uses the RunSubscriber class. This is the server that is up and listening for api triggers on the api box. Right now its set to listen on the 'api_info' queue.

----

1. **send_to_db**

like rpc_subscriber, this is a driver for the Classes module which uses the RpcPublisher class. It sends data to the database. 

----

1. **credentials**

Just credentials, must put in client id and secret in the required field

----

1. **api_accessor_methods**

This is a driver file for the API box. It can store all the api calls in getter functions. Its an extension of the subscriber class, which calls this file to run any command comming to the api box. 

Current its holding 3 functions. 
- fetch token
    this sends the users auth code to the API box to generate the token
    the token is then sent back to front end.

- get_token_from_db
    this takes in a sessionId and grabs a token from the database to perform API actions

- get_saved_tracks
    first actual test function, this takes in the sessionId, grabs that users token from db, then fetches the users saved tracks and sends back to front end.