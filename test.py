import interpreter
import std

inter = interpreter.HueLogoInterpreter()

std.load_words(inter)

inter.run_string('''
set nums [range 1 30]
forall num nums [
    set result quote []
    if [same? [modulo num 3] 0] {
        set result [sum result quote [Fizz]]
    }
    if [same? [modulo num 5] 0] {
        set result [sum result quote [Buzz]]
    }
    if [same? result quote []] {
        set result num
    }
    say result
]
''')