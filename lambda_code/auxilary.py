import boto3
import os
import sendgrid
from boto3.dynamodb.conditions import Attr
from sendgrid.helpers.mail import *

def get_a_question(done_list, topic_list):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('gfg_questions')
    questions = []
    if topic_list:
        for topic in topic_list:
            query_res = table.scan(
                            FilterExpression = Attr('tags').contains(topic)
                        )
            for question in query_res['Items']:
                if not done_list or question['qlink'] not in done_list:
                    questions.append(question)
            # print(query_res['Items'])
    else:
        query_res = table.scan(Limit=10)
        questions = list(query_res['Items'])
    newlist = sorted(questions, key=lambda k: k['rating']) 
    if newlist:
        return newlist[0]
    else:
        return None

def send_email(to, object):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("interview_me_alexa_skill@donotreply.com")
    to_email = Email(to)
    subject = object['title']
    text_content = (object['problem'] + "\n\nYou can practice the problem at {}".format(object['practice'])
       + "\n\nSee the solution at {}".format(object['qlink']))
    content = Content("text/plain", text_content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

if __name__ == '__main__':
    # Testing this thing !
    x = get_a_question(
            ['https://www.geeksforgeeks.org/linked-list-set-3-deleting-node/',
             'https://www.geeksforgeeks.org/reverse-nodes-of-a-linked-list-without-affecting-the-special-characters/'],
            ['Linked List']
        )
    print(x)
    send_email('virresh26@gmail.com', x)
