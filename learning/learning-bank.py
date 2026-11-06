#!/usr/bin/env python3
"""Original practice questions, reproducible and checked before publication; no paid API."""
import argparse
import hashlib
import json
import random
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

START = date(2026, 11, 6)
SOURCE = 'https://www.qcaa.qld.edu.au/p-10/aciq/version-9/learning-areas/p-10-mathematics'

def question(year, rng):
    a, b = rng.randint(2, 12), rng.randint(2, 9)
    topic = rng.randrange(5)
    if year == 0:
        a, b = rng.randint(1, 10), rng.randint(1, 5)
        if topic == 0: text, answer, why = f'数数 Counting：有 {a} 只考拉，又来了 {b} 只，一共有几只？', a+b, f'从 {a} 接着数 {b} 个，共 {a+b} 只。'
        elif topic == 1: text, answer, why = f'比较大小 Compare：{a} 和 {a+b} 哪一个更大？', a+b, f'{a+b} 比 {a} 多 {b}，所以更大。'
        elif topic == 2: text, answer, why = f'数序 Counting：{a}、{a+1}、{a+2}，下一个数是几？', a+3, f'每次数多 1：{a+2} 后面是 {a+3}。'
        else: text, answer, why = f'拿走 Take away：{a+b} 个贝壳拿走 {b} 个，还剩几个？', a, f'{a+b} − {b} = {a}。'
    elif year == 1:
        a, b = rng.randint(1, 9), rng.randint(1, 9)
        if topic == 0: text, answer, why = f'加法 Addition：{a} + {b} = ？', a+b, f'把两组合起来：{a} + {b} = {a+b}。'
        elif topic == 1: text, answer, why = f'减法 Subtraction：{a+b} − {b} = ？', a, f'从 {a+b} 减去 {b}，剩下 {a}。'
        elif topic == 2: text, answer, why = f'位值 Place value：{a*10+b} 有几个十？', a, f'{a*10+b} = {a} 个十加 {b} 个一。'
        else: text, answer, why = f'平均分 Sharing：{a*2} 颗葡萄平均分给2人，每人几颗？', a, f'把 {a*2} 分成两组，每组 {a}。'
    elif year == 2:
        if topic == 0: text, answer, why = f'加法 Addition：{a*5} + {b} = ？', a*5+b, f'先算整十再加个位，{a*5} + {b} = {a*5+b}。'
        elif topic == 1: text, answer, why = f'等组 Equal groups：{b} 组，每组5个，一共有几个？', b*5, f'每组5个，{b} × 5 = {b*5}。'
        elif topic == 2: text, answer, why = f'钱币 Money：{a} 枚10澳分硬币共多少澳分？', a*10, f'{a} × 10 = {a*10} 澳分。'
        else: text, answer, why = f'跳数 Skip counting：{a*2}、{a*2+2}、{a*2+4}，下一个数是？', a*2+6, '每次增加2，所以再加2。'
    elif year == 3:
        if topic == 0: text, answer, why = f'乘法 Multiplication：{a} × {b} = ？', a*b, f'{a} 组 {b}，合计 {a*b}。'
        elif topic == 1: text, answer, why = f'除法 Division：{a*b} ÷ {b} = ？', a, f'因为 {a} × {b} = {a*b}，所以商为 {a}。'
        elif topic == 2: text, answer, why = f'单位 Length：{a} 米等于多少厘米？', a*100, f'1米 = 100厘米，所以 {a} × 100 = {a*100}。'
        else: text, answer, why = f'分数 Fraction：{a*4} 个草莓的四分之一是几个？', a, f'四分之一表示平均分成4份取1份：{a*4} ÷ 4 = {a}。'
    elif year == 4:
        if topic == 0: text, answer, why = f'面积 Area：长 {a} 米、宽 {b} 米的长方形，面积是多少平方米？', a*b, f'面积 = 长 × 宽 = {a} × {b} = {a*b} 平方米。'
        elif topic == 1: text, answer, why = f'周长 Perimeter：长 {a} 厘米、宽 {b} 厘米的长方形周长多少厘米？', 2*(a+b), f'周长 = 2 ×（长 + 宽）= {2*(a+b)} 厘米。'
        elif topic == 2: text, answer, why = f'找零 Money：用20澳元购买 {b} 澳元的午餐，应找回多少澳元？', 20-b, f'找零 = 付出的钱 − 价格 = 20 − {b} = {20-b} 澳元。'
        else: text, answer, why = f'分数 Fraction：{a*8} 的八分之三是多少？', a*3, f'先除以8，再乘3：{a*8} ÷ 8 × 3 = {a*3}。'
    elif year == 5:
        if topic == 0: text, answer, why = f'百分数 Percentage：{a*20} 的25%是多少？', a*5, f'25% = 四分之一：{a*20} ÷ 4 = {a*5}。'
        elif topic == 1: text, answer, why = f'小数 Decimal：{a}.{b} + 0.{10-b} = ？', a+1, f'十分位合计10个十分之一，进1，结果为 {a+1}。'
        elif topic == 2: text, answer, why = f'体积 Volume：长 {a}、宽 {b}、高2厘米的长方体体积多少立方厘米？', a*b*2, f'体积 = 长 × 宽 × 高 = {a} × {b} × 2 = {a*b*2}。'
        else: text, answer, why = f'平均数 Mean：{a}、{a+2}、{a+4} 的平均数是多少？', a+2, f'总和除以个数：({a}+{a+2}+{a+4}) ÷ 3 = {a+2}。'
    elif year == 6:
        if topic == 0: text, answer, why = f'折扣 Discount：{a*20} 澳元的书包打八折，售价多少澳元？', a*16, f'付原价的80%：{a*20} × 0.8 = {a*16} 澳元。'
        elif topic == 1: text, answer, why = f'整数 Integers：气温 −{a}°C 上升 {a+b}°C 后是多少°C？', b, f'−{a} + {a+b} = {b}。'
        elif topic == 2: text, answer, why = f'概率 Probability：袋内有 {a} 红球和 {b} 蓝球，共有几种等可能的单球抽取结果（按球计）？', a+b, f'每个球是一个结果，合计 {a} + {b} = {a+b}。'
        else: text, answer, why = f'分数运算 Fractions：{a*12} 的三分之二是多少？', a*8, f'先除以3再乘2：{a*12} ÷ 3 × 2 = {a*8}。'
    elif year == 7:
        if topic == 0: text, answer, why = f'代数 Algebra：x + {b} = {a+b}，x = ？', a, f'等式两边减 {b}，得 x = {a}。'
        elif topic == 1: text, answer, why = f'整数 Integers：−{a} × {b} = ？', -a*b, f'负数乘正数为负数，绝对值为 {a} × {b} = {a*b}。'
        elif topic == 2: text, answer, why = f'角 Angles：三角形两个内角为 {a*5}° 和 {b*5}°，第三个角多少度？', 180-a*5-b*5, f'三角形内角和180°：180 − {a*5} − {b*5} = {180-a*5-b*5}°。'
        else: text, answer, why = f'比 Ratio：果汁和水为1:{b}，用 {a} 升果汁需多少升水？', a*b, f'水是果汁的 {b} 倍：{a} × {b} = {a*b} 升。'
    elif year == 8:
        if topic == 0: text, answer, why = f'方程 Equation：{b}x + {a} = {a+b*a}，x = ？', a, f'两边减 {a}，再除以 {b}，得 x = {a}。'
        elif topic == 1: text, answer, why = f'指数 Indices：{a}² = ？', a*a, f'平方就是自身相乘：{a} × {a} = {a*a}。'
        elif topic == 2: text, answer, why = f'速率 Rate：{b} 小时行驶 {a*b*10} 公里，平均时速多少公里？', a*10, f'速率 = 路程 ÷ 时间 = {a*b*10} ÷ {b} = {a*10} 公里/小时。'
        else: text, answer, why = f'百分数 Percentage：{a*100} 澳元增加 {b}% 后为多少澳元？', a*(100+b), f'新值 = 原值 × (1 + {b}/100) = {a*(100+b)} 澳元。'
    elif year == 9:
        if topic == 0: text, answer, why = f'勾股定理 Pythagoras：直角三角形直角边为 {a*3} 和 {a*4} 厘米，斜边多长？', a*5, f'斜边² = {a*3}² + {a*4}² = {a*a*25}，开平方得 {a*5} 厘米。'
        elif topic == 1: text, answer, why = f'线性函数 Linear：y = {b}x − {a}，x = {a} 时 y = ？', a*b-a, f'代入 x：{b} × {a} − {a} = {a*b-a}。'
        elif topic == 2: text, answer, why = f'展开 Expand：(x + {a})(x + {b}) 展开后 x 的系数是？', a+b, f'x² + ({a}+{b})x + {a*b}，所以系数为 {a+b}。'
        else: text, answer, why = f'科学计数 Scientific notation：{a} × 10³ 等于多少？', a*1000, f'10³ = 1000，故 {a} × 1000 = {a*1000}。'
    else:
        if topic == 0: text, answer, why = f'二次方程 Quadratic：x² = {a*a} 的正根是多少？', a, f'x = ±{a}，题目要求正根，所以是 {a}。'
        elif topic == 1: text, answer, why = f'复利 Compound interest：本金 {a*1000} 澳元，年利率10%，两年后本息多少澳元？', a*1210, f'本息 = {a*1000} × 1.1² = {a*1210} 澳元。'
        elif topic == 2: text, answer, why = f'直线 Slope：经过 (0, {b}) 和 (2, {b+a*2}) 的直线斜率是多少？', a, f'斜率 = y变化量 ÷ x变化量 = ({b+a*2} − {b}) ÷ 2 = {a}。'
        else: text, answer, why = f'概率 Probability：独立投掷 {a} 枚公平硬币，共有多少种等可能的正反面组合？', 2**a, f'每枚有2种结果，独立相乘：2^{a} = {2**a}。'
    if topic == 4:
        if year <= 2:
            values = rng.sample(range(1, 21 if year<=1 else 101),3)
            text = f'数据 Data：三组分别有 {values[0]}、{values[1]}、{values[2]} 个物品，最多的一组有几个？'
            answer = max(values)
            why = f'逐个比较三个数量，最大的数为 {answer}。'
        elif year <= 4:
            values = rng.sample(range(2, 101),3)
            if year==3:
                text=f'数据 Data：三天分别收集 {values[0]}、{values[1]}、{values[2]} 个回收瓶，一共收集多少个？'
                answer=sum(values);why=f'把三天的数量相加：{values[0]} + {values[1]} + {values[2]} = {answer}。'
            else:
                text=f'数据 Data：三组读书数量是 {values[0]}、{values[1]}、{values[2]} 本，最多比最少多几本？'
                answer=max(values)-min(values);why=f'最大数减最小数：{max(values)} − {min(values)} = {answer}。'
        elif year in (5,6,7,8):
            values = rng.sample(range(2, 201),3)
            if year in (5,8):
                values[2] += (-sum(values)) % 3
                text=f'平均数 Mean：{values[0]}、{values[1]}、{values[2]} 的平均数是多少？'
                answer=sum(values)//3;why=f'总和除以个数：{sum(values)} ÷ 3 = {answer}。'
            elif year==6:
                text=f'中位数 Median：{values[0]}、{values[1]}、{values[2]} 的中位数是多少？'
                answer=sorted(values)[1];why='从小到大排列：'+ '、'.join(map(str,sorted(values)))+f'；中间的数是 {answer}。'
            else:
                text=f'极差 Range：{values[0]}、{values[1]}、{values[2]} 的极差是多少？'
                answer=max(values)-min(values);why=f'最大值 − 最小值 = {max(values)} − {min(values)} = {answer}。'
        else:
            x,y,slope = rng.randint(1,50),rng.randint(1,100),rng.randint(-20,20)
            step=rng.randint(1,10)
            text=f'线性关系 Linear：直线经过 ({x}, {y}) 和 ({x+step}, {y+slope*step})，斜率是多少？'
            answer=slope;why=f'斜率 = y变化量 ÷ x变化量 = ({y+slope*step} − {y}) ÷ ({x+step} − {x}) = {slope}。'
    choices = {answer}
    while len(choices) < 4:
        choices.add(answer + rng.choice([-1, 1]) * rng.randint(1, max(3, abs(answer)//3)))
    choices = list(sorted(choices)); rng.shuffle(choices)
    identity = hashlib.sha256(f'{year}|{text}'.encode()).hexdigest()[:24]
    return dict(id='math-v1-'+identity, year=year, subject='math', prompt=text,
                options=[str(x) for x in choices], answer=choices.index(answer), explanation=why)

def generate(bank, day):
    if bank.get('schema') != 1: raise ValueError('Invalid schema')
    seen = {q['id'] for q in bank['questions']}
    dates = set(bank.get('batches', []))
    if day.isoformat() in dates: return bank
    count = 20 if not dates else 5
    for year in range(11):
        rng = random.Random(f'tuaotv-math-v1/{day}/{year}')
        added = 0
        for _ in range(100000):
            q = question(year, rng)
            if q['id'] in seen: continue
            q['published'] = day.isoformat()
            bank['questions'].append(q); seen.add(q['id']); added += 1
            if added == count: break
        if added != count: raise ValueError(f'Year {year} question templates exhausted; expand before publishing')
    bank['batches'] = sorted(dates | {day.isoformat()})
    bank['updated'] = day.isoformat()
    return bank

def validate(bank):
    ids = set()
    for q in bank['questions']:
        assert q['id'] not in ids; ids.add(q['id'])
        assert 0 <= q['year'] <= 10 and len(q['options']) == len(set(q['options'])) == 4
        assert 0 <= q['answer'] < 4 and q['prompt'] and q['explanation']
    return bank

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--date', type=date.fromisoformat, default=datetime.now(ZoneInfo('Australia/Brisbane')).date())
    args = parser.parse_args()
    bank = json.loads(args.output.read_text()) if args.output.exists() else dict(schema=1, subject='math', curriculum='Australian Curriculum v9 practice; approximate year alignment, not an assessment', source=SOURCE, questions=[], batches=[])
    bank = validate(generate(bank, args.date))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending = args.output.with_suffix('.pending')
    pending.write_text(json.dumps(bank, ensure_ascii=False, indent=2)+'\n')
    pending.replace(args.output)
    print(f"{bank['updated']}: {len(bank['questions'])} questions verified")

if __name__ == '__main__': main()
