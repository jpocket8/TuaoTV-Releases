"""Original, deterministic illustrated problems. Diagrams contain only safe drawing primitives."""
import hashlib
import json
import math

COLOURS = {'blue', 'teal', 'gold', 'ink', 'muted', 'red', 'paper'}

def validate_visual(v):
    assert isinstance(v, dict) and isinstance(v.get('alt'), str) and 0 < len(v['alt']) <= 500
    assert isinstance(v.get('elements'), list) and 0 < len(v['elements']) <= 100
    for e in v['elements']:
        assert isinstance(e, list) and e and e[0] in ('rect','circle','line','text')
        kind=e[0]
        assert len(e)==({'rect':6,'circle':5,'line':6,'text':5}[kind])
        coords=e[1:3] if kind=='text' else e[1:-1]
        assert all(isinstance(n,(int,float)) and not isinstance(n,bool) and math.isfinite(n) and 0<=n<=600 for n in coords)
        if kind=='text':
            assert isinstance(e[3],str) and 0<len(e[3])<=80 and isinstance(e[4],int) and 12<=e[4]<=24
            assert e[2]<=280
        else:
            assert e[-1] in COLOURS
            if kind=='rect':assert e[1]+e[3]<=600 and e[2]+e[4]<=280
            if kind=='circle':assert e[3]>0 and e[1]-e[3]>=0 and e[1]+e[3]<=600 and e[2]-e[3]>=0 and e[2]+e[3]<=280
            if kind=='line':assert e[2]<=280 and e[4]<=280
    return v

def illustrated_question(year, rng, slot):
    # Each consecutive group of five covers different situations, including younger/older levels.
    topics = (['count','clock','money','bars','shape'] if year<=1 else
              ['array','clock','money','bars','ruler'] if year==2 else
              ['array','fraction','clock','bars','money'] if year==3 else
              ['rectangle','fraction','money','bars','ruler'] if year==4 else
              ['rectangle','fraction','bars','clock','volume'] if year==5 else
              ['triangle','fraction','bars','temperature','money'] if year==6 else
              ['triangle','ratio','bars','map','line'] if year==7 else
              ['speed','equation','money','bars','triangle'] if year==8 else
              ['pythagoras','line','speed','bars','rectangle'] if year==9 else
              ['line','quadratic','interest','probability','speed'])
    kind=topics[slot%len(topics)]
    a,b=rng.randint(2,10),rng.randint(2,8)
    E=[]
    def text(x,y,s,size=20):E.append(['text',x,y,str(s),size])
    def rect(x,y,w,h,c='blue'):E.append(['rect',x,y,w,h,c])
    def line(x,y,x2,y2,c='ink'):E.append(['line',x,y,x2,y2,c])
    def circle(x,y,r,c='teal'):E.append(['circle',x,y,r,c])
    if kind=='count':
        a=rng.randint(2,9);b=rng.randint(1,5)
        for n in range(a+b):
            x=65+(n%7)*75;y=90+(n//7)*90
            circle(x,y,18,'red');line(x,y-18,x+7,y-30,'teal')
        prompt=f'At the fruit stall, there are {a} apples. A delivery adds {b} more. How many apples are there now?'
        answer=a+b;why=f'Count the apples or add: {a} + {b} = {answer}.';alt=f'Two rows of apples at a fruit stall, showing {a} plus {b} apples.'
        text(30,30,'Fruit stall')
    elif kind=='shape':
        sides=rng.choice([3,4,5,6]);points=[(300+95*math.cos(-math.pi/2+2*math.pi*i/sides),145+95*math.sin(-math.pi/2+2*math.pi*i/sides)) for i in range(sides)]
        for i,(x,y) in enumerate(points):line(round(x,2),round(y,2),*map(lambda z:round(z,2),points[(i+1)%sides]),'blue')
        name={3:'triangle',4:'square',5:'pentagon',6:'hexagon'}[sides]
        prompt=f'The playground sign is a {name}. How many straight sides does it have?'
        answer=sides;why=f'Count each straight edge once. The sign has {sides} sides.';alt=f'A playground sign with {sides} straight sides.'
    elif kind=='array':
        rows=rng.randint(2,4 if year==2 else 6);cols=rng.randint(2,5 if year==2 else 8)
        for row in range(rows):
            for col in range(cols):circle(65+col*60,40+row*38,12)
        prompt=f'The school garden has {rows} rows of seedlings, with {cols} seedlings in each row. How many seedlings are there altogether?'
        answer=rows*cols;why=f'Equal rows can be multiplied: {rows} × {cols} = {answer} seedlings.';alt=f'A garden array with {rows} rows and {cols} seedlings per row.'
    elif kind=='clock':
        hour=rng.randint(1,11);minute=0 if year<=1 else rng.choice([15,30,45]);elapsed=rng.choice([15,30,45,60])
        circle(300,137,103,'paper')
        for n in range(1,13):
            ang=n*math.pi/6;text(round(300+82*math.sin(ang)-8,2),round(144-82*math.cos(ang),2),n,16)
        ang=(hour+minute/60)*math.pi/6;line(300,137,round(300+52*math.sin(ang),2),round(137-52*math.cos(ang),2))
        ang=minute*math.pi/30;line(300,137,round(300+73*math.sin(ang),2),round(137-73*math.cos(ang),2),'blue');circle(300,137,4,'ink')
        if year<=1:
            prompt=f'The classroom clock shows {hour}:00. What hour is it?';answer=hour;why=f'The long hand points to 12 and the short hand points to {hour}. It is {hour} o’clock.'
        elif year==2:
            prompt=f'The swimming lesson starts at {hour}:{minute:02d}. How many minutes past {hour} is this?';answer=minute;why=f'Each number on the clock marks 5 minutes. The minute hand shows {minute} minutes past the hour.'
        else:
            end=hour*60+minute+elapsed;endh=(end//60-1)%12+1
            prompt=f'The library visit starts at {hour}:{minute:02d} and ends at {endh}:{end%60:02d}, later the same day. How long is the visit, in minutes?';answer=elapsed;why=f'Count forward from the start to the finish: {elapsed} minutes.'
        alt=f'An analogue clock showing {hour}:{minute:02d}.'
    elif kind=='money':
        if year<=3:
            coins=[rng.choice([5,10,20,50]) for _ in range(3 if year<=1 else 5)]
            if year<=1:coins=[10]*rng.randint(2,5)
            for i,c in enumerate(coins):circle(70+i*105,130,40,'gold');text(44+i*105,138,f'{c}c')
            prompt='At the school canteen, you have coins worth '+', '.join(f'{c}c' for c in coins)+'. What is their total value in Australian cents?'
            answer=sum(coins);why='Add the coin values: '+' + '.join(map(str,coins))+f' = {answer} cents.';alt='Australian coin-value counters labelled '+', '.join(f'{c} cents' for c in coins)+'.'
        else:
            price=a*10;paid=100 if year==4 else price*2
            rect(75,60,180,130,'teal');text(95,110,'School shop');text(100,155,f'A${price}')
            if year>=6:
                discount=rng.choice([10,20,30]);text(335,120,f'{discount}% off')
                prompt=f'A school bag is marked A${price}, with {discount}% off. What is the sale price in Australian dollars?';answer=price*(100-discount)//100;why=f'Pay {100-discount}% of A${price}: {price} × {100-discount}/100 = A${answer}.'
            else:
                text(335,120,f'Paid: A${paid}');prompt=f'A school kit costs A${price}. You pay A${paid}. How much change do you get, in Australian dollars?';answer=paid-price;why=f'Change = amount paid − price = {paid} − {price} = A${answer}.'
            alt='A school-shop price tag and '+('discount notice.' if year>=6 else 'amount paid.')
    elif kind=='bars':
        values=rng.sample(range(2,11 if year<=2 else 31),3)
        if year in (5,8):values[2]+=(-sum(values))%3
        setting=rng.choice(['Recycling station','Class library','School garden','Sports day','Beach cleanup','Pet shelter','Fruit stall','Art cupboard'])
        text(75,22,setting,16)
        labels=['Mon','Tue','Wed'];scale=150/max(values)
        line(55,220,555,220);line(55,35,55,220)
        for i,v in enumerate(values):
            h=round(v*scale,2);rect(100+i*155,220-h,75,h,['blue','teal','gold'][i]);text(120+i*155,210-h,v,18);text(105+i*155,250,labels[i],18)
        data=', '.join(f'{label} {v}' for label,v in zip(labels,values))
        if year<=2:task='largest daily total';answer=max(values);why=f'Compare the bar heights and labels. The largest total is {answer}.'
        elif year==3:task='total over all three days';answer=sum(values);why=f'Add the totals: {values[0]} + {values[1]} + {values[2]} = {answer}.'
        elif year in (5,8):task='mean number per day';answer=sum(values)//3;why=f'Mean = sum ÷ 3 = {sum(values)} ÷ 3 = {answer}.'
        elif year==6:task='median daily total';answer=sorted(values)[1];why=f'In order the totals are {sorted(values)}. The middle value is {answer}.'
        else:task='difference between the largest and smallest daily totals';answer=max(values)-min(values);why=f'Subtract the smallest total from the largest: {max(values)} − {min(values)} = {answer}.'
        prompt=f'The {setting.lower()} chart shows items counted: {data}. What is the {task}?';alt=f'A labelled bar chart at the {setting.lower()}: {data}.'
    elif kind=='fraction':
        denominator=rng.choice([4,8] if year<=4 else [4,5,10]);numerator=rng.randint(1,denominator-1);total=denominator*a
        for i in range(denominator):rect(40+i*520/denominator,80,520/denominator-3,80,'teal' if i<numerator else 'muted')
        text(50,210,f'Total: {total} seedlings')
        prompt=f'A garden bed has {total} seedlings. {numerator}/{denominator} are herbs, shown by the green equal parts. How many seedlings are herbs?';answer=a*numerator;why=f'One equal part has {total} ÷ {denominator} = {a} seedlings. Take {numerator} parts: {a} × {numerator} = {answer}.';alt=f'A bar divided into {denominator} equal parts, with {numerator} shaded green. The whole represents {total} seedlings.'
    elif kind in ('rectangle','quadratic'):
        rect(160,65,280,140,'teal');text(235,45,f'{a} m' if kind=='rectangle' else 'side = x m');text(455,145,f'{b} m' if kind=='rectangle' else 'x m')
        if kind=='quadratic':text(195,140,f'Area = {a*a} m²');prompt=f'A square courtyard has area {a*a} m². What is its positive side length x, in metres?';answer=a;why=f'For a square, x² = {a*a}. The positive square root is {a} m.'
        elif year==4 and rng.choice([True,False]):prompt=f'A rectangular veggie garden is {a} m long and {b} m wide. How many metres of fence are needed around all four sides?';answer=2*(a+b);why=f'Perimeter = 2 × ({a} + {b}) = {answer} m.'
        else:prompt=f'A rectangular veggie garden is {a} m long and {b} m wide. What is its area in square metres?';answer=a*b;why=f'Area = length × width = {a} × {b} = {answer} m².'
        alt='A labelled garden rectangle.' if kind=='rectangle' else f'A square courtyard with area {a*a} square metres and unknown side x.'
        text(25,265,'Diagram not to scale',14)
    elif kind=='ruler':
        start=rng.randint(0,4);length=rng.randint(2,7);rect(40,170,520,45,'gold')
        for i in range(13):line(45+i*42,170,45+i*42,185);text(40+i*42,207,i,14)
        rect(45+start*42,95,length*42,36,'blue');text(50,65,'Pencil length (cm)')
        prompt=f'A pencil starts at {start} cm and ends at {start+length} cm on a ruler. What is its length in centimetres?';answer=length;why=f'Subtract the start reading from the end reading: {start+length} − {start} = {length} cm.';alt=f'A pencil above a centimetre ruler from {start} to {start+length} cm.'
    elif kind=='volume':
        rect(130,100,280,115,'blue');line(130,100,200,55);line(410,100,480,55);line(200,55,480,55);line(480,55,480,170);line(410,215,480,170)
        text(220,245,f'{a} cm');text(450,215,f'{b} cm');text(50,160,'2 cm');text(25,30,'Storage box · not to scale',18)
        prompt=f'A classroom storage box is a rectangular prism, {a} cm long, {b} cm wide and 2 cm high. What is its volume in cubic centimetres?';answer=a*b*2;why=f'Volume = length × width × height = {a} × {b} × 2 = {answer} cm³.';alt=f'A rectangular storage box labelled {a} cm by {b} cm by 2 cm.'
    elif kind in ('triangle','pythagoras'):
        line(140,220,460,220,'blue');line(140,220,140,55,'blue');line(140,55,460,220,'blue');line(140,205,155,205);line(155,205,155,220)
        if kind=='pythagoras':text(60,140,f'{a*3} cm');text(240,250,f'{a*4} cm');text(310,120,'? cm');prompt=f'A right-angled shade sail has perpendicular sides {a*3} cm and {a*4} cm. How long is its hypotenuse, in centimetres?';answer=a*5;why=f'Pythagoras: c² = {a*3}² + {a*4}² = {25*a*a}, so c = {answer} cm.'
        elif year==6:text(60,140,f'{b} m');text(240,250,f'{a*2} m');prompt=f'A right-triangular garden has base {a*2} m and perpendicular height {b} m. What is its area in square metres?';answer=a*b;why=f'Area = base × height ÷ 2 = {a*2} × {b} ÷ 2 = {answer} m².'
        else:
            angle=rng.choice([25,30,35,40,50,55,60]);text(165,100,f'{angle}°');text(350,205,'?°');prompt=f'A right-angled ramp triangle has angles of 90° and {angle}°. What is the third angle, in degrees?';answer=90-angle;why=f'Triangle angles total 180°: 180 − 90 − {angle} = {answer}°.'
        text(25,28,'Diagram not to scale',14);alt='A right triangle with perpendicular sides and the known measurements labelled.'
    elif kind in ('speed','map'):
        distance=a*b*(10 if kind=='speed' else 1);line(80,145,515,145,'blue');circle(80,145,12);circle(515,145,12,'gold');text(50,110,'School');text(445,110,'Museum');text(220,85,f'{distance} km' if kind=='speed' else f'{a} cm on map');text(180,205,f'{b} hours' if kind=='speed' else f'1 cm = {b} km')
        if kind=='speed':prompt=f'A bus travels {distance} km from school to a museum in {b} hours. What is its average speed in km/h?';answer=distance//b;why=f'Average speed = distance ÷ time = {distance} ÷ {b} = {answer} km/h.'
        else:prompt=f'A map shows school and a museum {a} cm apart. The scale is 1 cm to {b} km. What real distance does this represent, in kilometres?';answer=a*b;why=f'Multiply map distance by the scale: {a} × {b} = {answer} km.'
        alt='A school-to-museum route with its distance and '+('travel time.' if kind=='speed' else 'map scale.')
    elif kind=='line':
        slope=rng.randint(-4,5);x1=rng.randint(0,4);y1=rng.randint(0,8);dx=rng.randint(1,4);x2=x1+dx;y2=y1+slope*dx
        ya=145 if slope==0 else (185 if slope>0 else 75);yb=145 if slope==0 else (75 if slope>0 else 185)
        line(75,225,555,225);line(75,225,75,30);line(140,ya,470,yb,'blue')
        circle(140,ya,6);circle(470,yb,6)
        text(95,ya+40,f'A ({x1}, {y1})',18);text(365,yb-25,f'B ({x2}, {y2})',18);text(25,20,'x-y graph · schematic, use labelled coordinates',16)
        prompt=f'A straight-line graph passes through A({x1}, {y1}) and B({x2}, {y2}). What is its gradient?';answer=slope;why=f'Gradient = change in y ÷ change in x = ({y2} − {y1}) ÷ ({x2} − {x1}) = {slope}.';alt=f'A schematic straight line joining labelled points A({x1}, {y1}) and B({x2}, {y2}); use coordinates, not drawn lengths.'
    elif kind=='ratio':
        text(30,35,'Sports-day drink mix')
        for i in range(b+1):rect(45+i*58,80,40,110,'gold' if i==0 else 'blue')
        text(40,240,f'Juice : water = 1 : {b}')
        prompt=f'A sports-day drink uses juice and water in the ratio 1:{b}. For {a} litres of juice, how many litres of water are needed?';answer=a*b;why=f'Each litre of juice needs {b} litres of water: {a} × {b} = {answer} litres.';alt=f'One yellow juice container for every {b} blue water containers.'
    elif kind=='temperature':
        low=-a;rise=a+b;line(300,55,300,230,'muted')
        for i,t in enumerate([low,0,b]):y=210-i*75;line(280,y,320,y);text(335,y+6,f'{t}°C')
        line(250,210,250,60,'red');text(35,125,f'Rise: {rise}°C')
        prompt=f'At a mountain campsite it is {low}°C. The temperature rises by {rise}°C. What is the new temperature in degrees Celsius?';answer=b;why=f'Add the rise to the starting temperature: {low} + {rise} = {b}°C.';alt=f'A schematic temperature scale showing a rise from {low}°C through zero.'
    elif kind=='equation':
        for i in range(b):rect(35+i*60,65,48,48,'blue');text(48+i*60,98,'x')
        text(40,170,f'+ {a}');text(300,230,f'Total: {a+b*a} tokens')
        prompt=f'{b} equal boxes each hold x tokens, with {a} extra tokens. There are {a+b*a} tokens altogether. What is x?';answer=a;why=f'Remove the extras, then divide equally: ({a+b*a} − {a}) ÷ {b} = {a}.';alt=f'{b} equal boxes labelled x with {a} extra tokens and a total of {a+b*a}.'
    elif kind=='interest':
        principal=a*1000;line(70,145,530,145,'blue')
        for i,label in enumerate(['Now','Year 1','Year 2']):circle(70+i*230,145,8);text(30+i*230,195,label,18)
        text(30,85,f'A${principal}');text(185,45,'10% per year, compounded annually',18)
        prompt=f'A${principal} is saved at 10% compound interest per year. What is the balance after 2 years, in Australian dollars?';answer=a*1210;why=f'Apply the growth factor twice: {principal} × 1.1 × 1.1 = A${answer}.';alt=f'A savings timeline from now to year 2 with an initial A${principal} and annual compound interest of 10%.'
    elif kind=='probability':
        coins=rng.randint(3,7)
        for i in range(coins):circle(55+i*78,125,29,'gold');text(38+i*78,133,'H/T',16)
        prompt=f'{coins} fair coins are tossed independently. How many equally likely sequences of heads and tails are possible?';answer=2**coins;why=f'Each coin has 2 outcomes. Multiply across all {coins} independent tosses: 2^{coins} = {answer}.';alt=f'{coins} coin counters each labelled H/T for heads or tails.'
    else:raise ValueError(kind)
    visual=validate_visual(dict(alt=alt,elements=E))
    identity=hashlib.sha256(json.dumps([year,kind,prompt,visual],sort_keys=True).encode()).hexdigest()[:24]
    choices={answer}
    while len(choices)<4:
        v=answer+rng.choice([-1,1])*rng.randint(1,max(3,abs(answer)//3))
        if v>=0 or kind in ('temperature','line'):choices.add(v)
    choices=sorted(choices);rng.shuffle(choices)
    visual_prompt = None
    if kind=='clock' and year<=1:visual_prompt='Read the classroom clock. What hour is it?'
    elif kind=='clock' and year==2:visual_prompt='Read the clock. How many minutes past the hour does it show?'
    elif kind=='ruler':visual_prompt='Use the ruler to find the pencil’s length, in centimetres.'
    elif kind=='money' and year<=3:visual_prompt='What is the total value of these coins, in Australian cents?'
    elif kind=='bars':visual_prompt=f'Study the chart. What is the {task}?'
    elif kind=='shape':visual_prompt='Look at the playground sign. How many straight sides does it have?'
    elif kind=='array':visual_prompt='Count the equal rows of seedlings. How many seedlings are there altogether?'
    result=dict(id='math-v1-'+identity,year=year,subject='math',topic=kind,prompt=prompt,options=list(map(str,choices)),answer=choices.index(answer),explanation=why,visual=visual)
    if visual_prompt:result['visualPrompt']=visual_prompt
    return result
