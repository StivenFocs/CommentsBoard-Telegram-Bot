import os
import sys

from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import *
from random import randrange

import sqlite3
from sqlite3 import Error

from ast import literal_eval
import json

################

bot = Client("commentsBoardBot_session",,"")
bot.start()

database = sqlite3.connect("commentsBoardDatabase.db")
cursor = database.cursor()

########

creating_post = {}
editing_post = {}
answering = {}

bot_admins = ["289336202"]

################

version = "1.3.5"

home = "Welcome or Welcome back <a href='tg://user?id={user_id}'>{name}</a>!\nWith this bot you can create, edit, and share, little comment boards.\nEveryone can leave a comment to your board, you too! and it's absolutely free.\n\nFor first, use one of the buttons below to interact with the bot.\n\nCreated with LOV by <a href='tg://user?id=289336202'>StivenFocs</a>\nv{version}"

home_kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ New board", callback_data="post_new"),InlineKeyboardButton("💾 My posts",callback_data="post_mine")],[InlineKeyboardButton("❤️ Donate",url="https://buymeacoffee.com/stivenfocs"),InlineKeyboardButton("📂 Source code", url="https://github.com/StivenFocs/CommentsBoard-Telegram-Bot")]])

new_post1 = "Send the title/caption for your new board..\n\n/cancel"

messages = {}
messages["no_boards"] = "No boards from you"
messages["board_created"] = "<b>Board created!</b>\n\nYou can now use the below menu to edit, share, or delete this board.\n\n{board_title}\nID: <code>{board_id}</code>\n\nBy clearing the board, you will delete all user's comments.\n\nBy clicking the share notification button you will toggle this option that, when enabled, you will receive a notification when someone (except you) share this board."
messages["board_panel"] = "{board_title}\n\nID: <code>{board_id}</code>\nShared {board_messages_amount} times\nWith {board_comments_amount} comments\n\nBy clearing the board, you will delete all user's comments.\n\nBy clicking the share notification button you will toggle this option that, when enabled, you will receive a notification when someone (except you) share this board."
messages["boards_list"] = "This list contains your owned boards. Choose one to open it's edit panel."
messages["board_deleted"] = "This board was deleted permanently."
messages["board_without_comments"] = "{board_title}\n\nNo comments yet."
messages["board_with_comments"] = "{board_title}\n\n{board_comments}"
messages["board_closed_comments"] = "{board_title}\n\n{board_comments}\nThe board is closed"

def get_message(name):
    return messages[name]

################

def default_tables():
    try:
        cursor.execute('CREATE TABLE "users" ("chat_id" TEXT);')
        print("Tabella 'users' generata")
    except Exception as ex:
        none = None
    
    try:
        cursor.execute('CREATE TABLE "posts" ("id" INTEGER, "title" TEXT, "comments" TEXT, "messages" TEXT, "owner" TEXT, "share_notifications" TEXT, "open" TEXT);')
        print("Tabella 'posts' generata")
    except Exception as ex:
        none = None

def parse_entry(entry):
    array = entry
    new_array = []
    for value in array:
        for value_ in value:
            new_array.append(str(value_))
    text_entry = new_array

    entry = {}
    entry["id"] = text_entry[0]
    entry["title"] = text_entry[1]
    entry["comments"] = text_entry[2]
    entry["messages"] = text_entry[3]
    entry["owner"] = text_entry[4]
    entry["share_notifications"] = text_entry[5]
    entry["open"] = text_entry[6]
    return entry

def parse_group_entry(entry):
    new_array = []
    for value in entry:
        new_array_ = []
        for value_ in value:
            new_array_.append(str(value_))
        entry = {}
        entry["id"] = new_array_[0]
        entry["title"] = new_array_[1]
        entry["comments"] = new_array_[2]
        entry["messages"] = new_array_[3]
        entry["owner"] = new_array_[4]
        entry["share_notifications"] = new_array_[5]
        entry["open"] = new_array_[6]
        
        new_array.append(entry)
    return new_array

def board_comments(board):
    text = ""

    comments = board["comments"]
    comments = literal_eval(comments)
    if len(comments) > 0:
        for comment in comments:
            name = comment["name"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")
            comment_text = comment["text"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")
            comment_text = comment_text.replace("\n"," ")

            text = text + "<a href='tg://user?id=" + comment["id"] + "'>" + name + "</a>: " + comment_text + "\n"
    return text

def board_text(board_data):
    comments = board_data["comments"]
    comments = literal_eval(comments)

    if str(board_data["open"]) == "true":
        if len(comments) > 0:
            return placeholder(messages["board_with_comments"], None, board_data)
        else:
            return placeholder(messages["board_without_comments"], None, board_data)
    else:
        return placeholder(messages["board_closed_comments"], None, board_data)

def placeholder(text, handler, board_data):
    global version

    replaces = []
    replaces.append({"from": "{version}", "to": str(version)})

    if handler is not None:
        if isinstance(handler, Message) or isinstance(handler, CallbackQuery):
            name = handler.from_user.first_name
            if handler.from_user.last_name is not None:
                name = name + " " + handler.from_user.last_name
            replaces.append({"from": "{name}", "to": str(name)})
            
            replaces.append({"from": "{user_id}", "to": str(handler.from_user.id)})
            if isinstance(handler, Message):
                replaces.append({"from": "{chat_id}", "to": str(handler.chat.id)})
            if isinstance(handler, CallbackQuery):
                replaces.append({"from": "{chat_id}", "to": str(handler.message.chat.id)})
    
    if board_data is not None:
        decoded_title = board_data["title"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")

        replaces.append({"from": "{board_id}", "to": str(board_data["id"])})
        replaces.append({"from": "{board_title}", "to": str(decoded_title)})
        replaces.append({"from": "{board_comments}", "to": str(board_comments(board_data))})
        replaces.append({"from": "{board_comments_amount}", "to": str(len(literal_eval(board_data["comments"])))})
        replaces.append({"from": "{board_messages_amount}", "to": str(len(literal_eval(board_data["messages"])))})
    
    for replace in replaces:
        text = text.replace(str(replace["from"]), str(replace["to"]))

    return text

def create_board(new_board_data):
    title_encoded = new_board_data['title'].replace("'", "////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")

    try:
        cursor.execute("INSERT INTO posts('id','title','comments','messages','owner','share_notifications','open') VALUES ('" + str(new_board_data["id"]) + "','" + title_encoded + "','[]','[]','" + str(new_board_data["owner"]) + "','false','true');")
        database.commit()

        print("Board created (" + str(new_board_data["id"]) + ",'" + str(title_encoded) + "','" + str(new_board_data["owner"]) + "')")

        comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(new_board_data["id"]) + "';")]
        return parse_entry(comparedentry)
    except Exception as ex:
        print("An error occurred while trying to create a board")
        print(ex)

####################

def return_editBoardKb(board_id):
    return InlineKeyboardMarkup([InlineKeyboardButton("🔙 Back",callback_data="post_edit_" + str(board_id))])

def editBoardKb(board_id):
    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    board_data = parse_entry(comparedentry)

    toggle_btn = InlineKeyboardButton("🔓 Open the board",callback_data="post_edit_" + str(board_id) + "_toggle")
    if str(board_data["open"]).lower() == "true":
        toggle_btn = InlineKeyboardButton("🔐 Close the board",callback_data="post_edit_" + str(board_id) + "_toggle")

    share_notification_btn = InlineKeyboardButton("❌ Share notifications",callback_data="post_edit_" + str(board_id) + "_shareNotifications")
    if str(board_data["share_notifications"]).lower() == "true":
        share_notification_btn = InlineKeyboardButton("✔️ Share notifications",callback_data="post_edit_" + str(board_id) + "_shareNotifications")

    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh",callback_data="post_edit_" + str(board_id) + "_refresh"),InlineKeyboardButton("🖇 Share",switch_inline_query=str(board_id))],[toggle_btn],[InlineKeyboardButton("✏️ Edit title", callback_data="post_edit_" + str(board_id) + "_title"),InlineKeyboardButton("🧹 Clear board",callback_data="post_edit_" + str(board_id) + "_clearComments")],[share_notification_btn],[InlineKeyboardButton("🗑 Delete the board",callback_data="post_delete_" + str(board_id))],[InlineKeyboardButton("🔙 Back to boards list",callback_data="post_mine")]])

def sA(array):
    new_array = []
    for value in array:
        new_array.append(value[0])
    return new_array

async def send_edit_panel(message, board_id):
    user_id = str(message.from_user.id)
    if isinstance(message, Message):
        chat_id = str(message.chat.id)
    mid = ""
    if  isinstance(message, CallbackQuery):
        mid = message.message.message_id

    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    if len(comparedentry) > 0:
        board_data = parse_entry(comparedentry)
        if  isinstance(message, CallbackQuery):
            await bot.edit_message_text(user_id, mid, placeholder(messages["board_panel"], message, board_data),parse_mode="HTML",reply_markup=editBoardKb(str(board_id)), disable_web_page_preview=True)
        else:
            await bot.send_message(chat_id, placeholder(messages["board_panel"], message, board_data),parse_mode="HTML",reply_markup=editBoardKb(str(board_id)), disable_web_page_preview=True)
    else:
        if  isinstance(message, CallbackQuery):
            await query.answer("Board not found")
        else:
            await bot.send_message(chat_id,"Board not found", disable_web_page_preview=True)

async def refresh_board(board_id):
    board_id = str(board_id)

    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    if len(comparedentry) > 0:
        print("Refreshing the board: " + str(board_id))

        try:
            board_data = parse_entry(comparedentry)
            messages = literal_eval(board_data["messages"])

            for message in messages:
                if str(board_data["open"]) == "true":
                    await bot.edit_inline_text(str(message), board_text(board_data), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Leave a comment",url="https://t.me/CommentsBoardBot?start=" + str(board_data["id"]))]]), disable_web_page_preview=True)
                else:
                    await bot.edit_inline_text(str(message), board_text(board_data), disable_web_page_preview=True)
            
            print("Refreshed the board: " + str(board_id))
        except Exception as ex:
            print("An error occurred while trying to refresh the board '" + str(board_id) + "'")
            print(ex)
    else:
        print("An error occurred while trying to refresh the board:" + str(board_id))
        print("comparedentry with no results")

def add_chat(chat):
    try:
        user_in_table = [a for a in cursor.execute("SELECT chat_id FROM users WHERE chat_id='" + str(chat) + "';")]
        if len(user_in_table) <= 0:
            cursor.execute("INSERT INTO users('chat_id') VALUES ('" + str(chat) + "');")
            database.commit()
            print(str(chat) + " added to the 'users' table")
    except Exception as ex:
        print("An error occurred during the new-user check")
        print(ex)

###############################

@bot.on_message()
async def onMsg(client,message):
    global messages

    #print("onMessage event")
    #print(message)

    if message.via_bot is not None:
        return
    if message.edit_date is not None:
        return
    if message.message_id is None:
        return
    if message.chat.id is None:
        return
    if message.from_user is None:
        return
    if message.text is None:
        return
    if len(message.text) < 1:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_type = message.chat.type
    cmd = message.text.split(" ")

    default_tables()

    add_chat(chat_id)

    log_string = "NewMessage from " + str(user_id) + " | text: '" + str(message.text) + "' ="
    
    if chat_type == "private":
        if creating_post.get(user_id) is not None:
            log_string = log_string + " creating_post = "

            if message.text.lower() == "/cancel":
                del creating_post[user_id]
                await bot.send_message(chat_id, "Operation canceled")

                log_string = log_string + "Operation canceled"
                print(log_string)
                return

            if creating_post.get(user_id) is None:
                del creating_post[user_id]
                await bot.send_message(chat_id, "An error occurred\nOperation canceled")

                log_string = log_string + "incomplete post creating structure"
                print(log_string)
                return
            
            if creating_post[user_id]["step"] == 0:
                if len(message.text) <= 130:
                    print(creating_post[user_id])
                    board_id = creating_post[user_id]["id"]
                    title_text = message.text.replace("<", "&lt;")
                    title_text = title_text.replace(">", "&gt;")
                    title_text = title_text.replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")

                    creating_post[user_id]["title"] = title_text
                    creating_post[user_id]["owner"] = str(user_id)

                    board_data = create_board(creating_post[user_id])
                    del creating_post[user_id]

                    await bot.send_message(chat_id, placeholder(messages["board_created"], message, board_data),parse_mode="HTML",reply_markup=editBoardKb(str(board_id)), disable_web_page_preview=True)
                else:
                    await bot.send_message(chat_id, placeholder("90 Characters max", message, None), parse_mode="HTML")
            else:
                del creating_post[user_id]
                await bot.send_message(chat_id, "Unknow creating step\nOperation canceled")

                return
        elif editing_post.get(user_id) is not None:
            log_string = log_string + " editing_post = "

            if message.text.lower() == "/cancel":
                del editing_post[user_id]
                await bot.send_message(chat_id, "Operation canceled")

                log_string = log_string + "Operation canceled"
                print(log_string)
                return
            
            edit_data = editing_post[user_id]
            board_id = edit_data["id"]

            try:
                comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
                if len(comparedentry) > 0:
                    board_data = parse_entry(comparedentry)

                    if str(chat_id) == str(board_data["owner"]):
                        if edit_data["section"] == "title":
                            log_string = log_string + "board (" + str(board_id) + ") section: 'title' = "

                            if len(message.text) <= 130:
                                title_text = message.text.replace("<", "&lt;")
                                title_text = title_text.replace(">", "&gt;")
                                title_encoded = title_text.replace("'", "////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")
                                
                                if editing_post.get(user_id) is not None:
                                    del editing_post[user_id]
                                
                                try:
                                    cursor.execute("UPDATE posts SET title='" + str(title_encoded) + "' WHERE id='" + str(board_id) + "';")
                                    database.commit()
                                    await bot.send_message(chat_id, placeholder("Title edited successfully!", message, None), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back",callback_data="post_edit_" + str(board_id))]]))
                                    
                                    log_string = log_string + "board (" + str(board_id) + ") edited successfully"

                                    await refresh_board(board_id)
                                except Exception as ex:
                                    await bot.send_message(chat_id, placeholder("Couldn't edit the title.", message, None), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back",callback_data="post_edit_" + str(board_id))]]))
                                    print("An error occurred while trying to edit a board title")
                                    print(ex)

                                    exception_traceback = sys.exc_info()
                                    line_number = exception_traceback.tb_lineno
                                    print("on line " + str(line_number))

                                    log_string = log_string + "board (" + str(board_id) + ") Couldn't edit the title"
                            else:
                                await bot.send_message(chat_id, placeholder("130 Characters maximum limit exceeded", message, None), parse_mode="HTML")

                                log_string = log_string + "130 Characters maximum limit exceeded"
                        else:
                            del editing_post[user_id]
                            await bot.send_message(chat_id, "An error occurred while trying to perform this task\nError code: #UKSCTN\n\nOperation canceled.")

                            print("unknow editing section occurred")

                            log_string = log_string + "board (" + str(board_id) + ") unknow editing section"
                    else:
                        del editing_post[user_id]
                        await bot.send_message(chat_id, "You're not the board owner!\n\nOperation canceled.")
                        
                        print("A non-creator tried to edit an unowned board")

                        log_string = log_string + "board (" + str(board_id) + ") tried to edit an unowned board"
                else:
                    del editing_post[user_id]
                    await bot.send_message(chat_id, "This board does not exist!\n\nOperation canceled.")
                    
                    print("Unexisting board, title editing")

                    log_string = log_string + "board (" + str(board_id) + ") unexisting board"
            except Exception as ex:
                del editing_post[user_id]
                await bot.send_message(chat_id, "An error occurred while trying to perform this task\nError code: #UKERRO\n\nOperation canceled.")
                
                print("An error occurred while trying to perform a board edit task")
                print(ex)

                log_string = log_string + "couldn't finish the edit operation"
        elif answering.get(user_id) is not None:
            log_string = log_string + " answering = "

            if message.text.lower() == "/cancel":
                del answering[user_id]
                await bot.send_message(chat_id, "Operation canceled")

                log_string = log_string + "Operation canceled"
                print(log_string)
                return
            
            board_id = answering[user_id]

            try:
                comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
                if len(comparedentry) > 0:
                    board_data = parse_entry(comparedentry)

                    if str(board_data["open"]) == "true":
                        if len(message.text) <= 150:
                            comments = board_data["comments"]
                            comments = literal_eval(comments)

                            new_comment = {}

                            name = message.from_user.first_name
                            if message.from_user.last_name is not None:
                                name = name + " " + message.from_user.last_name
                            name = name.replace("<","&lt;")
                            name = name.replace(">","&gt;")
                            name = name.replace("'","////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")
                            
                            text = message.text.replace("<", "&lt;")
                            text = text.replace(">","&gt;")
                            text = text.replace("'","////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")

                            new_comment["name"] = name
                            new_comment["id"] = str(user_id)
                            new_comment["text"] = text
                            comments.append(new_comment)

                            if answering.get(user_id) is not None:
                                del answering[user_id]

                            try:
                                cursor.execute("UPDATE posts SET comments='" + json.dumps(comments) + "' WHERE id='" + board_id + "';")
                                database.commit()
                                await bot.send_message(chat_id, "Comment added to the board")

                                log_string = log_string + "board (" + str(board_id) + ") Comment added"

                                await refresh_board(board_id)
                            except Exception as ex:
                                await bot.send_message(chat_id, "Couldn't add your comment.")
                                print(ex)

                                log_string = log_string + "board (" + str(board_id) + ") couldn't add the comment"
                        else:
                            await bot.send_message(chat_id,"Comment too long, 150 maximum characters allowed.")

                            log_string = log_string + "board (" + str(board_id) + ") comment too long"
                    else:
                        await bot.send_message(chat_id,"This board is closed, you can't comment now.")
                        await refresh_board(board_id)

                        log_string = log_string + "board (" + str(board_id) + ") tried to comment to a closed board"
                else:
                    await bot.send_message(chat_id,"Error!\nUnrecognized board id.")

                    log_string = log_string + "board (" + str(board_id) + ") unexisting board"
            except Exception as ex:
                print("Couldn't add a user comment")
                print(ex)

                await bot.send_mesage(chat_id,"Couldn't add the comment")
                
                log_string = log_string + " Couldn't add the comment"
            
            if answering.get(user_id) is not None:
                del answering[user_id]
        else:
            log_string = log_string + " normal command = "

            if cmd[0].lower() == "/start":
                if len(cmd) > 1:
                    board_id = str(cmd[1])
                    board_id = board_id.replace("'","////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")

                    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
                    if len(comparedentry) > 0:
                        board_data = parse_entry(comparedentry)

                        if board_data["open"] == "true":
                            answering[user_id] = board_id
                            await message.reply("Ok! Send me your comment text\n\n/cancel")

                            log_string = log_string + "board (" + str(board_id) + ") Adding a new comment"
                        else:
                            await message.reply("This board is closed, you can't comment now.")

                            log_string = log_string + "board (" + str(board_id) + ") tried to comment to a closed board"
                    else:
                        await bot.send_message(chat_id,"Error!\nunrecognized board id.")

                        log_string = log_string + "board (" + str(board_id) + ") unexisting board"
                else:
                    await bot.send_message(chat_id, placeholder(home, message, None),parse_mode="HTML",reply_markup=home_kb, disable_web_page_preview=True)

                    log_string = log_string + "Sent the home"
            elif cmd[0].lower() == "/cancel":
                await bot.send_message(chat_id, "No operations to cancel.")

                log_string = log_string + "No operations to cancel"

    print(log_string)






@bot.on_callback_query()
async def callback(client,query):

    #print("onCallbackQuery event")
    #print(query)

    mid = query.message.message_id
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    default_tables()

    add_chat(chat_id)

    log_string = "CallbackQuery from " + str(user_id) + " | callback_data: '" + str(query.data) + "' = "

    data = query.data.split("_")
    if data[0] == "home":
        await query.answer()
        await bot.edit_message_text(chat_id, mid, placeholder(home, query, None), reply_markup=home_kb, disable_web_page_preview=True)
        
        log_string = log_string + "Returned to home"
    if data[0] == "post":
        if len(data) > 1:
            if data[1] == "new":
                await query.answer()
                creating_post[user_id] = {}
                new_post_id = 0

                while(True):
                    new_post_id = randrange(10000,99999)
                    comparedentry = [a for a in cursor.execute("SELECT 'id' FROM posts WHERE id='" + str(new_post_id) + "';")]
                    if len(comparedentry) <= 0:
                        break
                
                creating_post[user_id]["id"] = new_post_id
                creating_post[user_id]["step"] = 0
                await bot.edit_message_text(chat_id, mid, placeholder(new_post1, query, None))

                log_string = log_string + "Creating a new board"
            if data[1] == "mine":
                comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE owner='" + str(user_id) + "';")]
                if len(comparedentry) > 0:
                    await query.answer()
                    boards_list_keyboard = []
                    boards = parse_group_entry(comparedentry)
                    for board in boards:
                        boards_list_keyboard.append([InlineKeyboardButton(str(board["title"]).replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'"), callback_data="post_edit_" + str(board["id"]))])
                    boards_list_keyboard.append([InlineKeyboardButton("🔙 Back",callback_data="home")])
                    
                    await bot.edit_message_text(chat_id, mid, placeholder(get_message("boards_list"), query, None), reply_markup=InlineKeyboardMarkup(boards_list_keyboard), disable_web_page_preview=True)
                    
                    log_string = log_string + "Returned to boards list"
                else:
                    await query.answer(placeholder(get_message("no_boards"), query, None))
                    try:
                        await bot.edit_message_text(chat_id, mid, placeholder(home, query, None), reply_markup=home_kb, disable_web_page_preview=True)
                    except Exception as ex:
                        none = None

                    log_string = log_string + "Returned to home, no boards"
            if data[1] == "edit":
                if len(data) > 2:
                    board_id = str(data[2])

                    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
                    if len(comparedentry) > 0:
                        board_data = parse_entry(comparedentry)

                        if str(user_id) == str(board_data["owner"]):
                            if len(data) > 3:
                                if data[3] == "refresh":
                                    try:
                                        await send_edit_panel(query, board_id)
                                        await query.answer("Done")

                                        log_string = log_string + "board (" + str(board_id) + ") refresh (changed)"
                                    except Exception as ex:
                                        await query.answer("No changes")

                                        log_string = log_string + "board (" + str(board_id) + ") refresh (no changes)"
                                elif data[3] == "title":
                                    await query.answer()
                                    editing_post[user_id] = {}
                                    editing_post[user_id]["id"] = str(data[2])
                                    editing_post[user_id]["section"] = "title"
                                    await bot.edit_message_text(chat_id, mid, placeholder("Ok, send me the new title/caption for this board...\n\n/cancel", query, None))

                                    log_string = log_string + "board (" + str(board_id) + ") started edit title operation"
                                elif data[3] == "clearComments":
                                    if str(board_data["open"]) == "true":
                                        if len(literal_eval(board_data["comments"])) > 0:
                                            try:
                                                cursor.execute("UPDATE posts SET comments='[]' WHERE id='" + board_id + "';")
                                                database.commit()

                                                await query.answer("Board cleared successfully")
                                                await refresh_board(board_id)

                                                log_string = log_string + "board (" + str(board_id) + ") cleared"
                                            except Exception as ex:
                                                await query.answer("Couldn't clear the board")

                                                log_string = log_string + "board (" + str(board_id) + ") couldn't clear the board"
                                        else:
                                            await query.answer("The board is already empty")

                                            log_string = log_string + "board (" + str(board_id) + ") tried to clear the board when it's empty"
                                    else:
                                        await query.answer("You can't clear the board when it's closed")
                                    
                                        log_string = log_string + "board (" + str(board_id) + ") tried to clear the board when it's closed"
                                elif data[3] == "shareNotifications":

                                    initial_toggle = str(board_data["share_notifications"])
                                    final_toggle = ""

                                    try:
                                        if str(board_data["share_notifications"]) == "true":
                                            cursor.execute("UPDATE posts SET share_notifications='false' WHERE id='" + board_id +"';")
                                            database.commit()

                                            final_toggle = "false"
                                        else:
                                            cursor.execute("UPDATE posts SET share_notifications='true' WHERE id='" + board_id +"';")
                                            database.commit()

                                            final_toggle = "true"
                                        await query.answer("successfully toggled the share notifications option")
                                        try:
                                            await send_edit_panel(query, board_id)
                                        except Exception as ex:
                                            none = None
                                        
                                        log_string = log_string + "board (" + str(board_id) + ") share notification toggled (from '" + initial_toggle + "', to '" + str(final_toggle) + "')"
                                    except Exception as ex:
                                        await query.answer("Couldn't switch the share notifications option")

                                        print("Couldn't switch the shareNotifications option for the board: " + str(board_id))
                                        print(ex)

                                        log_string = log_string + "board (" + str(board_id) + ") couldn't share notification toggle"
                                elif data[3] == "toggle":
                                    comments = literal_eval(board_data["comments"])
                                    if len(comments) > 0:
                                        try:
                                            
                                            initial_toggle = str(board_data["open"])
                                            fianl_toggle = ""

                                            
                                            if str(board_data["open"]) == "true":
                                                cursor.execute("UPDATE posts SET open='false' WHERE id='" + board_id +"';")
                                                database.commit()

                                                final_toggle = "false"
                                            else:
                                                cursor.execute("UPDATE posts SET open='true' WHERE id='" + board_id +"';")
                                                database.commit()

                                                final_toggle = "true"
                                            await query.answer("successfully toggled the board")

                                            await refresh_board(board_id)

                                            try:
                                                await send_edit_panel(query, board_id)
                                            except Exception as ex:
                                                none = None

                                            log_string = log_string + "board (" + str(board_id) + ") toggled (from '" + initial_toggle + "', to '" + str(final_toggle) + "')"
                                        except Exception as ex:
                                            await query.answer("Couldn't toggle the board")

                                            print("Couldn't toggle the board: " + str(board_id))
                                            print(ex)

                                            log_string = log_string + "board (" + str(board_id) + ") unable to toggle"
                                    else:
                                        await query.answer("You can't close a board without comments")

                                        log_string = log_string + "board (" + str(board_id) + ") tried to close the board without comments"
                                else:
                                    await query.answer("Invalid edit section")

                                    log_string = log_string + "board (" + str(board_id) + ") invalid edit section"
                            else:
                                await query.answer()
                                await send_edit_panel(query, str(data[2]))

                                log_string = log_string + "board (" + str(board_id) + ") opened edit panel"
                        else:
                            await query.answer("Error!\nThis board is not yours.", show_alert=True)

                            log_string = log_string + "board (" + str(board_id) + ") un-owned board"
                    else:
                        await query.answer("Error! Unrecognized board id.", show_alert=True)

                        try:
                            await bot.edit_message_text(chat_id, mid, placeholder(home, query, None), reply_markup=home_kb, disable_web_page_preview=True)
                        except Exception as ex:
                            none = None

                        log_string = log_string + "board (" + str(board_id) + ") unexisting board"
                else:
                    await query.answer("Error!\nIncomplete query command.")
            if data[1] == "delete":
                if len(data) > 2:
                    board_id = str(data[2])

                    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + board_id + "';")]
                    if len(comparedentry) > 0:
                        try:
                            board_data = parse_entry(comparedentry)
                            try:
                                cursor.execute("DELETE FROM 'posts' WHERE id='" + str(data[2]) + "';")
                                database.commit()

                                await bot.edit_message_text(str(chat_id), mid, placeholder("Board deleted successfully", query, None), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to boards list",callback_data="post_mine")]]))
                                await query.answer()

                                log_string = log_string + "board (" + str(board_id) + ") board deleted successfully"

                                try:
                                    messages = literal_eval(board_data["messages"])
                                    for message in messages:
                                        await bot.edit_inline_text(message, get_message("board_deleted"), disable_web_page_preview=True)
                                except Exception as ex:
                                    print("An error occurred while trying to edit all board's messages")
                                    print(ex)
                                    exception_type, exception_object, exception_traceback = sys.exc_info()
                                    filename = exception_traceback.tb_frame.f_code.co_filename
                                    line_number = exception_traceback.tb_lineno

                                    print("Exception type: ", exception_type)
                                    print("File name: ", filename)
                                    print("Line number: ", line_number)
                            except Exception as ex:
                                print("An error occurred while trying to delete a board")
                                print(ex)
                                exception_type, exception_object, exception_traceback = sys.exc_info()
                                filename = exception_traceback.tb_frame.f_code.co_filename
                                line_number = exception_traceback.tb_lineno

                                print("Exception type: ", exception_type)
                                print("File name: ", filename)
                                print("Line number: ", line_number)

                                await query.answer("Couldn't delete the board")

                                log_string = log_string + "board (" + str(board_id) + ") couldn't delete"
                        except Exception as ex:
                            await query.answer("An error occurred")

                            log_string = log_string + "board (" + str(board_id) + ") couldn't delete"
                    else:
                        await query.answer("Unrecognized board id, this panel is expired.", show_alert=True)
                        await bot.delete_messages(chat_id, mid)

                        log_string = log_string + "board (" + str(board_id) + ") unexisting board"
                else:
                    log_string = log_string + "insufficient arguments"
                
    print(log_string)





@bot.on_inline_query()
async def inline(client,query):
    global messages

    #print("onInlineQuery event")
    #print(query)

    user_id = query.from_user.id

    default_tables()

    log_string = "InlineQuery from " + str(user_id) + " | query: '" + str(query.query) + "' = "

    if len(query.query) > 0:
        log_string = log_string + " empty query"

        board_id = str(query.query)
        board_id = board_id.replace("'","////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")

        comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
        if len(comparedentry) > 0:
            board_data = parse_entry(comparedentry)
            await bot.answer_inline_query(query.id, results=[InlineQueryResultArticle(str(board_data["title"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")),InputTextMessageContent(board_text(board_data), disable_web_page_preview=True),id=str(board_data["id"]),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Leave a comment",url="https://t.me/CommentsBoardBot?start=" + str(board_data["id"]))]]))],cache_time=1,is_personal=True)

            log_string = log_string + " board ('" + str(board_id) + "') answered"
        else:
            await bot.answer_inline_query(query.id, results=[InlineQueryResultArticle("No Results",InputTextMessageContent("No results", disable_web_page_preview=True))],cache_time=1,is_personal=True)

            log_string = log_string + " board ('" + str(board_id) + "') no results"
    else:
        comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE owner='" + str(user_id) + "';")]
        if len(comparedentry) > 0:
            boards = parse_group_entry(comparedentry)
            boards_results = []

            for board_data in boards:
                boards_results.append(InlineQueryResultArticle(str(board_data["title"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")),InputTextMessageContent(board_text(board_data), disable_web_page_preview=True),id=str(board_data["id"]),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Leave a comment",url="https://t.me/CommentsBoardBot?start=" + str(board_data["id"]))]])))
            await bot.answer_inline_query(query.id, results=boards_results,cache_time=1,is_personal=True)

            log_string = log_string + " answered with " + str(len(boards)) + " boards"
        else:
            await bot.answer_inline_query(query.id, results=[InlineQueryResultArticle("No Results",InputTextMessageContent("No results", disable_web_page_preview=True))],cache_time=1,is_personal=True)

            log_string = log_string + " no results"
    
    print(log_string)





@bot.on_chosen_inline_result()
async def inline_choice(client,result):
    global messages

    #print("on_chosen_inline_result event")
    #print(result)

    user_id = result.from_user.id
    board_id = result.result_id

    log_string = "InlineQueryChosen from " + str(user_id) + " | result_id: '" + str(result.result_id) + "' ="

    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    if len(comparedentry) > 0:
        log_string = log_string + " board existing ="

        board_data = parse_entry(comparedentry)
        messages = literal_eval(board_data["messages"])
        messages.append(result.inline_message_id)
        try:
            cursor.execute("UPDATE posts SET 'messages'='" + json.dumps(messages) + "' WHERE id='" + str(board_id) + "';")
            database.commit()

            log_string = log_string + " Board message saved,"

            try:
                if str(board_data["share_notifications"]) == "true":
                    if str(user_id) != str(board_data["owner"]):
                        name = result.from_user.first_name
                        if result.from_user.last_name is not None:
                            name = name + " " + result.from_user.last_name

                        await bot.send_message(board_data["owner"], placeholder("<a href='tg://user?id=" + str(user_id) + "'>" + str(name) + "</a> shared your board.\n\n{board_title}\nID: <code>{board_id}</code>", result, board_data), disable_web_page_preview=True)

                        log_string = log_string + " Share notification sent"
                    else:
                        log_string = log_string + " Shared by the owner"
                else:
                    log_string = log_string + " Share notification disabled"
            except Exception as ex:
                print("I was unable to send a share notification")
                print(ex)

                log_string = log_string + " Couldn't send a share notification"
        except Exception as ex:
            print("An error occurred while saving a new board's message")
            print(ex)
            print("board_id: " + str(board_id))
            print("new inline message id: " + str(result.inline_message_id))

            try:
                await bot.edit_inline_text(result.inline_message_id, "An error occurred while trying to link this inline message to his board.", disable_web_page_preview=True)
            except Exception as ex:
                none = None
            
            log_string = log_string + " Couldn't save a board message"

    print(log_string)

###############

idle()
# 679 righe di agonia! ma è stato un piacere!