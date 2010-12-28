#!/usr/bin/env python 
class Parser:
	def __init__(self):
		pass
	def parse(self,data):
		data=BeautifulSoup(data)
		title=''
		contents=''
		try:
			title=data.title.string
			contents=re.sub('\n','\\\\n',self.extract_strings(data.body))
		except Exception,e:
			#todo: log exceptions
			print e
			pass
		return title,contents
	def extract_strings(self,elem):
		contents=''
		if isinstance(elem, Tag):
			contents+=''.join(map(self.extract_strings,elem.contents))
			return contents
		else:
			return elem