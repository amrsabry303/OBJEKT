import re,sys,json
sys.argv=['x','/home/user/OBJEKT','M']
src=open('/home/user/OBJEKT/plan/faux-books/print/src/make_print.py').read().split("import os, time")[0]
exec(src)
meta=[]
for v in VOLS:
    body=re.sub(r'<line [^>]*/>','',build(v)).replace('href="../../textures/','href="file:///home/user/OBJEKT/plan/faux-books/print/textures/')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {Wf} {H}" width="{Wf*5}" height="{H*5}">{body}</svg>'
    open(f'tex/tex_{v[0]:02d}.svg','w').write(svg)
    meta.append(dict(n=v[0],title=' '.join(v[1]),W=W/10,H=H/10,D=D/10,cover=C[v[2]],px=[Wf*5,H*5],Wmm=W,Dmm=D))
json.dump(meta,open('meta.json','w')); print(len(meta),'D',D)
