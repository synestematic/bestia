# bestia
bestia is a library of functions and classes designed to help you build dynamic command-line applications on Linux / Darwin systems.

***
## available functions / classes
### connect.py
* http_get

### iterate.py
* string_to_list
* iterable_to_string
* items_are_equal
* unique_random_items
* pop_random_item

### output.py
* tty_size
* tty_rows
* tty_columns
* clear_screen
* Row
* echo
* FString
* expand_seconds
* remove_path
* replace_special_chars
* obfuscate_random_chars

### misc.py
* command_output
* copy_to_clipboard
* file_type
* say


***
## dependencies
Installing bestia will install the following pip packages on your system:

* pyperclip
* termcolor

The following binaries are also required by some functions:

* file
* curl
* stty
* say
