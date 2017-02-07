import os
import time
from slackclient import SlackClient
import random
import subprocess

# starterbot's ID as an environment variable
BOT_ID = "U3CDG0XA4"

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
FIRING = "FIRING"
RESOLVED = "RESOLVED"
SCALE = "scale"

# instantiate Slack & Twilio clients
slack_client = SlackClient("xoxb-114458031344-eaLoiHJNKxIQnRSRWCvPiyhO")


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    random_notes = ["O degil de bi Ilhan Irem vardi, o ne oldu? :thinking_face:",
                    "Onu bilmem de dolar cok artti :cry:",
                    "Ne diyosun haci? :unamused:",
                    "Seni bir anlasam, neler diyecegim neler... :unamused:",
                    "Seni anlamiyorum. 'Insanlarla anlasmak zordur'' demislerdi... :unamused:",
                    "Ben bot'um, yapabileceklerim kisitli... :unamused:",
                    "Bunu anlamadim ama high load olursa soylerim... :hand::skin-tone-4:",
                    ":headphones: 'rayrayray raaay...' :headphones: neee?!! Duymuyorum seni!!"]
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."

    print ("handle_command'deki command: ", command)

    if command.startswith(EXAMPLE_COMMAND):
        # response = "Sure...write some more code then I can do that!"
        response = "Ne yapayim abime? :smirk:"
    elif command.startswith(SCALE):
        response = "Scale bizim isimiz. :smirk: Vakti gelsin, scale'im."
        print ("command for scaling: ", command)
    elif "adin" in command or "ismin" in command:
        print ("adin veya ismin geldi")
        response = "Benim adim GoreTex Bot, cunku su gecirmez bot'um! :bowtie:"
    elif "kullanima" in command or "devreye" in command:
        print ("kullanima veya devreye geldi")
        response = "Pazartesi gelip baslayayim mi abi?"
    elif "catalog" in command:
        print ("F1")
        response = "Yaniyosun Fuat abiii! :smiley:"
    else:
        print ("RND1")
        response = random.choice(random_notes)

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            print ("output --> ", output)
            if output and 'text' in output and AT_BOT in output['text']:
                print ("output --> ", output)
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
            if output and 'text' in output and "attachments" in output and 'text' in output['attachments'][0]:
                if "foundation" in output['attachments'][0]['text'] or "aggregation" in output['attachments'][0]['text']:
                    service = output['attachments'][0]['text'].split()[0]
                    subprocess.call(
                        "docker ps --filter 'label=traefik.backend={0}' "
                        "| wc -l | xargs -I % docker-compose scale {0}=%"
                        .format(service),
                        shell=True)
                    return output['text'].split(), output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
