import mailbox
import re
import csv
import html2text
import string
import unicodedata
from langdetect import detect, DetectorFactory



# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

discard = False

printable = {'Lu', 'Ll', 'Zs', 'Zl', 'Nd', 'Cf', 'Zp', 'Cc', 'Po'}
def filter_non_printable(str): #testing purposes
 return ''.join(c for c in str if unicodedata.category(c) in printable)
   # return ''.join(c for c in str if not unicodedata.category(c).startswith('C'))


def get_payloads(message):
    global discard
    res = [message]
    done = False
    while not done:
        temp = res[len(res) - 1].get_payload() #eventuell tupel getten
        if type(temp) is list:
            if len(temp) > 1:
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

def get_text(message):
    payloads = get_payloads(message)
    temp = html2text.html2text(payloads[len(payloads) - 1])
    for header in message._headers:
        if header[0] == 'Subject':
            temp = header[1] + '\n\n' + temp
    return temp#.encode('utf-8')

def remove_links(text):
    clean_link_short = 'its.phishing.fake'
    clean_link = 'https://' + clean_link_short
    text = re.sub(r'https?:\/\/[^]) ]*', clean_link, text, flags=re.MULTILINE)
    text = re.sub(r'www\.[^])]*', clean_link_short, text, flags=re.MULTILINE)
    # removing new line from link names
    text = re.sub(r'\[(.*)[\n](.*)]', r'\[\1 \2]', text, flags=re.MULTILINE)
    # reformating links:
    for i in range(0, 2): # repetition for nested links
        text = re.sub(r'\[(.*)]\(' + clean_link + '\)', r'LINK[\1]', text, flags=re.MULTILINE)
        text = re.sub(r'\[(.*)]\(' + clean_link_short + '\)', r'LINK[\1]', text, flags=re.MULTILINE)
        #make links that weren't labelled more readable:
        text = re.sub(r'LINK\[' + clean_link + ']', r'LINK[]', text, flags=re.MULTILINE)
        text = re.sub(r'LINK\[' + clean_link_short + ']', r'LINK[]', text, flags=re.MULTILINE)
    text = re.sub(r'LINKLINK', r'LINK', text, flags=re.MULTILINE)
    text = re.sub(r'\[]]', r']', text, flags=re.MULTILINE)
    return text

def remove_files_in_plaintext(text):
    start = text
    text = re.sub(r'file\:.*', '', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'end\:.*', '', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'type\:.*', '', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'media\:.*', '', text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r'0[=x][0-9a-zA-Z]*,? ?', '', text, flags=re.MULTILINE)
    #re.sub(r'0[=x][0-9a-zA-Z]*,? ?.*', '', start, flags=re.MULTILINE | re.DOTALL)
    if (start != text):
        print('filtered files')
    return text

def replace_name(text):
    variations = ['Jose Nazario', 'jose Nazario', 'Jose nazario', 'jose.nazario', 'jose.Nazario', 'Jose.nazario', 'Jose.Nazario', 'jose@monkey.org']
    replacement = 'Victim Name'
    for variation in variations:
        text = re.sub(variation, replacement, text, flags=re.MULTILINE)
    return text

with open('texts.csv', 'w', newline='\n') as csvfile:
    DetectorFactory.seed = 0
    csvwriter = csv.writer(csvfile, dialect='excel')
    mbox = mailbox.mbox('mbox_edited/private-phishing4.mbox')
    output = mailbox.mbox('output.mbox', create=True)
    discarded = 0
    decode_failed = 0
    error = 0
    accepted_languages = ['ca', 'en', 'uk']
    discarded_languages = []

    for key in mbox.iterkeys():
        try:
            print(key)
            res = []
            message = mbox.get_message(key)
            text = get_text(message)
            if not discard:
                text = remove_links(text)
                text = replace_name(text)
                #text = filter_non_printable(text)
                text = remove_files_in_plaintext(text)
                try:
                    language = detect(text)
                except Exception:
                    print('Can not detect language') #should only occur with messages containing no readable text
                if language in accepted_languages:
                    #text = remove_files_in_plaintext(text)
                    csvwriter.writerow([text.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')])
                else:
                    discarded_languages.append(language)
            else:
                discarded += 1
            discard = False
            mbox.flush()
        except UnicodeDecodeError:
            print('Cant decode message: ' + str(key))
            decode_failed += 1
        except Exception:
            print('Unknown error error: '  + str(key))
            error += 1

print('Done')
print('Discarded: ' + str(discarded))
print('Failed decoding: ' + str(decode_failed))
print('Not English: ' + str(len(discarded_languages)))
print('Not English: ' + str(set(discarded_languages)))
print('Unknown Error: ' + str(error))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
