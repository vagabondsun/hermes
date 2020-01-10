"""
lookup module

currently only does glossary, may do other things in future

"""

import cfg #to enable referring to variables in cfg with the namespace prefix
from cfg import * #to enable calling things imported in cfg /without/ the namespace prefix
from itertools import islice

@cfg.bot.command()
async def define(ctx, *, lookup=None):

	online = True #definition is assumed to come from the site unless there is a failure to connect
	
	#removes whitespace from queries, so things like 'alter human' and 'other kin' are still recognized
	lookup = ''.join(lookup.split())
	
	try:
		html_doc = cfg.urllib.request.urlopen("http://alt-h.net/_assets/pageraws/glossaryRAW.php")
		doc = BeautifulSoup(html_doc, 'html5lib')    
		print("site glossary ok")
	except:
		with open('glossaryRAW.php', 'r') as html_doc:
			doc = BeautifulSoup(html_doc, 'html5lib')
		online = False
		print("could not connect to site - serving definition from local copy")
		
	result = doc.find(class_=lookup)      
	print("searching glossary for " + lookup)

	if (result == None):
		await ctx.send("No such glossary entry exists!")
		
	else:

		entryTitle = result.find("h3").text
		try:
			entryAlts = result.find("i").text
			entryAlts = " _(" + entryAlts + ")_ "
		except:
			entryAlts = ""
		entryText = " ".join(str(i) for i in result.find(class_="definition").contents) #joining the list of chunks of text - we do this so the bold tags are preserved as part of the string
		print(entryText)
		regex = re.compile(r"(</*b>)") #matches both <b> and </b>
		entryText = re.sub(regex, '`', entryText) #replaces them with the discord markdown for bolding
		entryLinks = result.find_all("a")
		print (entryLinks)
		
		await ctx.send("<:spellbook:563708089379848192> From the Alt+H Glossary:\n**" + entryTitle + "** " + entryAlts + ":\n" + entryText)
		if entryLinks:
			await ctx.send("\n<:globe:563708281546211328> Additional info:")
			for link in entryLinks:
				await ctx.send("_" + link.text + "_ - <" + link.get('href') + ">")
				
		if not online:
			await ctx.send("<:exclamation_mark_red:534138087828226081> Hermes could not connect to the Alt+H website. This definition is served from a local copy of the glossary and might not be as up-to-date.")