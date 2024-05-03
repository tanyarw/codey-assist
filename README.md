# codey-extension


### Step 1:

Run `pip install https://github.com/tanyarw/codey-assist.git` to install extensions

### Step 2:

Use command `%load_ext codey_assist` loads this extension

### Step 3:

To generate context aware code

```py
%%codey
<code generation prompt>
```

### Step 4:

To index a fresh code repository

```py
%set_index <path>
```

### Step 5:

If your code repository has been indexed and you run,

```py
%set_index <path>
```

then the files listed under git diff will be reindexed.

### Step 6:

To interact with your repository

```py
%%code_qna
<prompt>
```
