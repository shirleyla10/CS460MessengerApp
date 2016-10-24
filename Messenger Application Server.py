#####################################################################
# Messenger Application Server.py
# Written By: Lauren Shirley, Steve Smith
# Date: 4/21/2016
# Description: Receives messages from a client and either
#   registers, logs in,  adds friends, updates chatlog,
#   retrieves friend list and chatlog, and logs off users.
#   All requests/response must follow their respective
#   format listed below:
#
#   Registration request 
#        REGISTER \t USERID \t PASSWORD \t EMAIL \t FULL NAME
#   Registration response 
#        REGISTRATION_STATUS \t DETAILS ON STATUS
#   Login request
#       LOGIN \t USERID \t PASSWORD
#   Login response
#       LOGIN_STATUS \t STATUS
#   Add Friend request
#       ADD_FRIEND \t USERID \t FRIEND_ID    
#   Add Friend response
#       ADD_FRIEND_STATUS \t STATUS
#   Send Message request
#       SEND_MESSAGE \t FRIEND_ID \t USERID \t MESSAGE
#   Send Message response
#       SEND_MESSAGE_STATUS \t STATUS
#   Chatlog request
#       REQUEST_CHATLOG \t FRIEND_ID \t USERID
#   Chatlog response
#       CHATLOG_STATUS \t STATUS \t MESSAGES (or FRIEND_ID \t USERID)
#   Get Friends request
#       GET_FRIENDS \t USERID
#   Get Friends response
#       GET_FRIENDS_RESULTS \t FRIEND_LIST
#   Logoff request
#       LOGOFF \t USERID
#   Logoff response
#       LOGOFF_STATUS \t STATUS
#####################################################################

from socket import *
from datetime import datetime

#Create a welcome socket bound at serverPort
serverPort = 12009
serverSocket = socket(AF_INET,SOCK_STREAM)
#serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(('',serverPort))
serverSocket.listen(10)
print ('The Messenger Application server is ready to receive')
accessTime = datetime.now();
print("Access time is", accessTime);

while 1:
    connectionSocket, addr = serverSocket.accept()
    #Wait for the hello message
    while 1:
        request = connectionSocket.recv(1024).decode('ascii')
        print("Request message:", request)
        #if request message is blank then break out and close socket
        if(request == ""):
            break

        #save method name to check for type of request
        methodName = request.split('\t')[0].strip()
        #print received from information
        print("From", addr,methodName)

        #receive hello message and return 
        if(methodName.upper() == "HELLO"):
            Request = "Connection successful!"
            connectionSocket.send(Request.encode())
        
        #Registration Processing
        elif(methodName.upper() == "REGISTER"):
            #assign each part of message to a variable
            userID = request.split('\t')[1].strip()
            password = request.split('\t')[2].strip()
            userFullName = request.split('\t')[3].strip()
            email = request.split('\t')[4].strip()
            RegisterStatus = "Registration_Status \tSuccess\r\n"
            #check file for existing records
            for line in open("UserProfile.txt"):
                registeredID = line.split('\t')[0].strip()
                registeredEmail = line.split('\t')[2].strip()
                if(userID==registeredID): #if user name already exists
                    RegisterStatus = "Registration_Status \tUsername already exists. Please try again\r\n"
                elif(email==registeredEmail): #if email is registered under a different user name
                    RegisterStatus = "Registration_Status \tRegistration already exists with this email. Please try again\r\n"
            if(RegisterStatus != "Registration_Status \tSuccess\r\n"):#if user info match any in file send back error
                connectionSocket.send(RegisterStatus.encode())
            else: #if username does not exist and email not already used
                if(len(password) < 6): #make sure password is at least 6 characters
                    passwordError = "Registration_Status \tPassword must be at least 6 characters. Please try again\r\n"
                    connectionSocket.send(passwordError.encode()) #return error
                else: #else registration successful, save record and report back to user
                    #create record to save
                    NewUserRecord = userID + '\t' + password + '\t' + email + '\t' + userFullName + '\t' + str(addr) + '\n'
                    #append it to the file
                    register_file = open("UserProfile.txt", "a")
                    register_file.write(NewUserRecord)
                    register_file.close()
                    #make entry in status file
                    status_file = open("UserStatus.txt", "a")
                    status_file.write(userID + '\t' + 'OFFLINE' + '\n')
                    status_file.close()
                    connectionSocket.send(RegisterStatus.encode())#return registrationstatus
                    
        #Login Processing        
        elif(methodName.upper() == "LOGIN"):
            #Assign each part of message to a variable
            userID =  request.split('\t')[1].strip()
            password = request.split('\t')[2].strip()
            LoginStatus = "Login_Status \tFail\r\n"
            #check file for correct user information
            for line in open("UserProfile.txt"):
                registeredID = line.split('\t')[0].strip()
                registeredPassword = line.split('\t')[1].strip()
                if(userID == registeredID and password == registeredPassword):
                    LoginStatus = "Login_Status \tSuccess\r\n"
                
            #Change status to online
            status_file = open("UserStatus.txt", "r")
            lines = status_file.readlines()
            status_file.close()
            
            status_file = open("UserStatus.txt", "w")
            for line in lines:
                if(line.split('\t')[0].strip() != userID):
                    status_file.write(line.rstrip('\n') + '\n')
            status_file.write(userID + '\t' + 'ONLINE' + '\n')
            status_file.close()
            connectionSocket.send(LoginStatus.encode()) #return loginStatus
            
        #Add Friend Processing    
        elif(methodName.upper() == "ADD_FRIEND"):
            #Assign each part of message to a variable
            userName = request.split('\t')[1].strip()
            friendName = request.split('\t')[2].strip()
            friendExists = False
            alreadyFriend = False
            message = ""
            #check file for friends username
            for line in open("UserProfile.txt"):
                tempUser = line.split('\t')[0].strip()
                if(tempUser == friendName):
                    friendExists = True #friend exists
            #check file to see if user is already a friend
            for line in open("UserFriends.txt"):
                tempUser = line.split('\t')[0].strip()
                if(tempUser == userName):
                    friend = line.split('\t')[1].strip()
                    if(friend == friendName):
                            alreadyFriend = True #user is already friends with this person
                            message = "User is already a friend!"
            if(friendExists == True):
                if(alreadyFriend == False):
                    #add friend
                    #append it to the file
                    friends_file = open("UserFriends.txt", "a")
                    friends_file.write(userName + '\t' + friendName + '\n')
                    friends_file.close()
                    message = "Success"
            else:
                message = "User does not exist!"
            #send back add friend status
            message = "Add_Friend_Status" + "\t" + message + "\r\n"
            connectionSocket.send(message.encode())
            
        #Send Message Processing    
        elif(methodName.upper() == "SEND_MESSAGE"):
            #Assign each part of message to a variable
            friendID = request.split('\t')[1].strip()
            userID = request.split('\t')[2].strip()
            message = request.split('\t')[3].strip()
            messageStatus = "Fail" #initialize as fail 
            messageFile = open("UserChatlog.txt", "r")
            #assign lines in file to a variable
            lines = messageFile.readlines()
            messageFile.close()
            #open file to write
            messageFile = open("UserChatlog.txt", "w")
            for line in lines:
                line = line.rstrip('\n')
                userID1 = line.split('\t')[0].strip()
                userID2 = line.split('\t')[1].strip()
                #if user ids match conversation then add message to current line and change status
                if((userID1.upper() == userID.upper() and userID2.upper() == friendID.upper())
                   or (userID1.upper() == friendID.upper() and userID2.upper() == userID.upper())):
                   messageFile.write(line + '\t' + message + '\n')
                   messageStatus = "Success" 
            messageFile.close()
            #if status is still at fail it means a conversation hasn't been started so append to end of file
            if(messageStatus != "Success"):
                messageFile = open("UserChatlog.txt", "a")
                messageFile.write(userID + '\t' + friendID + '\t' + message + '\n')
                messageFile.close()
                messageStatus = "Success"
            #send back Message status
            messageStatus = "Send_Message_Status \t" + messageStatus +'\r\n'
            connectionSocket.send(messageStatus.encode())
            
        #Request Chatlog Processing        
        elif(methodName.upper() == "REQUEST_CHATLOG"):
            friendID = request.split('\t')[1].strip()
            userID = request.split('\t')[2].strip()
            chatlog_status = "Fail" #initialize as fail
            for line in open("UserChatlog.txt", "r"):
                line = line.rstrip('\n')
                userID1 = line.split('\t')[0].strip()
                userID2 = line.split('\t')[1].strip()
                #if user ids match conversation then save message to send
                if((userID1.upper() == userID.upper() and userID2.upper() == friendID.upper())
                   or (userID1.upper() == friendID.upper() and userID2.upper() == userID.upper())):
                    message = line
                    chatlog_status = "Success" #if found then change to success
            #return status and ids and message if found
            if(chatlog_status == "Success"):
                chatlogStatus = "Chatlog_Status \t" + chatlog_status + "\t" + line
            else:
                chatlogStatus = "Chatlog_Status \t" + chatlog_status + "\t" + friendID + "\t" + userID + "\t" + "" + "\r\n"
            connectionSocket.send(chatlogStatus.encode())
            
        #Get Friends Processing    
        elif(methodName.upper() == "GET_FRIENDS"):
            #assign user's ID to variable to help locate friend list
            userID = request.split('\t')[1].strip()
            friends = ""
            #search each line for user ID match and save friends if match found
            for line in open("UserFriends.txt"):
                line = line.rstrip('\n')
                tempID = line.split('\t')[0].strip()
                friendID = line.split('\t')[1].strip()
                if(userID == tempID):
                    for line in open("UserStatus.txt"):
                        tempFID = line.split('\t')[0].strip()
                        tempFStatus = line.split('\t')[1].strip()
                        if(friendID == tempFID):
                            friends += friendID + "\t" + tempFStatus + "\t"
            #send back results
            message = 'GET_FRIENDS_RESULTS' + '\t' + friends +"\r\n"
            connectionSocket.send(message.encode())

        #Logoff Processing    
        elif(methodName.upper() == "LOGOFF"):
            #Assign each part of message to a variable
            userID = request.split('\t')[1].strip()
            
            #Change status to offline
            status_file = open("UserStatus.txt", "r")
            lines = status_file.readlines()
            status_file.close()
            
            status_file = open("UserStatus.txt", "w")
            for line in lines:
                if(line.split('\t')[0].strip() != userID):
                    status_file.write(line.rstrip('\n') + '\n')
            status_file.write(userID + '\t' + 'OFFLINE' + '\n')
            status_file.close()
            
            LogoffStatus = "Logoff_Status \tSuccess\r\n"
            connectionSocket.send(LogoffStatus.encode())
    #close connectionSocket            
    connectionSocket.close()

