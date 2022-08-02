import csv

files = ['phishing0.csv', 'phishing1.csv', 'phishing2.csv', 'phishing3.csv',
         '20051114.csv',
         'phishing-2015.csv', 'phishing-2016.csv', 'phishing-2017.csv', 'phishing-2018.csv', 'phishing-2019.csv', 'phishing-2020.csv', 'phishing-2021.csv',
         'private-phishing4.csv' ]

with open('all_filtered.csv', 'w', newline='\n') as outputfile:
    csvwriter = csv.writer(outputfile, dialect='excel')
    for file in files:
        with open('output_files/' + file, 'r', newline='\n') as csvfile:
            csvreader = csv.reader(csvfile, dialect='excel')
            for row in csvreader:
                csvwriter.writerow(row)