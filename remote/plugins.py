import json     
from collections import defaultdict
def checkVav(gr,diff):
    env = gr._genv()
    
    env.init()
    l = env.getSensorsByType(u'VAV')
    pairs = defaultdict(tuple)
    for it in l:
        k = it.split(':')
        if pairs.has_key(k[0]):
            p1 = pairs[k[0]]
            if k[1] == 'RM STPT DIAL':
                p2 = it
            elif k[1] == 'ROOM TEMP':
                p2 = p1
                p1 = it
            else:
                continue
            pairs[k[0]] = (p1,p2)
        else:
            if k[1] in ['RM STPT DIAL','ROOM TEMP']:            
                pairs[k[0]] = (it)   
    series = []
    for it in pairs.values():
        slist = [(it[0],env.getSensorId(it[0])),(it[1],env.getSensorId(it[1]))]
        cs = gr.getSeries(slist,'')
        ex = gr.getExpression(slist,'abs({0}-{1}),abs({0}-{1})>%f'%diff,cs,False)    
        name = it[0].split(':')[0]
        dataserie = defaultdict()
        c = ex[0][1][ex[0][1]['svalue'] > diff]
        if len(c) == 0:
            continue;
        json_s = c[['stime','svalue']].to_json(orient='values')
                   
                   
        dataserie['name']=name
        dataserie['data']=json_s
        series.append(dataserie)
        if len(series) > 30:
            break
    
    return json.dumps(series)             
