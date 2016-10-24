################################################################
# Messenger Application Client.py
# Written By: Steve Smith, Andy Firkus
# Date: 4/21/2016
# Description: Messenger Application. Using the correct protocol,
#   send messages to a server to be stored.
#
################################################################

from socket import *
from tkinter import *
import threading
import socket

global username
username = "" #Username of whoever is logged in
chattingWith = "" #Username of user being chatted with
serverName = "localhost" #Change it if you are running server elsewhere
serverPort = 12009

#Destroys a window
def destroyWindow(window):
    #connect to client
    window.destroy()
    
#Window with inputs for username and password
def login_window(master):
    #creates window for attempting to log in
    top = Toplevel(master)
    top.title("login")
    top.protocol("WM_DELETE_WINDOW", lambda: destroyWindow(top))
    top.grab_set()
    Label(top, text="username").grid(row=0)
    userEntry = Entry(top)
    userEntry.grid(row=0, column=1)
    userEntry.focus_set()
    Label(top, text="password").grid(row=1)
    pwEntry = Entry(top)
    pwEntry.grid(row=1, column=1)
    go = Button(top, text="Connect", command=lambda:
                client_login(userEntry.get(), pwEntry.get(), top))
    go.grid(row=2, column=1)

#Sends a message to the server to log a user in
def client_login(cusername, password, window):
    global username
    global chattingWith
    if(username != ""):
        client_logout()
    response = sendToServer('LOGIN' + '\t' + cusername + '\t' + password + '\r\n')
    response = response.split('\t')[1].strip()
    if(response == 'Fail'):
        response = 'Invalid information. Please try again'
    else:
        username = cusername
        chattingWith = ""
    writeToScreen(response)
    window.destroy()

#Window with inputs related to registering.
def register_window(master):
    #creates window for registering, calls client_register function
    top = Toplevel(master)
    top.title("login")
    top.protocol("WM_DELETE_WINDOW", lambda: destroyWindow(top))
    top.grab_set()
    Label(top, text="full name").grid(row=0)
    nameEntry = Entry(top)
    nameEntry.grid(row=0, column=1)
    nameEntry.focus_set()
    Label(top, text="username").grid(row=1)
    userEntry = Entry(top)
    userEntry.grid(row=1, column=1)
    userEntry.focus_set()
    Label(top, text="email").grid(row=2)
    emailEntry = Entry(top)
    emailEntry.grid(row=2, column=1)
    emailEntry.focus_set()
    Label(top, text="password").grid(row=3)
    pwEntry = Entry(top)
    pwEntry.grid(row=3, column=1)
    
    go = Button(top, text="Register", command=lambda:
                client_register(userEntry.get(), emailEntry.get(), pwEntry.get(), nameEntry.get(), top))
    go.grid(row=4, column=1)

#Sends a message to the server to register a user.
def client_register(cusername, email, password, fullName, window):
    response = sendToServer('REGISTER' + '\t' + cusername + '\t' + password + '\t' + fullName + '\t' + email + '\r\n')
    response = response.split('\t')[1].strip()
    writeToScreen(response)
    window.destroy()

#Places text into the textbox on root window.
def placeText(text):
    global username
    writeToScreen(text, username)

#Places text into the textbox on root window.
def writeToScreen(text, username=""):
    """Places text to main text body in format "username: text"."""
    global main_body_text
    global chattingWith
    main_body_text.config(state=NORMAL)
    main_body_text.insert(END, '\n')
    if username:
        main_body_text.insert(END, username + ": ")
        if(chattingWith != ""):
            response = sendToServer("SEND_MESSAGE" + "\t" + chattingWith + "\t" + username + "\t" + username + ": " + text)
    main_body_text.insert(END, text)
    main_body_text.yview(END)
    main_body_text.config(state=DISABLED)
def processUserText(event):
    data = text_input.get()
    placeText(data)
    text_input.delete(0, END)
def contacts_window(master): #contacts_window from research
    global username
    if(username != ""):
        cWindow = Toplevel(master)
        cWindow.title("Contacts")
        cWindow.grab_set()
        scrollbar = Scrollbar(cWindow, orient=VERTICAL)
        listbox = Listbox(cWindow, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        buttons = Frame(cWindow)
        cBut = Button(buttons, text="Connect",
                      command=lambda: contacts_connect(
                                          listbox.get(ACTIVE).split(":"), cWindow))
        cBut.pack(side=LEFT)
        aBut = Button(buttons, text="Add",
                      command=lambda: contacts_add_window(listbox, cWindow))
        aBut.pack(side=LEFT)
        buttons.pack(side=BOTTOM)

        friends = sendToServer("GET_FRIENDS" + "\t" + username).split('\t')
        friendIndex = 0
        friendStr = ""
        for i in friends:
            print(i)
            if(i != "GET_FRIENDS_RESULTS"):
                if(friendIndex % 2 == 1):
                    friendStr += ': ' + i
                    listbox.insert(END, friendStr)
                else:
                    friendStr = i
                friendIndex += 1
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
    else:
            writeToScreen("You need to log in before viewing your contacts")

#Window that has an input for the username of a friend one wishes to add.
def contacts_add_window(listbox, master): #contacts_add from research
    aWindow = Toplevel(master)
    aWindow.title("Contact add")
    Label(aWindow, text="Username:").grid(row=0)
    name = Entry(aWindow)
    name.focus_set()
    name.grid(row=0, column=1)

    go = Button(aWindow, text="Add", command=lambda:
                contacts_add_function(name.get(), aWindow, listbox))
    go.grid(row=3, column=1)

#Sets chattingWith variable to the username of a friend.
def contacts_connect(selectedUser, window):
    global username
    global chattingWith
    chattingWith = selectedUser[0]
    window.destroy()

#Send a message to the server to add a friend to the contacts list
def contacts_add_function(friendName, window, listbox):
    global username
    response = sendToServer('ADD_FRIEND' + '\t' + username + '\t' + friendName + '\r\n')
    response = response.split('\t')[1].strip()
    if(response == "Success"):
        listbox.delete(0, END)
        friends = sendToServer("GET_FRIENDS" + "\t" + username).split('\t')
        friendIndex = 0
        friendStr = ""
        for i in friends:
            if(i != "GET_FRIENDS_RESULTS"):
                if(friendIndex % 2 == 1):
                    friendStr += ': ' + i
                    listbox.insert(END, friendStr)
                else:
                    friendStr = i
                friendIndex += 1
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
    writeToScreen(response)
    window.destroy()

#Properly logs a user out (gets called by logging out through the menu
# or through click on the red x button to close a window
def client_logout():
    global username
    if(username != ""):
        sendToServer("LOGOFF" + "\t" + username)

#Confirmation message for logging out.
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        client_logout()
        root.destroy()

#This function connects and sends information to the server. Returns what is sent back from server.
def sendToServer(message):
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))
        clientSocket.send(message.encode())
        response = clientSocket.recv(1024).decode('ascii')
        clientSocket.close()     
    except:
        writeToScreen("There was an error communicating with the server.")
        response = "Error"
    return response

#Updates the chat log (Intended to be used in a loop that updates it ever 1 second).
def updateChatLog(root, textbox):
    global username
    global chattingWith
    if(chattingWith != ""):
        textbox.config(state=NORMAL)
        textbox.delete(1.0, END)
        textbox.config(state=DISABLED)
        chatLog = sendToServer("REQUEST_CHATLOG" + "\t" + username + "\t" + chattingWith).split("\t")
        logStatus = chatLog[1] # = "Fail" if no messages found, otherwise = "Success"
        del chatLog[:4]
        if(logStatus == "Success"):
            for i in chatLog:
                writeToScreen(i)
    #update chatlog every 1 second
    root.after(1000, lambda: updateChatLog(root, textbox))

    #Set up root window
    root = Tk()
    root.title("Chat")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    #Set up menu bar
    menubar = Menu(root)
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(label="login", command=lambda: login_window(root))
    file_menu.add_command(label="register", command=lambda: register_window(root))
    file_menu.add_command(label="logout", command=lambda: on_closing())
    menubar.add_cascade(label="File", menu=file_menu)
    menubar.add_command(label="Contacts", command=lambda:
                        contacts_window(root))
    root.config(menu=menubar)

    #Set up frame and main_body frame its components
    main_body = Frame(root, height=20, width=50)
    main_body_text = Text(main_body)
    body_text_scroll = Scrollbar(main_body)
    main_body_text.focus_set()
    body_text_scroll.pack(side=RIGHT, fill=Y)
    main_body_text.pack(side=LEFT, fill=Y)
    body_text_scroll.config(command=main_body_text.yview)
    main_body_text.config(yscrollcommand=body_text_scroll.set )
    main_body.pack()
    main_body_text.insert(END, "Welcome to the chat program!")
    main_body_text.config(state=DISABLED)
    text_input = Entry(root, width=60)
    text_input.bind("<Return>", processUserText)
    text_input.pack()

    #Create a socket and connect with server
    from socket import *
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))
        clientSocket.send("HELLO".encode())
        response = clientSocket.recv(1024).decode('ascii')
        writeToScreen(response)
        clientSocket.close()  
    except:
        writeToScreen("There was an error connecting to the server.")


#------------------------------------------------------------#
    root.after(1000, updateChatLog(root, main_body_text)) #Initializes the loop for updating the chat log
    root.mainloop()
