# Messanger-Analysis

A small program to do simple analysis on facebook messenger data and list/graph outputs.

Runs in python3

## Downloading your Facebook Messenger history

https://www.facebook.com/help/1701730696756992?helpref=hc_global_nav

Note that you can download a lot more than just your messenger history, but this program only works on facebook messages.


## Setup

Download your facebook messenger history as explained in the section above.

Unpack the history into the folder containing the `analyze-messages.py` file.  Make sure you have the `inbox` directory the same level as the file, or you will need to manually set the path for the files.

Install the requirements using
`pip3 install -r requirements.txt`

## Running

Basic Run:
`python3 analyze-messages.py <your facebook name>`

There are also a number of options:

| Option |      Long-form      | Description                                                                                                                                                                                   |
|:------:|:-------------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -h     | --help              | Display help message                                                                                                                                                                          |
| -p     | --path              | Relative or absolute path to the location of the conversation folders. Default "./inbox"                                                                                                      |
| -i     | --include-threshold | The smallest number of total messages in a conversation for a conversation to be counted. Default 100                                                                                         |
| -s     | --sort-mode         | How to sort the messages.  Options: 'total', 'num_words', 'oldest', 'imgur'. Default "total"                                                                                               |
| -t     | --top-people        | The top number of people people to display.  Default 5                                                                                                                                        |
| -f     | --filter            | List of names, separated by comma, for the program to filter to. If not provided, will do no filtering.  If a given name does not exist, will still filter, but will do nothing for that name |
| -so    | --summary-only      | Print only summary information in command-line.  Do not display graphs                                                                                                                        |
| -ph    | --print-history     | Print the messaging history per month                                                                                                                                                         |
| -w     | --word-count        | Display analysis with word-count in addition to total messages                                                                                                                                |
| -b     | --bar-mode          | How to display the bars in the history graph. Options: 'group', 'stack'. Default "group"                                                                                                      |
| -rg    | --relative-graphs   | Display the relative-percent graphs as well (kinda ugly if done with more than 3-4 people)                                                                                                    |

## Examples

I've included two anonymized conversations as examples so that the program will run out of the box.


## Testing

There are currently no tests for the program

### Anonymization

I've included a script that can anonymize a messenger conversation.  The script is `anonymize.py`.  It takes three arguments: the file's location, the person running's name, and the other person's name.

It removes all instances of names from the file and lorem-ipsum-ifies the message contents while preserving the word-count.

Note that I've only run it on the two example conversations, so it might not fully anonymize all messages.

### Plotly

The script relies on plotly to generate its graphs.  Please see plotly documentation for more info on plotly.

https://plot.ly/python/

https://plot.ly/python/static-image-export/
