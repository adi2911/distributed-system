# Distributed-system
This Distributed System is make using Exclusion lock mechanism along with multi-threading and proto

# Project Specification Part-1
1. A Simple Lock Server
2. A Client library

=> Read method details from the readme_description from the assigment. 

=> Assign a point from below to yourself. Explain in this readme about the code you are going to do in the next section below -> commit the explanation -> start coding.

=> First both init needs to be created and tested to check the working of our server.

=> After checking init we can start working seperately by putting name infront of the task we are doing in any order.

=> Create a new branch for all new work or a same branch (do not merge to main directly). Let's discuss the code, explain and merge by the end of the day, everyday.

=> Not able to understand something, need help or wanna switch task, call/message on the group.

=> Many of the following method,  needs some design discussions or thinking, whatever you think is write note it down (Eg: Data structure used, method used,) We need to add this to the design report later.

=> Do not think of efficiency in the starting. This is part 1 keep it as simple as possible.

=> Feel free to add anything in the below points, a sub point or extension or explanation as you like, please commit readme first before working. Ping in the group once something change. 

=> Use the utils file to store any method that is not the original method of the assignment specification. 

=> Run following command before generating proto using the command given in assignement:
pip install grpcio grpcio-tools

=> The command given in assignment have to run on root directory.

=> Update proto files as required for the commnuication between server and client. That is you can add or update any field in proto
please make sure to run proto command each time that is done.

   ## Client Library
   Client library main file is : Client/client.py
   1. Create functional structure of client.py - Aditi
   2. Create the proto files, using the command given - Aditi
   3. Create init method.
   4. Create Acqruire lock method - Nandita
   5. Create Release lock method - Nandita
   6. Create Append file method
       a. It should filter the file client is modifying
       b. Perform append operation on it.
   7. Create a prompt that takes input from client with the file name that needs to be updated.
   8. Create close method.
  
   ## Lock Server
   Server's main file is: Server/server.py. 
   For server implementation refer to the spinlock implementation given in assigment readme and assignment folder.
   1. Create the proto files, using the command given - Aditi
   2. Add 100 files to Server folder.
   3. Create functional structure of server.py - Aditi
   4. Create the init method
   5. Create structure for multithreaded environment
   6. Create the lock_acquire method - Nandita
   7.  Create the lock_release method - Nandita
   8. Create the append_file method.
   9. Create close method

# Design Pointers
Mention every method you write what it does what it handles, which all files the code is included.
https://www.velotio.com/engineering-blog/grpc-implementation-using-python
