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

import termcolor
os.system("color")
from time import gmtime, strftime

################

bot = Client("commentsBoardBot_session",0,"")
bot.start()

database = sqlite3.connect("commentsBoardDatabase.db")
cursor = database.cursor()

########

creating_post = {}
editing_post = {}
answering = {}

bot_admins = ["289336202"]

################

version = "1.4.6"

home = "Welcome or Welcome back <a href='tg://user?id={user_id}'>{name}</a>!\nWith this bot you can create, edit, and share, little comment boards.\nEveryone can ✒️ Leave a comment to your board, you too! and it's absolutely free.\n\nFor first, use one of the buttons below to interact with the bot.\n\nDeveloped with LOV by <a href='tg://user?id=289336202'>StivenFocs</a>\nv{version}\nUpdate news: now 200+ board title and comments!!"
home_kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ New board", callback_data="post_new"),InlineKeyboardButton("💾 My boards",callback_data="post_mine")],[InlineKeyboardButton("❤️ Donate",url="https://buymeacoffee.com/stivenfocs"),InlineKeyboardButton("📂 Source code", url="https://github.com/StivenFocs/CommentsBoard-Telegram-Bot")],[InlineKeyboardButton("ℹ️ Terms of Use",url="https://telegra.ph/CommentsBoardBot---Terms-of-use-01-05"),InlineKeyboardButton("📣 Channel",url="https://t.me/CommentsBoardChannel")]])

admin_home = "Hey Hey! what's my favorite developer?? MHHHhh??\n\nHere some stats:\nTotal boards: {total_boards}\nTotal users: {total_users}"
admin_home_kb = InlineKeyboardMarkup([[InlineKeyboardButton("Get user data",callback_data="admin_user")]])

new_post_step1 = "Send the title/caption for your new board..\n\n/cancel"

messages_no_commands = "You can't use commands during a text operation\n\nYou are actually commenting the board: <code>{board_id}</code>\n{board_title}\n\n/cancel"
messages_no_boards = "No boards from you"
messages_board_created = "<b>Board created!</b>\n\nYou can now use the below menu to edit, share, or delete this board.\n\n{board_title}\nID: <code>{board_id}</code>\n\nBy clearing the board, you will delete all user's comments.\n\nBy clicking the share notification button you will toggle this option that, when enabled, you will receive a notification when someone (except you) shares this board.\n\nBy clicking the privacy mode button, you will toggle the profile link that is applied to comments user's names.\n\nNote that the delete button doesn't have a confirmation step."
messages_board_panel = "{board_title}\n\nID: <code>{board_id}</code>\nShared {board_messages_amount} times\nWith {board_comments_amount} comments\n\nBy clearing the board, you will delete all user's comments.\n\nBy clicking the share notification button you will toggle this option that, when enabled, you will receive a notification when someone (except you) shares this board.\n\nBy clicking the privacy mode button, you will toggle the profile link that is applied to comments user's names.\n\nNote that the delete button doesn't have a confirmation step."
messages_boards_list = "This list contains your owned boards. Choose one to open it's edit panel."
messages_board_deleted = "This board was deleted permanently."
messages_board_without_comments = "{board_title}\n\nNo comments yet."
messages_board_with_comments = "{board_title}\n\n{board_comments}"
messages_board_closed_comments = "{board_title}\n\n{board_comments}\nThe board is closed"

################

def now_time():
    return strftime("%D - %T | ")

def default_tables():
    try:
        cursor.execute('CREATE TABLE "users" ("chat_id" TEXT);')
        print("Created table 'users'")
    except Exception as ex:
        none = None
    
    try:
        cursor.execute('CREATE TABLE "posts" ("id" INTEGER, "title" TEXT, "comments" TEXT, "messages" TEXT, "owner" TEXT, "share_notifications" TEXT, "open" TEXT, "privacy_mode" TEXT);')
        print("Created table 'posts'")
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
    entry["privacy_mode"] = text_entry[7]

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
        entry["privacy_mode"] = new_array_[7]
        
        new_array.append(entry)
    return new_array

def board_comments(board_data):
    text = ""

    comments = board_data["comments"]
    comments = literal_eval(comments)
    if len(comments) > 0:
        for comment in comments:
            name = comment["name"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")
            comment_text = comment["text"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")
            comment_text = comment_text.replace("\n"," ")

            if str(board_data["privacy_mode"]).lower() == "true":
                text = text + name + ": " + comment_text + "\n"
            else:
                text = text + "<a href='tg://user?id=" + comment["id"] + "'>" + name + "</a>: " + comment_text + "\n"
    
    return text

def board_text(board_data):
    comments = board_data["comments"]
    comments = literal_eval(comments)

    if str(board_data["open"]) == "true":
        if len(comments) > 0:
            return placeholder(messages_board_with_comments, None, board_data)
        else:
            return placeholder(messages_board_without_comments, None, board_data)
    else:
        return placeholder(messages_board_closed_comments, None, board_data)

def placeholder(text, handler, board_data):
    replaces = []

    replaces.append({"from": "{version}", "to": str(version)})

    total_boards = len([a for a in cursor.execute("SELECT '_rowid_' FROM posts")])
    total_users = len([a for a in cursor.execute("SELECT '_rowid_' FROM users")])
    replaces.append({"from": "{total_boards}", "to": str(total_boards)})
    replaces.append({"from": "{total_users}", "to": str(total_users)})

    if handler is not None:
        if isinstance(handler, Message) or isinstance(handler, CallbackQuery):
            name = handler.from_user.first_name
            if handler.from_user.last_name is not None:
                name = name + " " + handler.from_user.last_name
            name = name.replace("<","&lt;")
            name = name.replace(">","&gt;")
            replaces.append({"from": "{name}", "to": str(name)})
            
            replaces.append({"from": "{user_id}", "to": str(handler.from_user.id)})
            if isinstance(handler, Message):
                replaces.append({"from": "{chat_id}", "to": str(handler.chat.id)})
            if isinstance(handler, CallbackQuery):
                replaces.append({"from": "{chat_id}", "to": str(handler.message.chat.id)})
    
    if board_data is not None:
        board_id = str(board_data["id"])
        decoded_title = board_data["title"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")

        replaces.append({"from": "{board_id}", "to": str(board_data["id"])})
        replaces.append({"from": "{board_title}", "to": str(decoded_title)})
        replaces.append({"from": "{board_comments}", "to": str(board_comments(board_data))})

        board_comments_number = '0'
        board_messages_number = '0'
        try:
            board_comments_number = str(len(literal_eval(board_data["comments"])))
        except Exception as ex:
            cursor.execute("UPDATE posts SET comments='[]' WHERE id='" + str(board_id) + "';")
            database.commit()

            print("Comments reset for the board: " + str(board_id))
        try:
            board_messages_number = str(len(literal_eval(board_data["messages"])))
        except Exception as ex:
            cursor.execute("UPDATE posts SET messages='[]' WHERE id='" + str(board_id) + "';")
            database.commit()

            print("Messages reset for the board: " + str(board_id))
        replaces.append({"from": "{board_comments_amount}", "to": board_comments_number})
        replaces.append({"from": "{board_messages_amount}", "to": board_messages_number})
    
    for replace in replaces:
        text = text.replace(str(replace["from"]), str(replace["to"]))

    return text

def create_board(new_board_data):
    title_encoded = new_board_data['title'].replace("'", "////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")

    try:
        cursor.execute("INSERT INTO posts('id','title','comments','messages','owner','share_notifications','open','privacy_mode') VALUES ('" + str(new_board_data["id"]) + "','" + title_encoded + "','[]','[]','" + str(new_board_data["owner"]) + "','false','true','false');")
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

    privacy_mode_btn = InlineKeyboardButton("❌ Privacy Mode",callback_data="post_edit_" + str(board_id) + "_privacyMode")
    if str(board_data["privacy_mode"]).lower() == "true":
        privacy_mode_btn = InlineKeyboardButton("✔️ Privacy Mode",callback_data="post_edit_" + str(board_id) + "_privacyMode")

    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh",callback_data="post_edit_" + str(board_id) + "_refresh"),InlineKeyboardButton("🖇 Share",switch_inline_query=str(board_id))],[toggle_btn],[InlineKeyboardButton("✏️ Edit title", callback_data="post_edit_" + str(board_id) + "_title"),InlineKeyboardButton("📃 Comments",callback_data="post_edit_" + str(board_id) + "_comments")],[share_notification_btn],[privacy_mode_btn],[InlineKeyboardButton("🗑 Delete the board",callback_data="post_delete_" + str(board_id))],[InlineKeyboardButton("🔙 Back to boards list",callback_data="post_mine")]])

def editCommentsKb(board_id):
    clear_comments_btn = InlineKeyboardButton("🧹 Clear board comments",callback_data="post_edit_" + str(board_id) + "_clearComments")

    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    board_data = parse_entry(comparedentry)

    text = ""
    
    comments = board_data["comments"]
    comments = literal_eval(comments)

    rows = []
    comments_buttons = []
    if len(comments) > 0:
        count = 0
        for comment in comments:
            comments_buttons.append(InlineKeyboardButton(str(count), callback_data="post_edit_" + str(board_id) + "_comments_" + str(count)))
            
            if len(comments_buttons) >= 5:
                rows.append(comments_buttons)
                comments_buttons = []

            count = count + 1

            if len(comments) <= count:
                rows.append(comments_buttons)
                comments_buttons = []
                break
    
    rows.append([clear_comments_btn])
    rows.append([InlineKeyboardButton("🔙 Back",callback_data="post_edit_" + str(board_id))])
    return InlineKeyboardMarkup(rows)


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
            await bot.edit_message_text(user_id, mid, placeholder(messages_board_panel, message, board_data),parse_mode="HTML",reply_markup=editBoardKb(str(board_id)), disable_web_page_preview=True)
        else:
            await bot.send_message(chat_id, placeholder(messages_board_panel, message, board_data),parse_mode="HTML",reply_markup=editBoardKb(str(board_id)), disable_web_page_preview=True)
    else:
        if  isinstance(message, CallbackQuery):
            await query.answer("Error! Unrecognized board id.")
        else:
            await bot.send_message(chat_id,"Error!\nUnrecognized board id.", disable_web_page_preview=True)

async def send_comments_panel(message, board_id):
    user_id = str(message.from_user.id)
    if isinstance(message, Message):
        chat_id = str(message.chat.id)
    mid = ""
    if  isinstance(message, CallbackQuery):
        mid = message.message.message_id

    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    if len(comparedentry) > 0:
        board_data = parse_entry(comparedentry)

        text = "NOTE: this feature is still in beta\n\nHere the complete list of your board's comments\nClick to a comment id to delete it.\n\n"

        comments = board_data["comments"]
        comments = literal_eval(comments)
        if len(comments) > 0:
            count = 0

            for comment in comments:
                name = comment["name"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")
                comment_text = comment["text"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")
                comment_text = comment_text.replace("\n"," ")

                text = text + str(count) + ". <a href='tg://user?id=" + comment["id"] + "'>" + name + "</a>: " + comment_text + "\n"
                count = count + 1

        if  isinstance(message, CallbackQuery):
            await bot.edit_message_text(user_id, mid, placeholder(text, message, board_data),parse_mode="HTML",reply_markup=editCommentsKb(str(board_id)), disable_web_page_preview=True)
        else:
            await bot.send_message(chat_id, placeholder(text, message, board_data),parse_mode="HTML",reply_markup=editCommentsKb(str(board_id)), disable_web_page_preview=True)
    else:
        if  isinstance(message, CallbackQuery):
            await query.answer("Error! Unrecognized board id.")
        else:
            await bot.send_message(chat_id,"Error!\nUnrecognized board id.", disable_web_page_preview=True)

async def refresh_board(board_id):
    board_id = str(board_id)

    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    if len(comparedentry) > 0:
        #print("Refreshing the board: " + str(board_id))

        try:
            board_data = parse_entry(comparedentry)
            messages = literal_eval(board_data["messages"])

            for message in messages:
                try:
                    if str(board_data["open"]) == "true":
                        await bot.edit_inline_text(str(message), board_text(board_data), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✒️ Leave a comment",url="https://t.me/CommentsBoardBot?start=" + str(board_data["id"]))]]), disable_web_page_preview=True)
                    else:
                        await bot.edit_inline_text(str(message), board_text(board_data), disable_web_page_preview=True)
                except Exception as ex:
                    none = None
            
            #print("Refreshed the board: " + str(board_id))
        except Exception as ex:
            print("An error occurred while trying to refresh the board '" + str(board_id) + "'")
            print(ex)
    else:
        print("An error occurred while trying to refresh the board:" + str(board_id))
        print("comparedentry with no results")

def add_chat(chat_id):
    try:
        user_in_table = [a for a in cursor.execute("SELECT chat_id FROM users WHERE chat_id='" + str(chat_id) + "';")]
        if len(user_in_table) <= 0:
            cursor.execute("INSERT INTO users('chat_id') VALUES ('" + str(chat_id) + "');")
            database.commit()
            print(str(chat_id) + " added to the 'users' table")
    except Exception as ex:
        print("An error occurred during the new-user check")
        print(ex)

###############################

@bot.on_message()
async def onMsg(client,message):
    global messages

    #print("onMessage event")
    #print(message)

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

    log_string = now_time() + termcolor.colored("NewMessage", "cyan") + " from " + termcolor.colored(str(user_id), "green") + " in " + termcolor.colored(str(chat_id), "yellow")  + " | text: '" + termcolor.colored(str(message.text), "magenta") + "' ="
    if chat_type == "private":
        if creating_post.get(user_id) is not None:
            log_string = log_string + " " + termcolor.colored("creating_board", "green") + " = "

            if message.via_bot is not None:
                await bot.send_message(chat_id, "You are actually in a text operation, the bot is waiting a text from you.\n\n/cancel")
                return

            if message.text.lower() == "/cancel":
                del creating_post[user_id]
                await bot.send_message(chat_id, "Operation cancelled")

                log_string = log_string + termcolor.colored("Operation &ecancelled", "yellow")
                print(log_string)
                return

            if creating_post.get(user_id) is None:
                del creating_post[user_id]
                await bot.send_message(chat_id, "An error occurred\nOperation cancelled")

                log_string = log_string + termcolor.colored("incomplete post creating structure", "yellow")
                print(log_string)
                return
            
            if creating_post[user_id]["step"] == 0:
                if len(message.text) <= 250:
                    board_id = creating_post[user_id]["id"]
                    title_text = message.text.replace("<", "&lt;")
                    title_text = title_text.replace(">", "&gt;")
                    title_text = title_text.replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")

                    creating_post[user_id]["title"] = title_text
                    creating_post[user_id]["owner"] = str(user_id)

                    board_data = create_board(creating_post[user_id])
                    del creating_post[user_id]
                    
                    log_string = log_string + termcolor.colored("created successfully", "green")

                    await bot.send_message(chat_id, placeholder(messages_board_created, message, board_data),parse_mode="HTML",reply_markup=editBoardKb(str(board_id)), disable_web_page_preview=True)
                else:
                    await bot.send_message(chat_id, placeholder("250 Characters maximum limit exceeded", message, None), parse_mode="HTML")

                    log_string = log_string + termcolor.colored("250 Characters maximum limit exceeded", "yellow")
            else:
                del creating_post[user_id]
                await bot.send_message(chat_id, "Unknown creating step\nOperation cancelled")

                log_string = log_string + termcolor.colored("Unknown creating step", "red")
                print(log_string)
                return
        elif editing_post.get(user_id) is not None:
            log_string = log_string + " " + termcolor.colored("editing_post", "yellow") + " = "

            if message.via_bot is not None:
                await bot.send_message(chat_id, "You are actually in a text operation, the bot is waiting a text from you.\n\n/cancel")
                return

            if message.text.lower() == "/cancel":
                del editing_post[user_id]
                await bot.send_message(chat_id, "Operation cancelled")

                log_string = log_string + termcolor.colored("Operation cancelled", "yellow")
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

                            if len(message.text) <= 250:
                                title_text = message.text.replace("<", "&lt;")
                                title_text = title_text.replace(">", "&gt;")
                                title_encoded = title_text.replace("'", "////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")
                                
                                if editing_post.get(user_id) is not None:
                                    del editing_post[user_id]
                                
                                try:
                                    cursor.execute("UPDATE posts SET title='" + str(title_encoded) + "' WHERE id='" + str(board_id) + "';")
                                    database.commit()
                                    await bot.send_message(chat_id, placeholder("Title edited successfully!", message, None), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back",callback_data="post_edit_" + str(board_id))]]))
                                    
                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("edited successfully", "green")

                                    await refresh_board(board_id)
                                except Exception as ex:
                                    await bot.send_message(chat_id, placeholder("Couldn't edit the title.", message, None), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back",callback_data="post_edit_" + str(board_id))]]))
                                    print("An error occurred while trying to edit a board title")
                                    print(ex)

                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("Couldn't edit the title", "red")
                            else:
                                await bot.send_message(chat_id, placeholder("250 Characters maximum limit exceeded", message, None), parse_mode="HTML")

                                log_string = log_string + termcolor.colored("250 Characters maximum limit exceeded", "yellow")
                        else:
                            del editing_post[user_id]
                            await bot.send_message(chat_id, "An error occurred while trying to perform this task\nError code: #UKSCTN\n\nOperation cancelled.")

                            print("unknow editing section occurred")

                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("unknow editing section", "red")
                    else:
                        del editing_post[user_id]
                        await bot.send_message(chat_id, "You're not the board owner!\n\nOperation cancelled.")
                        
                        print("A non-creator tried to edit an unowned board")

                        log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to edit an un-owned board", "red")
                else:
                    del editing_post[user_id]
                    await bot.send_message(chat_id, "This board does not exist!\n\nOperation cancelled.")
                    
                    print("Unexisting board, title editing")

                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("unexisting board", "cyan")
            except Exception as ex:
                del editing_post[user_id]
                await bot.send_message(chat_id, "An error occurred while trying to perform this task\nError code: #UKERRO\n\nOperation cancelled.")
                
                print("An error occurred while trying to perform a board edit task")
                print(ex)

                log_string = log_string + termcolor.colored("couldn't finish the edit operation", "red")
        elif answering.get(user_id) is not None:
            log_string = log_string + " " + termcolor.colored("answering", "cyan") + " = "

            if message.via_bot is not None:
                await bot.send_message(chat_id, "You are actually in a text operation, the bot is waiting a text from you.\n\n/cancel")
                return
            
            try:
                board_id = answering[user_id]

                comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
                if len(comparedentry) > 0:
                    board_data = parse_entry(comparedentry)

                    if message.text.lower() == "/cancel":
                        del answering[user_id]
                        await bot.send_message(chat_id, "Operation cancelled")

                        log_string = log_string + termcolor.colored("Operation cancelled", "yellow")
                        print(log_string)
                        return

                    if message.text.lower().startswith("/start"):
                        await bot.send_message(chat_id, placeholder(messages_no_commands, message, board_data))

                        log_string = log_string + termcolor.colored("Blocked the command execution", "yellow")
                        print(log_string)
                        return

                    try:
                        if str(board_data["open"]) == "true":
                            if len(message.text) <= 250:
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
                                    cursor.execute("UPDATE posts SET comments='" + json.dumps(comments) + "' WHERE id='" + str(board_id) + "';")
                                    database.commit()
                                    await bot.send_message(chat_id, "Comment added to the board")

                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("Comment added", "green")

                                    await refresh_board(board_id)
                                except Exception as ex:
                                    await bot.send_message(chat_id, "Couldn't add your comment.")
                                    print(ex)

                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("couldn't add the comment", "red")

                                    if answering.get(user_id) is not None:
                                        del answering[user_id]
                            else:
                                await bot.send_message(chat_id,"Comment too long, 250 maximum characters allowed.")

                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("comment too long", "yellow")
                        else:
                            await bot.send_message(chat_id,"This board is closed, you can't comment now.")
                            await refresh_board(board_id)

                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to comment to a closed board", "yellow")

                            if answering.get(user_id) is not None:
                                del answering[user_id]
                    except Exception as ex:
                        print("Couldn't add a user comment")
                        print(ex)

                        await bot.send_mesage(chat_id,"Couldn't add the comment")
                        
                        log_string = log_string + " " + termcolor.colored("Couldn't add the comment", "red")

                        if answering.get(user_id) is not None:
                            del answering[user_id]
                else:
                    await bot.send_message(chat_id,"Error!\nUnrecognized board id.")

                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("unexisting board", "cyan")

                    if answering.get(user_id) is not None:
                        del answering[user_id]
            except Exception as ex:
                print("Couldn't get/find the target board")
                print(ex)

                await bot.send_mesage(chat_id,"Couldn't get/find the target board")
                
                log_string = log_string + " " + termcolr.colored("Couldn't get/find the target board", "cyan")
                
                if answering.get(user_id) is not None:
                    del answering[user_id]
        else:
            if message.via_bot is not None:
                return

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

                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("Adding a new comment", "green")
                        else:
                            await message.reply("This board is closed, you can't comment now.")

                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to comment to a closed board", "yellow")
                    else:
                        await bot.send_message(chat_id,"Error!\nunrecognized board id.")

                        log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("unexisting board", "yellow")
                else:
                    await bot.send_message(chat_id, placeholder(home, message, None),parse_mode="HTML",reply_markup=home_kb, disable_web_page_preview=True)

                    log_string = log_string + termcolor.colored("Sent the home", "green")
            elif cmd[0].lower() == "/admin":
                if str(chat_id) in bot_admins:
                    await bot.send_message(chat_id, placeholder(admin_home, message, None), reply_markup=admin_home_kb)

                    log_string = log_string + termcolor.colored("sent the admin panel", "green")
                else:
                    log_string = log_string + termcolor.colored("No permissions", "yellow")
            elif cmd[0].lower() == "/users":
                if str(chat_id) in bot_admins:
                    temp_sent_message = await bot.send_message(chat_id, placeholder("Calculating data, it can may take some minutes...", message, None))
                    
                    users_total = {}
                    unavailable_users = 0
                    users = [a for a in cursor.execute("SELECT * FROM users")]
                    for user in users:
                        try:
                            user_data = await bot.get_users([int(user[0])])
                            user_data = user_data[0]

                            if user_data.language_code != None:
                                lang = user_data.language_code.upper()

                                if users_total.get(lang) == None:
                                    users_total[lang] = 0
                                
                                users_total[lang] = users_total[lang] + 1
                            else:
                                unavailable_users = unavailable_users + 1
                        except Exception as ex:
                            print(ex)
                    
                    users_total_sorted = sorted(users_total, key= lambda x: users_total[x], reverse=True)
                    users_text = ""
                    for lang in users_total_sorted:
                        users_text = users_text + "\n<b>" + lang + "</b>: " + str(users_total[lang])
                    
                    await temp_sent_message.edit_text(users_text + "\n\nAvailable users: " + str(len(users) - unavailable_users) + "\nUnavailable users: " + str(unavailable_users))

                    log_string = log_string + termcolor.colored("sent the users counter", "green")
                else:
                    log_string = log_string + termcolor.colored("No permissions", "yellow")
            elif cmd[0].lower() == "/cancel":
                await bot.send_message(chat_id, "No operations to cancel.\n\n/start")

                log_string = log_string + termcolor.colored("No operations to cancel", "yellow")
            else:
                log_string = log_string + termcolor.colored("Unknow command", "yellow")
    else:
        await bot.send_message(chat_id, placeholder("This bot doesn't actually answer for commands in non-private chats.", message, None))

        log_string = log_string + termcolor.colored("Sent from non-private chat", "cyan")

    print(log_string)






@bot.on_callback_query()
async def callback(client,query):

    #print("onCallbackQuery event")
    #print(query)

    mid = query.message.message_id
    chat_type = query.message.chat.type
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    default_tables()

    log_string = now_time() + termcolor.colored("CallbackQuery", "cyan") + " from " + termcolor.colored(str(user_id), "green") + " in " + termcolor.colored(str(chat_id), "yellow") + " | data: '" + termcolor.colored(str(query.data), "magenta") + "' = "
    if creating_post.get(user_id) is None and editing_post.get(user_id) is None and answering.get(user_id) is None:
        data = query.data.split("_")

        if str(chat_type) == "private":
            add_chat(chat_id)

            if data[0] == "home":
                await query.answer()
                try:
                    await bot.edit_message_text(chat_id, mid, placeholder(home, query, None), reply_markup=home_kb, disable_web_page_preview=True)

                    log_string = log_string + "Returned to home"
                except Exception as ex:
                    print("An Exception occurred while a 'to home' edit")

                    log_string = log_string + termcolor.colored("An Exception occurred while a 'to home' edit", "red")
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
                        await bot.edit_message_text(chat_id, mid, placeholder("Panel closed due to a new board creation.", query, None))
                        await bot.send_message(chat_id, placeholder(new_post_step1, query, None))

                        log_string = log_string + termcolor.colored("Creating a new board", "green")
                    if data[1] == "mine":
                        comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE owner='" + str(user_id) + "';")]
                        if len(comparedentry) > 0:
                            await query.answer()
                            boards_list_keyboard = []
                            boards = parse_group_entry(comparedentry)
                            for board in boards:
                                boards_list_keyboard.append([InlineKeyboardButton(str(board["title"]).replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'"), callback_data="post_edit_" + str(board["id"]))])
                            boards_list_keyboard.append([InlineKeyboardButton("🔙 Back",callback_data="home")])
                            
                            await bot.edit_message_text(chat_id, mid, placeholder(messages_boards_list, query, None), reply_markup=InlineKeyboardMarkup(boards_list_keyboard), disable_web_page_preview=True)
                            
                            log_string = log_string + termcolor.colored("Returned to boards list", "green")
                        else:
                            await query.answer(placeholder(messages_no_boards, query, None))
                            try:
                                await bot.edit_message_text(chat_id, mid, placeholder(home, query, None), reply_markup=home_kb, disable_web_page_preview=True)
                            except Exception as ex:
                                none = None

                            log_string = log_string + termcolor.colored("Returned to home, no owned boards", "green")
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

                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("refresh (changed)", "green")
                                            except Exception as ex:
                                                await query.answer("No changes")

                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("refresh (no changes)", "green")
                                        elif data[3] == "title":
                                            await query.answer()
                                            editing_post[user_id] = {}
                                            editing_post[user_id]["id"] = str(data[2])
                                            editing_post[user_id]["section"] = "title"
                                            await bot.edit_message_text(chat_id, mid, placeholder("Panel closed due to a board title edit.", query, None))
                                            await bot.send_message(chat_id, placeholder("Ok, send me the new title/caption for this board...\n\n/cancel", query, None))

                                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("edit title operation started", "green")
                                        elif data[3] == "comments":
                                            if str(board_data["open"]) == "true":
                                                if len(literal_eval(board_data["comments"])) > 0:
                                                    if len(data) > 4:
                                                        try:
                                                            comment_to_delete = int(data[4])
                                                            comments = literal_eval(board_data["comments"])
                                                            
                                                            new_comments = []
                                                            count = 0
                                                            for comment in comments:
                                                                if count != comment_to_delete:
                                                                    new_comments.append(comment)
                                                                count = count + 1

                                                            cursor.execute("UPDATE posts SET comments='" + json.dumps(new_comments) + "' WHERE id='" + str(board_id) + "';")
                                                            
                                                            await refresh_board(board_id)

                                                            await query.answer("Comment deleted")
                                                        except Exception as ex:
                                                            await query.answer("Couldn't delete the comment")

                                                        try:
                                                            await send_edit_panel(query, board_id)
                                                        except Exception as ex:
                                                            none = None

                                                        log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("deleted the comment " + str(comment_to_delete), "green")
                                                    else:
                                                        await query.answer()
                                                        await send_comments_panel(query, board_id)

                                                        log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("sent to the comments panel", "green")
                                                else:
                                                    await query.answer("No comments yet in this board")

                                                    try:
                                                        await send_edit_panel(query, board_id)
                                                    except Exception as ex:
                                                        none = None

                                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to access the comments edit panel when the board is empty", "yellow")
                                            else:
                                                await query.answer("You can't edit the board comments when the board is closed")

                                                try:
                                                    await send_edit_panel(query, board_id)
                                                except Exception as ex:
                                                    none = None
                                            
                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to edit the board's comments but the board is closed", "yellow")
                                        elif data[3] == "clearComments":
                                            if str(board_data["open"]) == "true":
                                                if len(literal_eval(board_data["comments"])) > 0:
                                                    try:
                                                        cursor.execute("UPDATE posts SET comments='[]' WHERE id='" + str(board_id) + "';")
                                                        database.commit()

                                                        await query.answer("Board cleared successfully")
                                                        await refresh_board(board_id)

                                                        log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("cleared", "green")

                                                        try:
                                                            await send_edit_panel(query, board_id)
                                                        except Exception as ex:
                                                            none = None
                                                    except Exception as ex:
                                                        await query.answer("Couldn't clear the board")

                                                        log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("couldn't clear the board", "red")
                                                else:
                                                    await query.answer("The board is already empty")

                                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to clear the board but it's empty", "yellow")
                                            else:
                                                await query.answer("You can't clear the board when it's closed")
                                            
                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to clear the board when it's closed", "yellow")
                                        elif data[3] == "shareNotifications":

                                            initial_toggle = str(board_data["share_notifications"])
                                            final_toggle = ""

                                            try:
                                                if str(board_data["share_notifications"]) == "true":
                                                    cursor.execute("UPDATE posts SET share_notifications='false' WHERE id='" + str(board_id) +"';")
                                                    database.commit()

                                                    final_toggle = termcolor.colored("false", "red")
                                                else:
                                                    cursor.execute("UPDATE posts SET share_notifications='true' WHERE id='" + str(board_id) +"';")
                                                    database.commit()

                                                    final_toggle = termcolor.colored("true", "green")
                                                
                                                await query.answer("successfully toggled the share notifications option")
                                                try:
                                                    await send_edit_panel(query, board_id)
                                                except Exception as ex:
                                                    none = None
                                                
                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("share notification toggled", "green") + " " + final_toggle
                                            except Exception as ex:
                                                await query.answer("Couldn't switch the share notifications option")

                                                print("Couldn't switch the shareNotifications option for the board: " + str(board_id))
                                                print(ex)

                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("couldn't toggle the share notification", "red")
                                        elif data[3] == "privacyMode":

                                            initial_toggle = str(board_data["privacy_mode"])
                                            final_toggle = ""

                                            try:
                                                if str(board_data["privacy_mode"]) == "true":
                                                    cursor.execute("UPDATE posts SET privacy_mode='false' WHERE id='" + str(board_id) +"';")
                                                    database.commit()

                                                    final_toggle = termcolor.colored("false", "red")
                                                else:
                                                    cursor.execute("UPDATE posts SET privacy_mode='true' WHERE id='" + str(board_id) +"';")
                                                    database.commit()

                                                    final_toggle = termcolor.colored("true", "green")
                                                
                                                await query.answer("successfully toggled the privacy mode option")
                                                try:
                                                    await send_edit_panel(query, board_id)
                                                except Exception as ex:
                                                    none = None
                                                
                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("privacy mode toggled", "green") + " " + final_toggle
                                            
                                                await refresh_board(board_id)
                                            except Exception as ex:
                                                await query.answer("Couldn't switch the privacy mode option")

                                                print("Couldn't switch the privacyMode option for the board: " + str(board_id))
                                                print(ex)

                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("couldn't toggle the privacy mode", "red")
                                        elif data[3] == "toggle":
                                            comments = literal_eval(board_data["comments"])
                                            if len(comments) > 0:
                                                try:
                                                    
                                                    initial_toggle = str(board_data["open"])
                                                    fianl_toggle = ""
                                                    
                                                    if str(board_data["open"]) == "true":
                                                        cursor.execute("UPDATE posts SET open='false' WHERE id='" + str(board_id) +"';")
                                                        database.commit()

                                                        final_toggle = termcolor.colored("false", "red")
                                                    else:
                                                        cursor.execute("UPDATE posts SET open='true' WHERE id='" + str(board_id) +"';")
                                                        database.commit()

                                                        final_toggle = termcolor.colored("true", "green")
                                                    
                                                    await query.answer("successfully toggled the board")

                                                    try:
                                                        await send_edit_panel(query, board_id)
                                                    except Exception as ex:
                                                        none = None

                                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("toggled", "green") + " " + final_toggle
                                                
                                                    await refresh_board(board_id)
                                                except Exception as ex:
                                                    await query.answer("Couldn't toggle the board")

                                                    print("Couldn't toggle the board: " + str(board_id))
                                                    print(ex)

                                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("unable to toggle", "red")
                                            else:
                                                await query.answer("You can't close a board without comments")

                                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to close the board without comments", "yellow")
                                        else:
                                            await query.answer("Invalid edit section")

                                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("invalid edit section", "red")
                                    else:
                                        try:
                                            await query.answer()
                                            await send_edit_panel(query, str(data[2]))

                                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("opened an edit panel", "green")
                                        except Exception as ex:
                                            none = None

                                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("tried to open an edit panel", "yellow")
                                else:
                                    await query.answer("Error!\nThis board is not yours.", show_alert=True)

                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("un-owned board", "red")
                            else:
                                await query.answer("Error! Unrecognized board id.", show_alert=True)

                                try:
                                    await bot.edit_message_text(chat_id, mid, placeholder(home, query, None), reply_markup=home_kb, disable_web_page_preview=True)
                                except Exception as ex:
                                    none = None

                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("unexisting board", "yellow")
                        else:
                            await query.answer("Error! Incomplete query command data.")
                    if data[1] == "delete":
                        if len(data) > 2:
                            board_id = str(data[2])

                            comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
                            if len(comparedentry) > 0:
                                try:
                                    board_data = parse_entry(comparedentry)

                                    if str(user_id) == str(board_data["owner"]):
                                        try:
                                            cursor.execute("DELETE FROM 'posts' WHERE id='" + str(data[2]) + "';")
                                            database.commit()

                                            await query.answer()
                                            await bot.edit_message_text(str(chat_id), mid, placeholder("Board deleted successfully", query, None), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to boards list",callback_data="post_mine")]]))

                                            try:
                                                messages = literal_eval(board_data["messages"])
                                                for message in messages:
                                                    try:
                                                        await bot.edit_inline_text(message, messages_board_deleted, disable_web_page_preview=True)
                                                    except Exception as ex:
                                                        none = None
                                            except Exception as ex:
                                                print("An error occurred while trying to edit all board's messages")
                                                print(ex)

                                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("board deleted successfully", "green")
                                        except Exception as ex:
                                            print("An error occurred while trying to delete a board")
                                            print(ex)

                                            await query.answer("Couldn't delete the board")

                                            log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("couldn't delete", "red")
                                    else:
                                        await query.answer("Error!\nThis board is not yours.", show_alert=True)

                                        log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("un-owned board", "red")
                                except Exception as ex:
                                    await query.answer("An error occurred")

                                    log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("couldn't delete", "red")
                            else:
                                await query.answer("Error! Unrecognized board id.", show_alert=True)

                                try:
                                    await bot.edit_message_text(chat_id, mid, placeholder(home, query, None), reply_markup=home_kb, disable_web_page_preview=True)
                                except Exception as ex:
                                    none = None

                                log_string = log_string + "board (" + str(board_id) + ") " + termcolor.colored("unexisting board", "yellow")
                        else:
                            log_string = log_string + termcolor.colored("insufficient arguments", "yellow")
            if data[0] == "admin":
                if str(user_id) in bot_admins:
                    if len(data) > 1:
                        if data[1] == "user":
                            await query.answer("Work in progress..")
                else:
                    try:
                        await bot.delete_messages(chat_id, mid)
                    except Exception as ex:
                        none = None
        else:
            await query.answer("This bot doesn't actually answer callback queries in non-private chats.", show_alert=True)
    else:
        await query.answer("You can't use buttons during a text operation\n\nYou can use the /cancel command.", show_alert=True)
    print(log_string)





@bot.on_inline_query()
async def inline(client,query):
    global messages

    #print("onInlineQuery event")
    #print(query)

    user_id = query.from_user.id

    default_tables()

    log_string = now_time() + termcolor.colored("InlineQuery","cyan") + " from " + termcolor.colored(str(user_id), "green") + " | query: '" + termcolor.colored(str(query.query), "magenta") + "' ="

    if len(query.query) > 0:
        log_string = log_string + " " + termcolor.colored("non-empty query", "green") + " ="

        board_id = str(query.query)
        board_id = board_id.replace("'","////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///")

        comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
        if len(comparedentry) > 0:
            board_data = parse_entry(comparedentry)
            await bot.answer_inline_query(query.id, results=[InlineQueryResultArticle(str(board_data["title"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")),InputTextMessageContent(board_text(board_data), disable_web_page_preview=True),id=str(board_data["id"]),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✒️ Leave a comment",url="https://t.me/CommentsBoardBot?start=" + str(board_data["id"]))]]))],cache_time=1,is_personal=True)

            log_string = log_string + " board ('" + str(board_id) + "') " + termcolor.colored("answered", "green")
        else:
            await bot.answer_inline_query(query.id, results=[InlineQueryResultArticle("No Results",InputTextMessageContent("No results", disable_web_page_preview=True))],cache_time=1,is_personal=True)

            log_string = log_string + " board ('" + str(board_id) + "') " + termcolor.colored("no results", "green")
    else:
        log_string = log_string + " empty query ="

        comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE owner='" + str(user_id) + "';")]
        if len(comparedentry) > 0:
            boards = parse_group_entry(comparedentry)
            boards_results = []

            for board_data in boards:
                boards_results.append(InlineQueryResultArticle(str(board_data["title"].replace("////+!!!+-,..-,.,,,,,,,OOf-..,,,!!+///", "'")),InputTextMessageContent(board_text(board_data), disable_web_page_preview=True),id=str(board_data["id"]),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✒️ Leave a comment",url="https://t.me/CommentsBoardBot?start=" + str(board_data["id"]))]])))
            await bot.answer_inline_query(query.id, results=boards_results,cache_time=1,is_personal=True)

            log_string = log_string + termcolor.colored(" answered with " + str(len(boards)) + " boards", "green")
        else:
            await bot.answer_inline_query(query.id, results=[InlineQueryResultArticle("No Results",InputTextMessageContent("No results", disable_web_page_preview=True))],cache_time=1,is_personal=True)

            log_string = log_string + termcolor.colored(" no results", "yellow")
    
    print(log_string)





@bot.on_chosen_inline_result()
async def inline_choice(client,result):
    global messages

    #print("on_chosen_inline_result event")
    #print(result)

    user_id = result.from_user.id
    board_id = result.result_id

    log_string = now_time() + termcolor.colored("InlineQueryChosen", "cyan") + " from " + termcolor.colored(str(user_id), "green") + " | result_id: '" + termcolor.colored(str(result.result_id), "magenta") + "' ="

    comparedentry = [a for a in cursor.execute("SELECT * FROM posts WHERE id='" + str(board_id) + "';")]
    if len(comparedentry) > 0:
        log_string = log_string + " " + termcolor.colored("board existing", "green") + " ="

        board_data = parse_entry(comparedentry)
        messages = literal_eval(board_data["messages"])
        messages.append(result.inline_message_id)
        try:
            cursor.execute("UPDATE posts SET 'messages'='" + json.dumps(messages) + "' WHERE id='" + str(board_id) + "';")
            database.commit()

            log_string = log_string + " " + termcolor.colored("Board message saved", "green") + ","

            try:
                if str(board_data["share_notifications"]) == "true":
                    if str(user_id) != str(board_data["owner"]):
                        name = result.from_user.first_name
                        if result.from_user.last_name is not None:
                            name = name + " " + result.from_user.last_name
                        name = name.replace("<","&lt;")
                        name = name.replace(">","&gt;")

                        await bot.send_message(board_data["owner"], placeholder("<a href='tg://user?id=" + str(user_id) + "'>" + str(name) + "</a> shared your board.\n\n{board_title}\nID: <code>{board_id}</code>", result, board_data), disable_web_page_preview=True)

                        log_string = log_string + termcolor.colored(" Share notification sent", "green")
                    else:
                        log_string = log_string + termcolor.colored(" Shared by the owner", "yellow")
                else:
                    log_string = log_string + termcolor.colored(" Share notification disabled", "yellow")
            except Exception as ex:
                print("I was unable to send a share notification")
                print(ex)

                log_string = log_string + termcolor.colored(" Couldn't send a share notification", "red")
        except Exception as ex:
            print("An error occurred while saving a new board's message")
            print(ex)
            print("board_id: " + str(board_id))
            print("new inline message id: " + str(result.inline_message_id))

            try:
                await bot.edit_inline_text(result.inline_message_id, "An error occurred while trying to link this inline message to his board.", disable_web_page_preview=True)
            except Exception as ex:
                none = None
            
            log_string = log_string + termcolor.colored(" Couldn't save a board message", "red")
    else:
        log_string = log_string + termcolor.colored(" No Results", "green")

    print(log_string)

###############

idle()
# 1139 righe di agonia! ma è stato un piacere!