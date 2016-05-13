import re
import praw
import pickle
import atexit
import time
import os.path
import sys
import threading
import OAuth2Util

#initial setup

r = praw.Reddit('MarkDown Fixer')
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

pickle_file = "save.p"

subreddit = r.get_subreddit('all')

reply_text = "It seems you've used the wrong syntax for linking a word with reddit.\n\n Try: \[Word\]\(http://link.com) instead. :)\n\n \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- \n\n *^^I'm ^^a ^^bot* \n\n ^^^[Contact](https://www.reddit.com/message/compose/?to=bsmith0) \n \n ^^^If you made the mistake, fix your own comment, then reply to this: \"fixed\" and it will delete this"

match_pattern = ")[http"

if os.path.isfile(pickle_file):
	searched = pickle.load(open(pickle_file, "rb"))	
else:
	searched = set()


def dumpComments(): 
	"""
	Save comment ID's in a pickle on graceful crash or exit
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
	r._use_oauth = False
	s = r.get_submission(comment.permalink) #Get updated comment based 
	updatedComment = s.comments[0]			#on original permalink
	if len(s.comments) >= 1: #Making sure comment exists
		updatedComment = s.comments[0]
		if ")[http" in updatedComment.body.lower(): #if we match the comment again
			comment.reply(reply_text)
			print("Replied")
		else:
			print("Ninja-edited")
	else:
		print("Deleted")
	r._use_oauth = True
def checkInbox():
	"""
	Check inbox for replies which contain "fixed" from the author of the mistake
	and delete our own comment
	"""

	for message in r.get_unread(limit=None):
		message.mark_as_read()

		if message.author is not None and "fixed" in message.body.lower() and returnParent(message) is not False:
		#if the user's page exists and "fixed" is in the comment and the parent is a comment
			original_author = message.author.name #store reply's author
			parent_comment = returnParent(message)

			if parent_comment.author is not None and parent_comment.author.name == r.user.name and returnParent(parent_comment) is not False:
			#verify parent comment's author is valid and the same as the oauthed user - "MarkdownFixer"
				grandparent_comment = returnParent(parent_comment)

				if grandparent_comment.author is not None and grandparent_comment.author.name == original_author and match_pattern not in parent_comment.body:
				#verify that the grandparent comment was written by the user who made the mistake and it has been fixed
					parent_comment.delete()
					print("Deleted")
		
def returnParent(comment):
	"""
	Get the the parent comment of a given comment if the has the parent_id attribute
	(Parent is not a submission or PM)

	Args:
		comment: praw comment object to find the parent of

	Returns:
		parent_object: the parent comment of the arg
		False: only if the parent is not another comment
	"""

	parent_object = r.get_info(thing_id=comment.parent_id)
	if hasattr(parent_object, 'parent_id') and comment.is_root is False:
		return(parent_object)
	else:
		return(False)

loops = 0
#Main loop
while True:
	try:
		sub_comments = subreddit.get_comments(limit=200) #fetch comments from r/all
		for comment in sub_comments:
			if comment.id not in searched: 
				searched.add(comment.id) #add the comment id to the log
				if match_pattern in comment.body.lower():
					print(comment.body)
					t = threading.Thread(target=threadedCheck, args=(comment,))			
					t.start() #Start a threaded event with a timer incase of a ninja edit
		loops+=1
		if loops>60: #Check inbox every minute
			checkInbox()
			loops=0
		time.sleep(1)
	except Exception,e: #Catch exceptions to keep bot online even if reddit is down
		print(e)
		continue


atexit.register(dumpComments)
