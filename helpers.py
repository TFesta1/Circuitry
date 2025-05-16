
# Import tool to copy text on clipboard
import pyperclip
def getVideoTimeStamp(url, time):
    minutes = int(time.split(":")[0])
    seconds = int(time.split(":")[1])
    return fr"{url}&t={minutes*60 + seconds}s"

url = "https://www.youtube.com/watch?v=8q8kU-6-4DM"


time = "4:41"
# Copy the timestamp to clipboard
pyperclip.copy(getVideoTimeStamp(url, time))
