import mailbox
import re



# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

discard = False

def test_edit(message):
    payload1 = mailbox.mboxMessage(message.get_payload()[0])
    payload2 = payload1.get_payload()
    payload2 = re.sub(r'Daddy', 'Mommy', payload2, flags=re.MULTILINE)
    payload1.set_payload(payload2)
    message.set_payload(payload1)
    return message

def get_payloads(message):
    global discard
    res = [message]
    done = False
    while not done:
        temp = res[len(res) - 1].get_payload() #eventuell tupel getten
        if type(temp) is list:
            if len(temp) > 1:
                print('long list found - discarding')
                discard = True
            temp = temp[0]
        res.append(temp)
        if type(temp) is str or type(temp) is bytes:
            done = True
    return res

def set_payloads(payloads):
    for i in range(1, len(payloads) - 1):
        idx = len(payloads) - i - 1
        payloads[idx].set_payload(payloads[idx + 1])
    return payloads[0]

def encode_payload(string, payloads):
    if payloads[0]._headers:
        for header in payloads[0]._headers:
            if header[0] == 'Content-Type':
                if 'Windows-1251' in header[1]:
                    return string.encode('windows-1251').decode('windows-1251').encode('utf-8')
    return string.encode('utf-8')

def clean_links(message):
    payloads = get_payloads(message)
    if not discard:
        clean_link = 'https://its.phishing.fake'
        temp = re.sub(r'https?:\/\/[^">]*', clean_link, payloads[len(payloads) - 1], flags=re.MULTILINE)
        payloads[len(payloads) - 1] = temp.encode('utf-8')#encode_payload(temp, payloads)
    return set_payloads(payloads)
    # payload1 = mailbox.mboxMessage(message.get_payload()[0])
    # payload2 = payload1.get_payload()
    # payload2 = re.sub(r'https?:\/\/[^">]*', clean_link, payload2, flags=re.MULTILINE)
    # res = payload2.encode('utf-8')
    # payload1.set_payload(res)
    # message.set_payload(payload1)
    #return message

def edit_headers(message):
    sender_mail = 'attacker@phishing.fake'
    recipient_mail = 'victim@phishing.fake'
    sender = '[attacker]'
    recipient = '[victim]'
    keep = ['Subject', 'Sender', 'Content-Type', 'Return-Path', 'X-Original-To', 'Delivered-To', 'From', 'Subject'
        , 'X-Priority', 'Content-Type', 'Content-Length', 'Lines', 'Status', 'X-Status', 'X-Keywords', 'Content-Type']
    newHeaders = []
    for header in message._headers:
        #print (header)
        if header[0] in keep:
            newHeader = (header[0], header[1])
            if header[0] == 'Sender' or header[0] == 'From':
                newHeader = (newHeader[0], re.sub(r'<.*@.*>', '<' + sender + '>', newHeader[1], flags=re.MULTILINE))
            if header[0] == 'Return-Path':
                newHeader = (newHeader[0], '<' + sender_mail + '>')
            if header[0] == 'X-Original-To' or header[0] == 'Delivered-To':
                newHeader = (newHeader[0], recipient_mail)
            newHeaders.append(newHeader)
    message._headers = newHeaders
    return message

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    mbox = mailbox.mbox('private-phishing4.mbox')
    output = mailbox.mbox('output.mbox', create=True)
    i = 0
    for mailTuple in mbox.iteritems():
        print(i)
        i += 1
        message = mailTuple[1]
        message = clean_links(message)
        if not discard:
            message = edit_headers(message)
            output.add(message)
        discard = False
        mbox.flush()
    mbox.close()
    output.close()
    print('mail')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
