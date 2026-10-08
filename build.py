import fitz,json,re,pathlib,shutil
root=pathlib.Path(__file__).parent
p=fitz.open(root/'dist/book.pdf')
toc=p.get_toc(); chapters=[(x[1].replace('\r',' '),x[2]) for x in toc if x[0]==1 and x[1].lower().startswith('chapter')]
chapters=[('Предисловие и оглавление',6)]+chapters+[('References',788),('Index',850)]
lessons=[]
for ci,(title,start) in enumerate(chapters):
 end=chapters[ci+1][1]-1 if ci+1<len(chapters) else len(p)
 for a in range(start,end+1,2):
  b=min(a+1,end);pages=[]
  for pn in range(a,b+1):
   t=p[pn-1].get_text().replace('\u00ad\n','').replace('\u00ad','').replace('\u200b','')
   t=re.sub(r'(?<=\w)-\n(?=[a-z])','',t)
   paragraphs=[];buf=[]
   for line in t.splitlines():
    line=line.strip()
    if not line:
     if buf: paragraphs.append(' '.join(buf));buf=[]
    elif len(line)<48 and not line.endswith((',', ';')):
     if buf:paragraphs.append(' '.join(buf));buf=[]
     paragraphs.append(line)
    else:buf.append(line)
   if buf:paragraphs.append(' '.join(buf))
   pages.append({'page':pn,'text':paragraphs})
  topics=[x[1].replace('\r',' ') for x in toc if x[0] in [2,3] and a<=x[2]<=b]
  lessons.append({'chapter':ci,'title':title,'start':a,'end':b,'topics':topics,'pages':pages})
data={'chapters':[x[0] for x in chapters],'lessons':lessons}
(root/'data.json').write_text(json.dumps(data,ensure_ascii=False))
html=(root/'template.html').read_text().replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
(root/'dist/index.html').write_text(html)
print(len(lessons),'lessons',len(p),'pages')
