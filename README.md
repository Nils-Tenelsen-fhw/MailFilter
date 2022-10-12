Program used to clean up the data of the Nazario Phishing Corpus (https://monkey.org/~jose/phishing/) for use in training neural networks.

The original data from the corpus can be found in the mbox_originals folder.
A slightly altered version of the data that is used by this program, as a handful of emails with encoding issues were removed, can be found in the mbox_edited folder.
The output_files folder contains the cleaned up output generated by the program. With an individual .csv file for each respective .mbox file of the corpus.
A concatenated version of the entirety of the cleaned up data can be found in the root directory under the name all_mails.csv. This file was used as input data for the training processes of the networks found in the other repositories.

The program reads the HTML payload from the emails and converts the HTML to plaintext.
It also removes links and replaces them with placeholders. Both to protect from malware as well as to make the training process easier.
Other filtering steps include formatting as well as removal of as much non-natural language left after the plaintext conversion as possible.
