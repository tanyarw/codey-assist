# codey-extension

1. Create a venv
2. install requirements.txt
3. run `pip install -e .` to install code assist
4. in the notebook `sample.ipynb`, the command `%load_ext codey_assist` loads this extension
5. try to run this
```
%%codey
<prompt>
```
6. For code qna here are 2 steps. Index is a one time activity
```
%index path
```
```
%%code_qna
<prompt>
```
