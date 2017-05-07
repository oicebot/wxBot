# coding=utf-8
"""
dice.py - Dice Module
Copyright 2010-2013, Dimitri "Tyrope" Molenaars, TyRope.nl
Copyright 2013, Ari Koivula, <ari@koivu.la>
Licensed under the Eiffel Forum License 2.

http://sopel.chat/
"""
from __future__ import unicode_literals, absolute_import, print_function, division
import random
import re
import operator

import sopel.module
from sopel.tools.calculation import eval_equation
from sopel import formatting as sfm

class DicePouch:
    def __init__(self, num_of_die, type_of_die, addition):
        """Initialize dice pouch and roll the dice.

        Args:
            num_of_die: number of dice in the pouch.
            type_of_die: how many faces the dice have.
            addition: how much is added to the result of the dice.
        """
        self.num = num_of_die
        self.type = type_of_die
        self.addition = addition

        self.dice = {}
        self.dropped = {}

        self.roll_dice()

    def roll_dice(self):
        """Roll all the dice in the pouch."""
        self.dice = {}
        self.dropped = {}
        for __ in range(self.num):
            number = random.randint(1, self.type)
            count = self.dice.setdefault(number, 0)
            self.dice[number] = count + 1

    def drop_lowest(self, n):
        """Drop n lowest dice from the result.

        Args:
            n: the number of dice to drop.
        """

        sorted_x = sorted(self.dice.items(), key=operator.itemgetter(0))

        for i, count in sorted_x:
            count = self.dice[i]
            if n == 0:
                break
            elif n < count:
                self.dice[i] = count - n
                self.dropped[i] = n
                break
            else:
                self.dice[i] = 0
                self.dropped[i] = count
                n = n - count

        for i, count in self.dropped.items():
            if self.dice[i] == 0:
                del self.dice[i]

    def get_simple_string(self):
        """Return the values of the dice like (2+2+2[+1+1])+1."""
        dice = self.dice.items()
        faces = ("+".join([str(face)] * times) for face, times in dice)
        dice_str = "+".join(faces)

        dropped_str = ""
        if self.dropped:
            dropped = self.dropped.items()
            dfaces = ("+".join([str(face)] * times) for face, times in dropped)
            dropped_str = "[+%s]" % ("+".join(dfaces),)

        plus_str = ""
        if self.addition:
            plus_str = "{:+d}".format(self.addition)

        return "(%s%s)%s" % (dice_str, dropped_str, plus_str)

    def get_compressed_string(self):
        """Return the values of the dice like (3x2[+2x1])+1."""
        dice = self.dice.items()
        faces = ("%dx%d" % (times, face) for face, times in dice)
        dice_str = "+".join(faces)

        dropped_str = ""
        if self.dropped:
            dropped = self.dropped.items()
            dfaces = ("%dx%d" % (times, face) for face, times in dropped)
            dropped_str = "[+%s]" % ("+".join(dfaces),)

        plus_str = ""
        if self.addition:
            plus_str = "{:+d}".format(self.addition)

        return "(%s%s)%s" % (dice_str, dropped_str, plus_str)

    def get_sum(self):
        """Get the sum of non-dropped dice and the addition."""
        result = self.addition
        for face, times in self.dice.items():
            result += face * times
        return result

    def get_number_of_faces(self):
        """Returns sum of different faces for dropped and not dropped dice

        This can be used to estimate, whether the result can be shown in
        compressed form in a reasonable amount of space.
        """
        return len(self.dice) + len(self.dropped)


def _roll_dice(dice_expression):
    result = re.search(
        r"""
        (?P<dice_num>-?\d*)
        d
        (?P<dice_type>-?\d+)
        (v(?P<drop_lowest>-?\d+))?
        $""",
        dice_expression,
        re.IGNORECASE | re.VERBOSE)

    dice_num = int(result.group('dice_num') or 1)
    dice_type = int(result.group('dice_type') or 20)

    # Dice can't have zero or a negative number of sides.
    if dice_type == 0:
        #bot.action("拿出了一把0面的骰子，但它们随即就消失在了空间里。")
        return "Error: 你拿出了一把0面的骰子，但它们随即就消失在了空间里。"  # Signal there was a problem

    if dice_type < 0:
        #bot.action("拿出了一把 %s 面的骰子，但它们随即就消失在了空间里。" % dice_type)
        return 0,"Error: 你拿出了一把 %s 面的骰子，但它们随即就消失在了空间里。" % dice_type # Signal there was a problem

    # Can't roll a negative number of dice.
    if dice_num < 0:
        return "Error: 我觉得我尽量还是不要做丢负数个骰子这种违反物理规律的事情，谢谢合作。" # Signal there was a problem

    # Upper limit for dice should be at most a million. Creating a dict with
    # more than a million elements already takes a noticeable amount of time
    # on a fast computer and ~55kB of memory.
    if dice_num > 1000:
        return 'Error: 抱歉，目前我手边只有一千个骰子呢。'  # Signal there was a problem

    dice = DicePouch(dice_num, dice_type, 0)

    if result.group('drop_lowest'):
        drop = int(result.group('drop_lowest'))
        if drop >= 0:
            dice.drop_lowest(drop)
        #else:
            return "Error: I can't drop the lowest %d dice. =(" % drop

    return dice


def roll(trigger):
    """.dice XdY[vZ][+N], rolls dice and reports the result.

    X is the number of dice. Y is the number of faces in the dice. Z is the
    number of lowest dice to be dropped from the result. N is the constant to
    be applied to the end result.
    """
    # This regexp is only allowed to have one captured group, because having
    # more would alter the output of re.findall.
    dice_regexp = r"-?\d*[dD]-?\d+(?:[vV]-?\d+)?"

    # Get a list of all dice expressions, evaluate them and then replace the
    # expressions in the original string with the results. Replacing is done
    # using string formatting, so %-characters must be escaped.
    if not trigger:
        return "额，你要我丢啥骰子？我没看到呢。"
    explain_str = ''
    total_str = trigger
    arg_str = total_str[0]
    if len(total_str) > 1 :
        explain_str = ' ' +  ' '.join(total_str[1:]) + ' '

    if arg_str in ['d','D']:
        arg_str = 'd20'
    dform = ['d-','d+','d*','d/','D-','D+','D*','D/','d(','D(',]
    if any(x in arg_str for x in dform):
        for i in dform:
            arg_str = arg_str.replace(i ,i[0] + '20' +i[1] )
    
    dice_expressions = re.findall(dice_regexp, arg_str)
    arg_str = arg_str.replace("%", "%%")
    arg_str = re.sub(dice_regexp, "%s", arg_str)

    f = lambda dice_expr: _roll_dice(dice_expr)
    dice = list(map(f, dice_expressions))

    if 'Error' in dice:
        # Stop computing roll if there was a problem rolling dice.
        return dice

    def _get_eval_str(dice):
        return "(%.10g)" % (dice.get_sum(),)

    def _get_pretty_str(dice):
        if dice.num <= 10:
            return dice.get_simple_string()
        elif dice.get_number_of_faces() <= 10:
            return dice.get_compressed_string()
        else:
            return "(...)"

    eval_str = arg_str % (tuple(map(_get_eval_str, dice)))
    pretty_str = arg_str % (tuple(map(_get_pretty_str, dice)))

    # Showing the actual error will hopefully give a better hint of what is
    # wrong with the syntax than a generic error message.
    try:
        result = eval_equation(eval_str)
        result = float("{:.10g}".format(result))
    except Exception as e:
        if "not implement" in '%s' % e:
            return "出错啦，没法计算 %s" % (eval_str)
        else:
            return "出错啦，没法计算 %s，原因：%s" % (eval_str, e)

    return "进行%s检定[%s]： %s=%s" % ( explain_str, trigger[0], pretty_str, result)


def choose(trigger):
    if not trigger:
        return u'我可以帮你做决定哟，但你需要先指明有哪些选项，用空格键隔开。'

    if len(trigger) <= 1:
        return u'只有一个选项吗？多个选项请用空格隔开'
    pick = random.choice(trigger)
    return u'经过仔细考虑后，在 %s 中选择了：%s' % (' '.join(trigger), pick)

