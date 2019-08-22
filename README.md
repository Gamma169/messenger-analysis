# Messanger-Analysis

A small program to do simple analysis on facebook messenger data and list/graph outputs.

Runs in python3

## Downloading your Facebook Messenger history

https://www.facebook.com/help/1701730696756992?helpref=hc_global_nav

Note that you can download a lot more than just your messenger history, but this program only works on messenger for now


## Running

Download your facebook messenger history as explained in the section above.

Unpack the history into the folder containing the `analyze-messages.py` file

Run the file:
`python3 analyze-messages.py`



## Examples

I've included two anonymized conversations as examples so that the program will run out of the box.


## Testing

There is currently no tests on the program

### Anonymization

I've included a script that can anonymize a messenger conversation.  The script is `anonymize.py`.  It takes three arguments: the file's location, the person running's name, and the other person's name.

It removes all instances of names from the file and lorem-ipsum-ifies the message contents while preserving the word-count.

Note that I've only run it on the two example conversations, so it might not fully anonymize all messages.

### Plotly

The script relies on plotly to generate its graphs.  Please see plotly documentation for more info on plotly.

https://plot.ly/python/

https://plot.ly/python/static-image-export/