# Orion Language
Orion is a simple interpreted programming language, built for fun. 

## 🔃 Installation 
Install using pip:  
 ```
 pip install orion-lang
 ```

## 🛠️ Usage
Running it is easy:
```
orion <script.or>
```
<br>

# ℹ️ Documentation
## Whats new in Orion 0.2.0
* Support for module imports
* Added `math` module
* Boolean inversion
* New global function `find()`

## Variables
Variables can be declared with the **`var`** keyword
```
var x = 1;
```
Arrays must be declared with the **`array`** keyword
```
array x = [1, 2, 3, 4, 5];
```
## Array methods
#### `push()` : pushes an element to the last index
```
x.push("a");
// [1, 2, 3, 4, 5, "a"]
```
#### or multiple elements:
```
x.push("a", "b", "c");
// [1, 2, 3, 4, 5, "a", "b", "c"]
```
#### `pop()` : removes the last element of an array
```
x.pop();
// [1, 2, 3, 4]
```
#### `insert()` : inserts an element at the specified index
```
x.insert(0, "abc");
// ["abc", 1, 2, 3, 4, 5]
```
#### `delete()` : deletes the specified index of an array (the outermost dimension)
```
x.delete(1);
// [1, 3, 4, 5]
```

## Data types
Data types built into Orion are as follows: `string`, `int`, `float`, `True`, `False`, `Nothing`

<hr />

`null` values can be assigned using the **`Nothing`** keyword:
```
var a = Nothing;
```
Functions may also return `Nothing`:
```
fn donothing():
    return Nothing;
end
```

## Type conversion
Data types can also be converted.  
`int` : converts to integer  
```
var x = 3.0;
x = int(x); // 3
```
`float` : converts to float  
```
var x = 3;
x = float(x); // 3.0
```
`string` : converts to string  
```
var x = 3;
x = string(x); // "3"
```

### Strings
Strings can also be concatenated.
```
var str = "Hello" + ", " + "World";
print(str);
// Hello, World
```

## Booleans

`True` and `False` can be inverted interchangeably

Boolean inversion using `!`:
```
var x = True;

print(!x);
```

## Boolean operators

`&&` : AND operator  
`||`: OR operator

## If statements
```
if (condition):
    // do
end
```
*or*
```
if (condition):
    // do
else if (condition):
    // do
else:
    // do
end
```

## While statements
```
while (condition):
    // do
end
```

## For loops
*Examples:*  
```
// Example 1
for (var i = 0; i < 3; i++):
    print(i);
end
```
```
// Example 3
for (var i = 0; i < 3; i = i + 1):
    print(i);
end
```

##

## Functions
Functions can be written with the **`fn`** keyword. You can also return values using **`return`**
```
fn add(a, b):
    return a + b;
end
```
Recursion is also supported:
```
fn factorial(n):
    if (n==1):
        return 1;
    end
    return n * factorial(n-1);
end
```

## I/O
`ask()` : prompts the user for an input
```
var input = ask("name: ");
``` 
`print()` : prints a message into the terminal
```
print("Hello, world");
```
you can also print multiple items
```
print("Hello," "world");
// Hello, world
```

## Importing modules
Make multiple `.or` files work together!

**Syntax:**
```
import <YOUR_FILE_HERE> as <NAME>
                        (optional)
```
### Example
If you want to import from `\example\animals.or`:
```
import example.animals

print(animals.bark())

// some logic here
```

## Math module
Math is easy with `import math`!

| Name | Usage | Description |
|----------|-----------|-------------|
|`math.sqrt()`|`math.sqrt(number)`|returns the square root of a given number|
|`math.pi`|`math.pi`|mathematical constant pi|
|`math.pi`|`math.e`|euler's number|

## Global functions
| Name | Usage | Description |
|------|-------|-------------|
`terminate()`|`terminate()`|exits the program
`find()`|`find(target, element)`| returns `True` if element is found within target string 