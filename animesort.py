import requests
import json
import threading
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os
import sys

year = 2020
season = 2
mainlandonly = False

if not os.path.exists('animelist'+str(year)+'s'+str(season)+'.json'):
    animelist = json.loads(requests.get('https://api.bilibili.com/pgc/season/index/result?season_month='+str((season-1)*3+1)+'&year=['+str(year)+','+str(year+1)+')&page=1&season_type=1&pagesize=50&type=1').text)['data']['list']

    def getstyles(i):
        animeinfo = json.loads(requests.get('https://api.bilibili.com/pgc/view/web/media?media_id='+str(animelist[i]['media_id'])).text)
        animelist[i]['styles'] = animeinfo['result']['styles']
        print(animelist[i]['title'])

    threads = [threading.Thread(target=getstyles,args=[i]) for i in range(len(animelist))]

    for i in threads:
        i.start()

    for i in threads:
        i.join()

    with open('animelist'+str(year)+'s'+str(season)+'.json','w') as a:
        json.dump(animelist,a)
else:
    with open('animelist'+str(year)+'s'+str(season)+'.json','r') as a:
        animelist = json.loads(a.read())

if os.path.exists('stylesoffset.json'):
    styles = json.load(open('stylesoffset.json','r'))
else:
    print('未发现 stylesoffset.json ，已创建，请修改offset到自己满意的数值后再运行此脚本')
    styles = []
    for i in range(1,5):
        styles = styles+[y for y in [x for x in json.loads(requests.get('https://api.bilibili.com/pgc/season/index/condition?season_type='+str(i)+'&type=1').text)['data']['filter'] if x['field'] == 'style_id'][0]['values'] if y not in styles]
    styles.sort(key=lambda z: z['keyword'])
    for i in styles:
        i['offset'] = 0
    open('stylesoffset.json','w').write(json.dumps(styles,indent=4,ensure_ascii=False))
    sys.exit()

if mainlandonly :
    animelist = [i for i in animelist if '（僅限' not in i['title'] and i['title'][-3:] != '地區）']

for i in animelist:
    i['offset'] = 0
    for j in i['styles']:
        j['offset'] = [x['offset'] for x in styles if int(x['keyword']) == j['id']][0]
        i['offset'] = i['offset']+[x['offset'] for x in styles if int(x['keyword']) == j['id']][0]

allstylesid = []
[[allstylesid.append(y['id']) for y in x['styles'] if y['offset'] != 0] for x in animelist]
allstylesid = list(set(allstylesid))

animelist.sort(key=lambda x:x['offset'])

font = FontProperties(fname='/system/fonts/NotoSansCJK-Regular.ttc',size=14)
barh = plt.figure(figsize=(20,20))
leftp = [0]*len(animelist)
leftn = [0]*len(animelist)


def emptyreturn0(a,i):
    if int(i['keyword']) in [y['id'] for y in a['styles']]:
        for z in a['styles']:
            if z['id'] == int(i['keyword']):
                return z['offset']
    else:
        return 0


for i in styles:
    if i['offset'] > 0 and int(i['keyword']) in allstylesid:
        plt.barh([x['title'] for x in animelist],[emptyreturn0(a,i) for a in animelist],left=leftp)
        for j in range(len(animelist)):
            if int(i['keyword']) in [x['id'] for x in animelist[j]['styles']]:
                plt.text(leftp[j]+1,j,i['name'],FontProperties=font,ha='right',va='center')
        leftp = [leftp[j] + [emptyreturn0(a,i) for a in animelist][j] for j in range(len(animelist))]
    if i['offset'] < 0 and int(i['keyword']) in allstylesid:
        plt.barh([x['title'] for x in animelist],[emptyreturn0(a,i) for a in animelist],left=leftn)
        for j in range(len(animelist)):
            if int(i['keyword']) in [x['id'] for x in animelist[j]['styles']]:
                plt.text(leftn[j]-1,j,i['name'],FontProperties=font,va='center')
        leftn = [leftn[j] + [emptyreturn0(a,i) for a in animelist][j] for j in range(len(animelist))]
plt.tick_params(labelleft=False,left=False)
for i in barh.get_axes()[0].get_xticklabels():
    i.set_fontproperties(font)
for i in range(len(animelist)):
    plt.text(0,i,animelist[i]['title'],ha='center',va='center',FontProperties=font)
plt.savefig('/sdcard/adm/animelist'+str(year)+'s'+str(season)+'.png')
