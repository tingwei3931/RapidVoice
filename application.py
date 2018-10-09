
from flask import Flask
from flask_ask import Ask, statement, question, session
import csv
import smtplib
from typing import List, Dict, Tuple
import copy
from random import choice
import time
#from nltk.corpus import wordnet, stopwords
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
ask = Ask(app, '/')


#data_list

def send_mail(html: str, *, to: str = 's.stanynaite@gmail.com'):
    gmail_user = "elb.voice.innotrans@gmail.com"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(gmail_user, "byW4m8o>joAas}ZJK7LLr[)f8ZK9^T")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Network Rail standard report"
    msg['From'] = gmail_user
    msg['To'] = to

    part1 = MIMEText(html, 'html')
    msg.attach(part1)

    try:
        server.sendmail(gmail_user, to, msg.as_string())
        print('email sent')

    except:
        print('error sending mail')

    server.quit()


def prepare_and_send(data, keywords):
    TEXT = f"Results for the query with keywords: <b>{' - '.join([word.upper() for word in keywords])}</b>"

    html = """\
    <html>
      <head></head>
      <body>
        %s
      </body>
    </html>
    """

    for index, (key, value) in enumerate(data.items()):
        TEXT += f"<p>{index + 1}.<br>" \
                f"Title: {value['Title']}<br>" \
                f"Link: {value['StandardLink']}<br>" \
                f"Reference: {value['Reference']}<br>" \
                f"Department: {value['Standard Owner']}<br>"

        if index == 0:
            TEXT += '<i><a href="https://sriram6897.wixsite.com/networkrails" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://sriram6897.wixsite.com/networkrails&amp;source=gmail&amp;ust=1537608863662000&amp;usg=AFQjCNH0KXCg1iK9ZU6JLX1Mv1EWqOP5mA">Rate the Standard</a>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;&nbsp;<a href="https://sriram6897.wixsite.com/networkrails" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://sriram6897.wixsite.com/networkrails&amp;source=gmail&amp;ust=1537608863662000&amp;usg=AFQjCNH0KXCg1iK9ZU6JLX1Mv1EWqOP5mA">Report a problem</a></i>'
            TEXT += '<div><img src="https://image.ibb.co/bWzJBe/star.png" width="202" height="50" style="margin-right:0px" data-image-whitelisted=""><img src="https://image.ibb.co/gkhzHK/warning.png" width="45" height="45" style="margin-right:0px" data-image-whitelisted=""></div></p><br>'

    send_mail(html % TEXT)


def remove_stopwords(words: List[str]) -> List[str]:
    global stopwords_list

    for word in words.copy():
        if word in stopwords_list:
            words.remove(word)

    return words


def sanitize(words):
    global excluded_keywords

    for word in words.copy():
        if len(word) in [1, 2] + excluded_keywords:
            words.remove(word)

    return words


"""
def tokenize_data(data):
    new_data = copy.deepcopy(data)

    for key, value in list(new_data.items()):

        value['token_title'] = []

        for sentence in nltk.sent_tokenize(value['Title']):
            for word in sanitize(remove_stopwords(nltk.word_tokenize(sentence))):
                #if word.lower() in nouns:
                value['token_title'].append(word.lower())

    return new_data
"""

def filter_titles(data, keywords) -> Tuple[Dict, Dict]:
    new_data = copy.deepcopy(data)
    priority = {}

    for key, value in new_data.copy().items():

        skip = False
        for keyword in keywords:
                if keyword not in value['token_title']:
                    skip = True
                    del new_data[key]

                    break

        if not skip:
            if len(keywords) >= (len(value['token_title']) * 0.60):
                priority[key] = value

    return priority, new_data


def get_most_used_token(data, excluded=[]):
    counter = {}

    for key, value in data.items():
        for entry in value['token_title']:
            if entry not in excluded:
                counter.setdefault(entry, 0)
                counter[entry] += 1

    return list(sorted(counter.items(), key=lambda a: a[1], reverse=True))[0][0]


def remove_token(data, keyword):
    new_data = copy.deepcopy(data)

    for key, value in new_data.copy().items():
        if keyword in value['token_title']:
            del new_data[key]

    return new_data


@app.route("/")
def hello():
    return "Hello World!"




@ask.launch
def launch():
    print("------ RapidVoice Launching ----------")

    speech = "Welcome to RapidVoice, what can I help you today?"

    print('speech = {}'.format(speech))

    return question(speech).reprompt("I didn't quite catch that, could you please repeat that?")


@ask.intent("TimetableIntent", convert={'route': int})
def test(route):
    print(route)
    speech = f"The timetable for rapid bus is "
    
    print('speech = {}'.format(speech))
    
    return statement(speech)

busStop1 = ""


@ask.intent("BusComingIntent")
def bus_coming():
    speech = f"The bus number is 203 arriving to Jalan Air Itam"
    
    print('speech = {}'.format(speech))
    
    return statement(speech)

@ask.intent("NextStopIntent", convert={'busStop': str})
def next_stop(busStop):
    arrival_time = ""
    csv_reader = csv.reader(open('./bus-updated.csv'), delimiter=';')
    list_data = list(csv_reader)
    #print(list_data)
    data_list = []
    #Route, Latitude, Longitude, Bus Stop, Time
    attributes = list_data[0];
    print(busStop);
    for dataline in list_data[1:]:
        data = {}
        split_data = dataline[0].split(',')
        data['Route'] = int(split_data[0])
        data['Latitude'] = float(split_data[1])
        data['Longitude'] = float(split_data[2])
        data['Bus_Stop'] = split_data[3]
        data['Time'] = split_data[4]
        data_list.append(data)
    for data in data_list:
        if data['Bus_Stop'].lower() == busStop:
            global busStop1
            busStop1 = busStop
            arrival_time = data['Time']  
    speech = f"The next bus will arrive at {busStop} at {arrival_time} a.m.."
    print('speech = {}'.format(speech))
    
    return statement(speech)


@ask.intent("NextBusIntent", convert={'busNumber': str})
def next_bus(busNumber):
    arrival_time = ""
    busStop = ""
    csv_reader = csv.reader(open('bus-updated.csv'), delimiter=';')
    list_data = list(csv_reader)
    #print(list_data)
    data_list = []
    #Route, Latitude, Longitude, Bus Stop, Time
    #attributes = list_data[0];
    print("********")
    for dataline in list_data[1:]:
        data = {}
        split_data = dataline[0].split(',')
        data['Route'] = int(split_data[0])
        data['Latitude'] = float(split_data[1])
        data['Longitude'] = float(split_data[2])
        data['Bus_Stop'] = split_data[3]
        data['Time'] = split_data[4]
        data_list.append(data)
    for data in data_list:
        if str(data['Route']) == busNumber:
            busStop = data['Bus_Stop']
			arrival_time = data['Time']  
    speech = f"The next {busNumber} bus will arrive at {busStop} at {arrival_time} a.m.."
    print('speech = {}'.format(speech))
    
    return statement(speech)
"""


@ask.intent("SpecifyStandard", convert={'query': str})
def specify_standard(query):
    global stopwords_list
    global tokenized_data
    global tokenized_data_full
    global matched_tags
    global excluded_keywords

    tokenized_data = tokenized_data_full

    print(f"started SpecifyStandard Intent with query {query}")

#    matched_tags = [keyword.lower() for keyword in sanitize(remove_stopwords(nltk.word_tokenize(query)))]
    print(f"matched keywords {matched_tags}")

    priority, tokenized_data = filter_titles(tokenized_data, matched_tags)
    print(f"matched {len(priority)} priority and {len(tokenized_data)} standards")

    if priority:

        if len(priority) != 1:
            (index, value) = choice(list(priority.items()))

            if value['Reference']:

                insert_str = f" with reference number {value['Reference']} "

            else:

                insert_str = " "

            speech = f"I’ve found {len(priority)} perfect hit for the keyword {' '.join(matched_tags)}. " \
                     f"The title for the most fitting one is " \
                     f"{value['Title']}{insert_str}" \
                     f"and accountable department is {value['Standard Owner']}. " \
                     f"I’m sending you an email with further details."

        else:

            (index, value) = list(priority.items())[0]

            if value['Reference']:

                insert_str = f" with reference number {value['Reference']} "

            else:

                insert_str = " "

            speech = f"I’ve found a perfect hit for the keywords {' '.join(matched_tags)}. The title is " \
                     f"{value['Title']}{insert_str}" \
                     f"and accountable department is {value['Standard Owner']}. " \
                     f"I’m sending you an email with further details."

        print('speech = {}'.format(speech))

        prepare_and_send(priority, matched_tags)

        return statement(speech)

    else:

        if len(tokenized_data) == 0:
            speech = f"Unfortunately i have found no matching documents for your queried keywords " \
                     f"{' '.join(matched_tags)}, " \
                     f"please change the search terms and try again."

            return statement(speech)

        elif len(tokenized_data) == 1:

            (index, value) = list(tokenized_data.items())[0]

            if value['Reference']:

                insert_str = f" with reference number {value['Reference']} "

            else:

                insert_str = " "

            speech = f"I’ve found a perfect hit for the query {' '.join(matched_tags)}. The title is " \
                     f"{value['Title']}{insert_str}" \
                     f"and accountable department is {value['Standard Owner']}. " \
                     f"I’m sending you an email with further details."

            print('speech = {}'.format(speech))

            prepare_and_send(tokenized_data, matched_tags)

            return statement(speech)

        elif len(tokenized_data) < 4:

            (index, value) = choice(list(tokenized_data.items()))

            if value['Reference']:

                insert_str = f" with reference number {value['Reference']} "

            else:

                insert_str = " "

            speech = f"I’ve found {len(tokenized_data)} hits for your query. The title for the most fitting one is " \
                     f"{value['Title']}{insert_str}" \
                     f"and accountable department is {value['Standard Owner']}. " \
                     f"I’m sending you an email with further details."

            print('speech = {}'.format(speech))

            prepare_and_send(tokenized_data, matched_tags)

            return statement(speech)

        # matched too many
        else:

            session.attributes['new_tag'] = get_most_used_token(tokenized_data, excluded=matched_tags + excluded_keywords + stopwords_list)

            speech = f"Your query returned {len(tokenized_data)} documents. " \
                     f"Is your standard also related to {session.attributes['new_tag']}?"

            session.attributes['context'] = "asking_tag"

            print('speech = {}'.format(speech))

            return question(speech).reprompt("I didn't get that, please answer with yes or no")


@ask.intent('AMAZON.YesIntent')
def answer_to_yes():
    global tokenized_data
    global stopwords_list
    global excluded_keywords
    global matched_tags

    if session.attributes.get('context') == "asking_tag":

        print(f"YES matched {matched_tags}")

        matched_tags.append(session.attributes['new_tag'])

        priority, tokenized_data = filter_titles(tokenized_data, matched_tags)
        print(f"matched {len(priority)} priority and {len(tokenized_data)} standards")

        if priority:

            if len(priority) != 1:
                (index, value) = choice(list(priority.items()))

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found {len(priority)} perfect hit for your query. The title for the most fitting one is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}. " \
                         f"I’m sending you an email with further details."

            else:

                (index, value) = list(priority.items())[0]

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found a perfect hit for your query. The title is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}. " \
                         f"I’m sending you an email with further details."

            print('speech = {}'.format(speech))

            prepare_and_send(priority, matched_tags)

            return statement(speech)

        else:

            if len(tokenized_data) == 0:
                speech = f"Unfortunately i have found no matching documents for your query," \
                         f"please change the search terms and try again."

                print('speech = {}'.format(speech))

                prepare_and_send(tokenized_data, matched_tags)

                return statement(speech)

            elif len(tokenized_data) == 1:

                (index, value) = list(tokenized_data.items())[0]

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found a perfect hit for your query. The title is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}." \
                         f"I’m sending you an email with further details."

                print('speech = {}'.format(speech))

                prepare_and_send(tokenized_data, matched_tags)

                return statement(speech)

            elif len(tokenized_data) < 4:

                (index, value) = choice(list(tokenized_data.items()))

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found {len(tokenized_data)} hits for your query. The title for the most fitting one is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}. " \
                         f"I’m sending you an email with further details."

                print('speech = {}'.format(speech))

                prepare_and_send(tokenized_data, matched_tags)

                return statement(speech)

            # matched too many
            else:

                session.attributes['new_tag'] = get_most_used_token(tokenized_data, excluded=matched_tags +
                                                                                             excluded_keywords +
                                                                                             stopwords_list)

                speech_list = [f"Great. Is it related to {session.attributes['new_tag']} as well?",
                               f"Is it also related to {session.attributes['new_tag']})",
                               f"Perfect. Does it also include {session.attributes['new_tag']}?"]

                speech = choice(speech_list)

                session.attributes['context'] = "asking_tag"

                print('speech = {}'.format(speech))

                return question(speech).reprompt("I didn't get that, please answer with yes or no")


@ask.intent('AMAZON.NoIntent')
def answer_to_no():
    global tokenized_data
    global excluded_keywords
    global stopwords_list
    global matched_tags

    print(f"started AMAZON.NoIntent with context {session.attributes['context']}")

    if session.attributes.get('context') == "asking_tag":

        print(f"NO matched {matched_tags}")

        tokenized_data = remove_token(tokenized_data, session.attributes['new_tag'])

        priority, tokenized_data = filter_titles(tokenized_data, matched_tags)
        print(f"matched {len(priority)} priority and {len(tokenized_data)} standards")

        if priority:

            if len(priority) != 1:
                (index, value) = choice(list(priority.items()))

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found {len(priority)} perfect hit for your query. The title for the most fitting one is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}. " \
                         f"I’m sending you an email with further details."

            else:

                (index, value) = list(priority.items())[0]

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found a perfect hit for your query. The title is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}. " \
                         f"I’m sending you an email with further details."

            print('speech = {}'.format(speech))

            prepare_and_send(priority, matched_tags)

            return statement(speech)

        else:

            if len(tokenized_data) == 0:
                speech = f"Unfortunately i have found no matching documents for your query," \
                         f"please change the search terms and try again."

                return statement(speech)

            elif len(tokenized_data) == 1:

                (index, value) = list(tokenized_data.items())[0]

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found a perfect hit for your query. The title is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}." \
                         f"I’m sending you an email with further details."

                print('speech = {}'.format(speech))

                prepare_and_send(tokenized_data, matched_tags)

                return statement(speech)

            elif len(tokenized_data) < 4:

                (index, value) = choice(list(tokenized_data.items()))

                if value['Reference']:

                    insert_str = f" with reference number {value['Reference']} "

                else:

                    insert_str = " "

                speech = f"I’ve found {len(tokenized_data)} hits for your query. The title for the most fitting one is " \
                         f"{value['Title']}{insert_str}" \
                         f"and accountable department is {value['Standard Owner']}. " \
                         f"I’m sending you an email with further details."

                print('speech = {}'.format(speech))

                prepare_and_send(tokenized_data, matched_tags)

                return statement(speech)

            # matched too many
            else:

                session.attributes['new_tag'] = get_most_used_token(tokenized_data, excluded=matched_tags +
                                                                                             excluded_keywords +
                                                                                             stopwords_list)

                speech_list = [f"Ok. What about {session.attributes['new_tag']}?",
                               f"Maybe it is related to {session.attributes['new_tag']} then?",
                               f"How about {session.attributes['new_tag']} then?"]

                speech = choice(speech_list)

                session.attributes['context'] = "asking_tag"

                print('speech = {}'.format(speech))

                return question(speech).reprompt("I didn't get that, please answer with yes or no")


@ask.intent('AMAZON.StopIntent')
def stop():
    return statement("Thank you for using RapidVoice. Have a nice day ")


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("Goodbye")


@ask.intent('AMAZON.FallbackIntent')
def fallback():
    return question("I didn't quite catch that, could you please repeat your request")


@ask.session_ended
def session_ended():
    return "{}", 200
    
if __name__ == "__main__":
    """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    import nltk

    print("Downloading wordnet")
    nltk.download('wordnet')

    print("Downloading stopwords")
    nltk.download('stopwords')

    print("Downloading punkt")
    nltk.download('punkt')

    print("creating datasets")

    nouns = {word.lower() for word in {x.name().split('.', 1)[0] for x in wordnet.all_synsets('n')}}

    stopwords_list = list([word.lower() for word in stopwords.words('english')])
    excluded_keywords = [word.lower()for word in list(filter(lambda a: a != "",
                                    [row for row in list(csv.reader(open('csv_remove.csv'), delimiter=",")) for row in
                                     row]))]

    
    excluded_keywords += ['standard', 'rail', 'large', 'small', 'how', 'traditional']
    """
    print("loading csv data")
    csv_reader = csv.reader(open('bus-updated.csv'), delimiter=';')
    list_data = list(csv_reader)
    #print(list_data)
    data_list = []
    #Route, Latitude, Longitude, Bus Stop, Time
    attributes = list_data[0];
   
    for dataline in list_data[1:]:
        data = {}
        split_data = dataline[0].split(',')
        data['Route'] = int(split_data[0])
        data['Latitude'] = float(split_data[1])
        data['Longitude'] = float(split_data[2])
        data['Bus_Stop'] = split_data[3]
        data['Time'] = split_data[4]
        data_list.append(data)
    print(data_list)
    
    bus_101 = data_list[:16] 
    bus_203 = data_list[16:]
    print(bus_101, bus_203)
    
    print(len(bus_101))
    print(len(bus_203))
    """
    headers = list_data[0]
    headers[0] = "StandardLink"
    """
    """
    csv_data = {index: data for index, data in
                enumerate([{x: y for (x, y) in list(zip(headers, row))} for row in list_data[1:]])}
    """
    print("loaded csv data")

    """
    tokenized_data_full = tokenize_data(csv_data)
    print("tokenized data") 
    """
    time.sleep(1)

    print("starting app")
    app.run(host="0.0.0.0", ssl_context=('certificate.pem', 'private-key.pem'), port=443)

