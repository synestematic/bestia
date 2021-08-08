# bestia
bestia is a library of functions and classes designed to help you build vibrant and dynamic applications for the command-line on Linux / Darwin systems. It allows you to create rich evolving TUI's for your terminal-based tools using a simple and readable programming interface.


## installation
Please install bestia using pip:

```
$   python3 -m pip install bestia
```


The library does not require you to install any external dependencies.


## available functions / classes

### output.py

```
* echo
* FString
* Row
* tty_cursor
* tty_clear
* tty_up
* tty_rows
* tty_cols
* expand_seconds
* human_bytes
* remove_path
* obfuscate_random_chars
* ProgressBar
* ansi_esc_seq
* ansi_sgr_seq
```

### iterate.py

```
* LoopedList
* items_are_equal
* iterable_to_string
* unique_random_items
* pop_random_item
```


## api reference

Let's focus on the `echo` function, the `FString` class and the `Row` class which contain the core of this library's functionality.

`>>> from bestia.output import echo, FString, Row `


### echo() function:

This is a very basic function which takes your string as first argument, followed by any number of effects that you may want to apply to your text. You can specify up to a maximum of 2 colors (1st: foreground, 2nd: background) and as many effects as you want.

![](https://github.com/synestematic/bestia/blob/master/resources/e.png?raw=true)

Supported color values:  
`'black' 'red' 'green' 'yellow' 'blue' 'magenta' 'cyan' 'white'`  


Supported effect values:  
`'reset' 'bold' 'faint' 'underline' 'blink' 'reverse' 'conceal' 'cross' 'frame' 'circle' 'overline'`  

Not all terminal emulators support the same colors or effects so some of these may not work depending on what you are using. 

The echo function also has an optional last keyword argument `mode` that alters how strings are rendered|terminated. 

```
>>> echo("foo", mode='raw')
foo>>> 
```

The `'modern'` mode is your standard printing mode.  
The `'raw'` mode prints strings without appending a newline char.  
The `'retro'` mode emulates the printing style of an 80's computer by adding a random amount of lag to each char that gets printed. It can make your applications have a real vintage feel to them.

Play with all of them and see what you like!


### FString() class:

The `FString` class has all the "coloring" functionality of the `echo` function but requires you to explicitly use it's attributes `fg: str, bg: str, fx: list`. This added complexity allows for far more flexibility since you can specify these values when instantiating an object and modify them at will later. You can print your FString either by calling it's echo method or by printing the object itself.

Coloring is NOT however the main feature of this class, the most important functionality that `FString` provides is the ability to force strings into specific areas of your terminal space. It achieves this by dynamically padding your string with spaces (or any other char) so that it will be placed where needed on the horizontal plane.

```
>>> fs1 = FString('123', size=5, align='r')
>>> print(fs1)
  123
>>> fs1.size = 10
>>> print(fs1)
       123
>>> fs1.align = 'c'
>>> print(fs1)
   123    
```

Notice how the "123" string moves to the right by setting it's `size` and `align` attributes. The default value for `align` is `'l'`, but other possible values are:  
 `'l' 'r' 'c' 'cl' 'cr'`


`FString` can add space to your strings but it can also crop them if you set a `size` value lower than the string's actual length. This is extremely useful when you are dealing with dynamic text and you want to ensure it will not take more than a fixed amount of space in your application.

```
>>> fs2 = FString('Welcome to the Jungle!', size=10)
>>> fs2.echo()
Welcome to
>>> fs2.size = 16
>>> fs2.echo()
Welcome to the J
```   


Dealing with empty spaces can make it hard to understand where our FStrings finish and begin. You can use the `pad` attribute for debugging purposes or to create more interesting TUI's:

```
>>> FString(' asd ', size=20, align='cl', pad=' ').echo(mode='modern')
        asd         
>>> FString(' asd ', size=20, align='cl', pad='|').echo(mode='modern')
||||||| asd ||||||||
>>> FString(' asd ', size=20, align='cr', pad='*').echo(mode='modern')
******** asd *******
```

The `echo` method of `FString` also has an optional `mode` argument which works exactly as in the `echo` function. 


### Row() class:

Row() is a class that accepts any number of `str` or `FString` objects as arguments and forces them to print on the same terminal row by automatically detecting the size of your terminal window and resizing each item accordingly. It will crop items if their total length is more than your terminal size or add spaces if their length is less. It is a fantastic tool for building dynamic textual user interfaces. First, let's check out some basics:

```
>>> r = Row( '123', FString('ABC', align='r') )
>>> r.echo(mode='retro')
123                                                                                   ABC
```

The size of your terminal is calculated on the fly just before rendering your strings. This means that `Row` objects work great at keeping your data neat and viewable even across terminal window resizes.

Most of the times you will want your Row instances to automatically size up to your terminal width but if for some reason you don't, you can always set their `size` attribute to a static size.

```
>>> r.size = 30
>>> r.echo()
123                        ABC
```

If you need any of the strings that make up your `Row` to NOT be resized, just init a `FString` and then set it's `size` attribute to a static value. That object will now keep it's size static and `Row` will resize all other items.


```
>>> Row(
...     FString('id', size=3, fg='cyan', align='l', bg='blue', fx=['bold', 'underline']),
...     FString('Location', size=None, fg='yellow', bg='blue', fx=['bold', 'underline']),
...     FString('Size', size=6, align='r', bg='blue', fx=['bold', 'underline']),
...     FString('Files', size=6, fg='green', align='r', bg='blue', fx=['bold', 'underline']),
...     FString('Users', size=6, fg='red', align='r', bg='blue', fx=['bold', 'underline']),
...     FString('Categories', size=15, align='r', bg='blue', fx=['bold', 'underline']),
...    ).echo(mode='retro')
```

In this example, all items will have a fixed size and `Row` will take care of making them fit exactly into the terminal width by shrinking/expanding the Location `FString` (the only one that has not a fixed size value). The `mode` parameter will take care of giving the rendering of the string a retro vibe.

Unfortunately MarkDown does not do a great job at showing off all the possibilities that this library gives you in terms of creating classy looking CLI tools. I will let the next __screenshots__ section do some of the talking now with a couple of examples of applications built using bestia.

Enjoy!


## screenshots

![](https://github.com/synestematic/bestia/blob/master/resources/k.png?raw=true)

![](https://github.com/synestematic/bestia/blob/master/resources/r.png?raw=true)

![](https://github.com/synestematic/bestia/blob/master/resources/th.png?raw=true)

