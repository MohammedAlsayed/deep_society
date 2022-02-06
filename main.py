#!/usr/bin/python3

import os
from random import randint
import openai
from flask import Flask
from flask import request, jsonify
import json
import sqlite3
con = sqlite3.connect('chat.db')
cursor = con.cursor()

app = Flask(__name__)

chat_dict = {}

@app.route('/')
def main():
    return jsonify("hello world"), 200

# 127.0.0.1:5000/login?username=Jack
# https://deepsociety-340502.wn.r.appspot.com/login?username=Jack
@app.route('/login')
def login():
    print("DEBUG: chat_dict: "+ str(chat_dict))
    username = request.args.get('username')
    if username == None:
        return jsonify({"text":"Please check the spelling of username query parameter"}), 400
    if username in chat_dict:
        reply = "Hello {}, happy to be your deep society connecter :), but this name is already taken. May you enter another one?".format(username)
        return jsonify({"text":reply}), 200
    dict_welcome= {
        1 :"Hello {}. I'm your friendly Bob :), and I'm here to deepen your understanding about the people that surround you and don't.".format(username),
        2 :"Hello {}! My name is Bob and I'm here to help you understand the people around you who are different from you.".format(username),
        3 : "Hi {}! I'm your friendly Bob. I'm here to help you understand the people around you better.".format(username),
    }
    chat_idx = 1
    welcome_text = dict_welcome[randint(1,3)]
    chat_dict[username] = {
        "bot_name": "Bob",
        "chat":{
            chat_idx:welcome_text
        }
    }
    return jsonify({"text":welcome_text}), 200

# 127.0.0.1:5000/send?username=Jack&text=That's great! I was hoping you can tell me about Saudi Arabia.
# https://deepsociety-340502.wn.r.appspot.com/send?username=Jack&text=That's great! I was hoping you can tell me about Saudi Arabia.
@app.route('/send')
def send():
    print("DEBUG: chat_dict: "+ str(chat_dict))
    username = request.args.get('username')
    text = request.args.get('text')
    if username == None:
        return jsonify({"text":"please check the spelling of username query parameter"}), 400
    if text == None:
        return jsonify({"text":"please check the spelling of text query parameter"}), 400

    if username not in chat_dict:
        print("DEBUG: chat_dict: "+ str(chat_dict))
        return jsonify({"text":"Please login first"}), 200

    if len(text) < 1:
        reply = "I'm sorry, {}, I don't know what you're asking. Can you please clarify?".format(username)
        return jsonify({"text":reply}), 200

    chat_idx = len(chat_dict[username]["chat"]) +1
    # add user text to his chat history
    chat_dict[username]["chat"].update({chat_idx:text})
    openai.api_key = "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"
    prompt = ""
    chat = chat_dict[username]["chat"]
    chat_bot_name = chat_dict[username]["bot_name"]
    # aggregate previous chat with sent text
    for keys, values in chat.items(): 
        if keys % 2 != 0: # odd
            prompt = prompt+"{}: {}\n".format(chat_bot_name, values)
        if keys % 2 == 0:
            prompt = prompt+"{}: {}\n".format(username, values)

    prompt = prompt + chat_bot_name + ":"
    print("DEBUG: prompt: "+prompt)
    response = openai.Completion.create(engine="text-davinci-001", prompt=prompt , max_tokens=20)
    response_text = response.choices[0].text
    response_text = response_text.strip()
    print("DEBUG: AI response_text: "+response_text)
    chat_idx += 1
    chat.update({chat_idx:response_text})
    return jsonify({"text":response_text}), 200

# 127.0.0.1:5000/clear?username=Jack
# https://deepsociety-340502.wn.r.appspot.com/clear?username=Jack
@app.route('/clear')
def clear():
    print("DEBUG: chat_dict: "+ str(chat_dict))
    username = request.args.get('username')
    if username in chat_dict:
        chat_dict.pop(username)
        print("DEBUG: username sucessfuly: "+username)
        return jsonify({"text":"Username sucessfuly deleted"}), 200
    else:
        print("DEBUG: username does not exist: "+username)
        return jsonify({"text":"Username does not exist"}), 200

@app.route('/changeBot')
def changeBot():
    print("DEBUG: chat_dict: "+ str(chat_dict))
    username = request.args.get('username')
    new_name = request.args.get('botName')
    if username == None:
        return jsonify({"text":"please check the spelling of username query parameter"}), 400
    if new_name == None:
        return jsonify({"text":"please check the spelling of name query parameter"}), 400
    if username not in chat_dict:
        print("DEBUG: chat_dict: "+ str(chat_dict))
        return jsonify({"text":"Please login first"}), 200

    chat_dict[username]["bot_name"] = new_name
    return jsonify({"text":"Bot name changed successfully"}), 200

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, threaded=False, processes=1)