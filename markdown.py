import re
import praw
import pickle
import atexit
import time
import os.path
import sys
import threading

#initial setup

r = praw.Reddit('MarkDown Fixer')
r.login("User","Pass")

pickle_file = "save.p"

subreddit = r.get_subreddit('all')
if os.path.isfile(pickle_file):
	searched = pickle.load( open( pickle_file, "rb" ))	
else:
	searched = set()


def dumpComments(): 
	"""
	On program crash or exit.
	"""

	print("HELP")
	if os.path.isfile(pickle_file): #if file exists
		os.remove(pickle_file) #deletes existing pickle file
	pickle.dump(searched, open( pickle_file, "wb" )) #dump set() with comment ids into pickle
	sys.exit()

def threadedCheck(comment): 
	"""
	Timed thread to check for ninja edits.

	Args:
		comment: Matched praw comment.
	"""

	print("Thread sleeping")
	time.sleep(60) #wait 1 minute before checking again
	print("Thread resumed")
	s = r.get_submission(comment.permalink) #Get updated comment based 
	updatedComment = s.comments[0]			#on original permalink
	
	if ")[http" in updatedComment.body.lower(): #if we match the comment again
		comment.reply("It seems you've used the wrong syntax for linking a word with reddit.\n\n Try: \[Word\]\(http://link.com) instead. :)\n\n \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- \n\n *^^I'm ^^a ^^bot* \n\n ^^^[Contact](https://www.reddit.com/message/compose/?to=bsmith0)") 
		print("Replied")
	else:
		print("Ninja-edited")


#Main loop
while True:
	try:
		sub_comments = subreddit.get_comments(limit=200) #fetch comments from r/all

		for comment in sub_comments:
			if comment.id not in searched: 
				searched.add(comment.id) #add the comment id to the log
				if ")[http" in comment.body.lower():
					print(comment.body)
					t = threading.Thread(target=threadedCheck, args=(comment,))
					t.start() #start a threaded event with a timer incase of a ninja edit

		time.sleep(2)
	except Exception,e:
		print(e)
		continue


atexit.register(dumpComments)
