

# ttyp
Typing test in your terminal.

# Installation
Install `ttyp` using pip:
```
pip install ttyp
```
Requires Python 3.9 or later.
# Usage
Start a typing test with default settings (English, 25 words):
```
ttyp 
```
Show help:
```
ttyp --help
```
Run a test in Spanish with 50 words:
```
ttyp --language spanish --count 50
```
List available languages:
```
ttyp --list-languages
```

# Tips
Alias your favorite options to `ttyp`:
```
alias ttyp="ttyp -q --language portuguese"
```
Stats are written to `stderr`, so you can redirect them to a processing script using process substitution:
```
ttyp 2> >(python your-processing-script.py)
```

# Credits
Language word lists derived from the [Monkeytype project](https://github.com/monkeytypegame/monkeytype),  
available under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).
