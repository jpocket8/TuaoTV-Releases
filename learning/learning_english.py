"""English presentation of the stable v1 question templates (no RNG consumption)."""
def render(year, topic, a, b, answer, values=None, line=None):
    if topic == 4:
        if year <= 2:
            return (f'Three groups contain {values[0]}, {values[1]} and {values[2]} objects. How many objects are in the largest group?',
                    f'Compare the three numbers. The largest number is {answer}.')
        if year == 3:
            return (f'A class collects {values[0]}, {values[1]} and {values[2]} bottles over three days. How many bottles are collected altogether?',
                    f'Add the three amounts: {values[0]} + {values[1]} + {values[2]} = {answer}.')
        if year == 4:
            return (f'Three groups read {values[0]}, {values[1]} and {values[2]} books. How many more books does the largest total have than the smallest total?',
                    f'Subtract the smallest total from the largest: {max(values)} − {min(values)} = {answer}.')
        if year in (5, 8):
            return (f'What is the mean of {values[0]}, {values[1]} and {values[2]}?',
                    f'Add the values, then divide by 3: {sum(values)} ÷ 3 = {answer}.')
        if year == 6:
            return (f'What is the median of {values[0]}, {values[1]} and {values[2]}?',
                    'Put the numbers in order: '+', '.join(map(str, sorted(values)))+f'. The middle number is {answer}.')
        if year == 7:
            return (f'What is the range of {values[0]}, {values[1]} and {values[2]}?',
                    f'Range = largest − smallest = {max(values)} − {min(values)} = {answer}.')
        x, y, slope, step = line
        return (f'A straight line passes through ({x}, {y}) and ({x+step}, {y+slope*step}). What is its gradient?',
                f'Gradient = change in y ÷ change in x = ({y+slope*step} − {y}) ÷ ({x+step} − {x}) = {slope}.')
    questions = {
        0: [
            (f'There are {a} koalas. Another {b} koalas arrive. How many koalas are there now?', f'Add the two groups: {a} + {b} = {answer} koalas.'),
            (f'Which number is larger: {a} or {a+b}?', f'{a+b} is {b} more than {a}, so {a+b} is larger.'),
            (f'What comes next: {a}, {a+1}, {a+2}, ___?', f'Count on by 1. The number after {a+2} is {answer}.'),
            (f'You have {a+b} shells and take away {b}. How many shells are left?', f'{a+b} − {b} = {answer} shells.')],
        1: [
            (f'What is {a} + {b}?', f'Add the two amounts: {a} + {b} = {answer}.'),
            (f'What is {a+b} − {b}?', f'Take {b} away from {a+b}: {a+b} − {b} = {answer}.'),
            (f'How many tens are in {a*10+b}?', f'{a*10+b} has {a} tens and {b} ones.'),
            (f'{a*2} grapes are shared equally between 2 children. How many grapes does each child get?', f'Divide into two equal groups: {a*2} ÷ 2 = {answer}.')],
        2: [
            (f'What is {a*5} + {b}?', f'Add {b} to {a*5}: {a*5} + {b} = {answer}.'),
            (f'There are {b} groups of 5 counters. How many counters are there altogether?', f'{b} × 5 = {answer} counters.'),
            (f'What is the total value of {a} ten-cent coins, in Australian cents?', f'{a} × 10 = {answer} cents.'),
            (f'What comes next: {a*2}, {a*2+2}, {a*2+4}, ___?', f'The pattern increases by 2. Add 2 again to get {answer}.')],
        3: [
            (f'What is {a} × {b}?', f'{a} groups of {b} make {a} × {b} = {answer}.'),
            (f'What is {a*b} ÷ {b}?', f'Since {a} × {b} = {a*b}, the quotient is {a}.'),
            (f'How many centimetres are in {a} metres?', f'1 metre = 100 centimetres, so {a} × 100 = {answer} centimetres.'),
            (f'What is one quarter of {a*4} strawberries?', f'Divide the total into four equal parts: {a*4} ÷ 4 = {answer}.')],
        4: [
            (f'A rectangle is {a} m long and {b} m wide. What is its area in square metres?', f'Area = length × width = {a} × {b} = {answer} m².'),
            (f'A rectangle is {a} cm long and {b} cm wide. What is its perimeter in centimetres?', f'Perimeter = 2 × (length + width) = 2 × ({a} + {b}) = {answer} cm.'),
            (f'You pay A$20 for lunch costing A${b}. How much change do you receive, in Australian dollars?', f'Change = amount paid − cost = 20 − {b} = A${answer}.'),
            (f'What is three eighths of {a*8}?', f'Divide by 8, then multiply by 3: {a*8} ÷ 8 × 3 = {answer}.')],
        5: [
            (f'What is 25% of {a*20}?', f'25% is one quarter: {a*20} ÷ 4 = {answer}.'),
            (f'What is {a}.{b} + 0.{10-b}?', f'The tenths add to one whole, so the result is {answer}.'),
            (f'A rectangular prism is {a} cm long, {b} cm wide and 2 cm high. What is its volume in cubic centimetres?', f'Volume = length × width × height = {a} × {b} × 2 = {answer} cm³.'),
            (f'What is the mean of {a}, {a+2} and {a+4}?', f'Add the values and divide by 3: ({a} + {a+2} + {a+4}) ÷ 3 = {answer}.')],
        6: [
            (f'A school bag costs A${a*20} before a 20% discount. What is the sale price, in Australian dollars?', f'Pay 80% of the original price: {a*20} × 0.8 = A${answer}.'),
            (f'The temperature is −{a}°C. It rises by {a+b}°C. What is the new temperature in degrees Celsius?', f'−{a} + {a+b} = {answer}°C.'),
            (f'A bag contains {a} red balls and {b} blue balls. If each individual ball is equally likely to be drawn, how many individual ball outcomes are possible?', f'Each ball is one possible outcome: {a} + {b} = {answer}.'),
            (f'What is two thirds of {a*12}?', f'Divide by 3, then multiply by 2: {a*12} ÷ 3 × 2 = {answer}.')],
        7: [
            (f'Solve for x: x + {b} = {a+b}.', f'Subtract {b} from both sides to get x = {answer}.'),
            (f'What is −{a} × {b}?', f'A negative number times a positive number is negative: −({a} × {b}) = {answer}.'),
            (f'Two angles of a triangle are {a*5}° and {b*5}°. What is the third angle, in degrees?', f'Triangle angles add to 180°: 180 − {a*5} − {b*5} = {answer}°.'),
            (f'Juice and water are mixed in the ratio 1:{b}. How many litres of water are needed for {a} litres of juice?', f'The water amount is {b} times the juice amount: {a} × {b} = {answer} litres.')],
        8: [
            (f'Solve for x: {b}x + {a} = {a+b*a}.', f'Subtract {a} from both sides, then divide by {b}: x = {answer}.'),
            (f'What is {a}²?', f'Squaring means multiplying a number by itself: {a} × {a} = {answer}.'),
            (f'A vehicle travels {a*b*10} km in {b} hours. What is its average speed in km/h?', f'Speed = distance ÷ time = {a*b*10} ÷ {b} = {answer} km/h.'),
            (f'A${a*100} increases by {b}%. What is the new amount, in Australian dollars?', f'New amount = {a*100} × (1 + {b}/100) = A${answer}.')],
        9: [
            (f'A right-angled triangle has shorter sides of {a*3} cm and {a*4} cm. How long is the hypotenuse, in centimetres?', f'By Pythagoras, c² = {a*3}² + {a*4}² = {a*a*25}. The positive square root is {answer} cm.'),
            (f'If y = {b}x − {a}, what is y when x = {a}?', f'Substitute x = {a}: {b} × {a} − {a} = {answer}.'),
            (f'When (x + {a})(x + {b}) is expanded, what is the coefficient of x?', f'The expansion is x² + ({a} + {b})x + {a*b}. The coefficient of x is {answer}.'),
            (f'Write {a} × 10³ as an ordinary number.', f'10³ = 1000, so {a} × 1000 = {answer}.')],
        10: [
            (f'What is the positive solution of x² = {a*a}?', f'The solutions are x = ±{a}. The positive solution is {answer}.'),
            (f'A${a*1000} earns 10% compound interest per year. What is the balance after 2 years, in Australian dollars?', f'Balance = {a*1000} × 1.1² = A${answer}.'),
            (f'What is the gradient of the line through (0, {b}) and (2, {b+a*2})?', f'Gradient = change in y ÷ change in x = ({b+a*2} − {b}) ÷ 2 = {answer}.'),
            (f'{a} fair coins are tossed independently. How many equally likely sequences of heads and tails are possible?', f'Each coin has 2 outcomes. Multiply for independent tosses: 2^{a} = {answer}.')]
    }
    return questions[year][topic]
