import re
import praw
import pickle
import atexit
import time
import os.path
import sys


		
def dumpComments():
	print("HELP")
	os.remove(pickle_file)
	pickle.dump(searched, open( pickle_file, "wb" ))
	sys.exit()


r = praw.Reddit('MarkDown Fixer')#all_comments = r.get_comments('all')
r.login("USER","PASS")

pickle_file = "save.p"

subreddit = r.get_subreddit('all')
if os.path.isfile(pickle_file):
	searched = pickle.load( open( pickle_file, "rb" ))	
else:
	searched = set()

while True:
	try:
		sub_comments = subreddit.get_comments(limit=200)
		for comment in sub_comments:
			if comment.id not in searched:
				searched.add(comment.id)
				if ")[http" in comment.body.lower():
					print(comment.body)
					comment.reply("It seems you've used the wrong syntax for linking a word with reddit.\n\n Try: \[Word\]\(http://link.com) instead. :)\n\n \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- \n\n *^^I'm ^^a ^^bot* \n\n ^^^[Contact](https://www.reddit.com/message/compose/?to=bsmith0)")

		time.sleep(2)
	except Exception,e:
		print(e)
		#dumpComments()


atexit.register(dumpComments)
