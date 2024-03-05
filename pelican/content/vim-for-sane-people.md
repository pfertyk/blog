Title: Vim for sane people
Date: 2017-08-19
Summary: When you want something powerful but also something normal
Tags: vim

Long time ago, I decided to master Vim. Like many before me, I started with `vimtutor` to learn the basics, then played around with the editor a bit and attempted to use it for actual work. I soon realized that it will not be that simple. Vim's commands were powerful, but required some time getting used to. I knew I had to spend a lot more time to become proficient enough to use Vim as my main text editor.

But there was also something else.

Vim was significantly different than other editors I used by far. Things I took for granted became difficult. Keeping the list of previously opened files? Not easy. Searching in the whole document? Unintuitive. Pasting content from the clipboard? I had to use a mouse for that. A mouse in Vim! All of those problems made me come back to other editors and not spend enough time with Vim to learn it properly.

I realized that those problems were keeping me from using Vim on daily basis. I had to solve them, otherwise I would keep coming back to other editors and never really master Vim. So I searched through documentation and available plugins and, after many days of tweaking my `.vimrc` file, I finally came up with configuration that made Vim an editor I could use. Here I'd like to share that configuration with you and explain how it works.

Note: This post contains mostly hints as to making Vim more user friendly (like a normal editor), but also some generally useful things you can add to your configuration. Also, I'm a Python/JavaScript developer, so there are sections of my `.vimrc` file that focus on these languages (but you can still use the rest if you are not working with them). My `.vimrc` file is available [here](https://github.com/pfertyk/dotfiles/blob/master/vimrc), so you can check the complete configuration anytime you want.

### Plugins

Vim plugins are very powerful and turn this great text editor into a perfect tool for software developers. Using a plugin manager makes it a lot easier to install and update plugins. There are several options available for Vim. [Vundle](https://github.com/VundleVim/Vundle.vim) is one of them, and it works just fine.

To install it, you need to clone the repository:

```bash
$ git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
```

Then put this at the top of your `.vimrc` file:

```vim
set nocompatible
filetype off
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
Plugin 'VundleVim/Vundle.vim'
" other plugins go here
call vundle#end()
filetype plugin indent on
```

Every time you add a new plugin, run this command in Vim:

```vim
:PluginInstall
```

### Leader

Leader is a special key in Vim. It's a prefix for sequences of keys that you can map to different commands. Many plugins use it, but you can also configure your own mappings (which I recommend). By default, the leader key is the backslash. But you are going to use this key very often, so it should be changed to something more convinient, something that you can use with any hand, something bigger than usual keys. Space is an excellent choice:

```vim
let mapleader = ' '
```

### Clipboard

One of the things that annoyed me the most when I started using Vim was
copying and pasting text. Vim has its own registers, and they have nothing
to do with standard clipboard. Fortunately, there is a way to fix it:

```vim
vmap <Leader>y "+y
vmap <Leader>d "+d
nmap <Leader>p "+p
nmap <Leader>P "+P
vmap <Leader>p "+p
vmap <Leader>P "+P
```

Now pressing `Space+y` will copy the selected text into the clipboard, `Space+p` will paste the text from the clipboard, and `Space+d` will delete the text while copying it into the clipboard (the equivalent of `Ctrl+X` in normal editors). I've got to say, this made my work with Vim a lot easier.

### Search

Vim has excellent search tools, but they could use some tuning:

```vim
nnoremap / /\v
vnoremap / /\v
vnoremap // y/<c-r>"<cr>
set ignorecase
set smartcase
set gdefault
set hls
set incsearch
```

First 2 lines set `\v` ('very-magic') as default option for searching. It will cause all characters except 'a-zA-Z0-9_' to have special meaning, so if you want to use their literal meaning, you will have to precede them with the backslash. That makes working with regular expressions a lot more predictable.

The `//` mapping makes it easy to search the currently selected text.

Next 2 lines make searching case insensitive by default, unless you start typing characters with different case. So searching for `base` will match both `base` and `Base`, but searching for `Base` will only match the latter. I find it quite useful.

By default Vim searches only the current line. This behavior is very unintuitive. Setting `gdefault` fixes this issue.

Lastly, `hls` and `incsearch` highlight the search results as you type and move the cursor to the next available match.

### Buffers, sessions and projects

Instead of having files opened in tabs (like normal editors do), Vim has tabs that can contain windows, and each window can display one buffer, where buffer is a file. Multiple windows can display the same buffer, and the buffer can be replaced by another one without closing the window.

At first, it confused me a lot, but after a while it became quite natural and convinient. I realized that I don't really need tabs: I can just split windows using `:split` or `:vsplit` and then navigate between them with `Ctrl+W` and `hjkl`. Still, there was room for improvement here:

```vim
set directory^=$HOME/.vim/swp//
set viminfo^=%
set hidden
command! Bd :bp<bar>bd#

set sessionoptions=blank,buffers,curdir,resize,winpos,winsize

au VimLeave * call SaveVimProject()
function! SaveVimProject()
    if filereadable("./Project.vim")
        mksession! Project.vim
    endif
endfunction
```

The first line puts all the swap files created by Vim into one central directory (you need to create it first), therefore keeping your working directories clean.

Vim uses `.viminfo` file to store information from the previous editing session. Adding `%` option to `viminfo` keeps the list of last opened buffers.

Another one of the most annoying things I discovered about Vim is that it didn't let me hide the buffer (e.g. by loading another one into the window) if the buffer was modified. It's the equivalent of a normal editor not letting you switch to another tab unless you save the current file. Setting the `hidden` flag fixed this issue (Vim still complained if I wanted to close the program with unsaved modifications, but that's the behavior I wanted to keep).

The `Bd` command closes the current buffer (removes it from the buffer list) without closing the current window. That way you can close files without changing your window layouts. I find that command to be very helpful.

What comes next is my attempt to add project management to Vim. The `mksession` command creates a file with current session information. What exactly is stored in that file is defined by `sessionoptions`. I chose to store the empty windows, all of the buffers (not only the ones displayed in windows), current directory (very useful for file searching, which will be explained in a moment), size and position of the whole Vim window (useful for GVim), and the sizes of all open windows. That combination is sufficient for me to feel that I pick the project up where I left off.

To automate project management a bit, I created a function. If it finds a file called  `Project.vim` in the current directory, it overwrites it with current session settings. This function is called automatically when exiting Vim. So, to create a new project, you need to navigate to a directory with your project's files and create a `Project.vim` file manually, thus declaring it a project:

```vim
:cd /path/to/your/project
:mksession Project.vim
```

When you leave Vim, the project will be saved automatically. Next time you want to work on it again, all you have to do is import the project file and all your windows and files will be restored:

```vim
:so /path/to/your/project/Project.vim
```

Another thing is searching for files. There are several tree based file explorers for Vim, but I never used them. In my opinion, they take unnecessary space on the screen and don't bring much value. Instead of searching a file in a directory tree, I prefer to look for it by typing a fuzzy path. And that's what `CtrlP` plugin is for. You can add it to Vim like this:

```vim
Plugin 'ctrlpvim/ctrlp.vim'
```

Here is the configuration I use:

```vim
let g:ctrlp_cmd = 'CtrlPMixed'
let g:ctrlp_working_path_mode = 0
let g:ctrlp_max_files=0
let g:ctrlp_custom_ignore = '__pycache__\|node_modules'

map \ :CtrlPLine<cr>
```

The first line enables searching both the already opened files and other files (putting the most recently used ones on top of the search results). The next line disables working path mode feature, so we always search the entire current directory (that's why we made sure earlier to store the current directory in our `Project.vim` file). Setting `g:ctrlp_max_files` to 0 means that `CtrlP` will scan all the files in the current directory. Usually, there is no need to search inside `node_modules` (JavaScript) or `__pycache__` (Python) folders, so we can ignore them. With this configuration you can quickly find files like `auth/users/test_main.py` by pressing `Ctrl+P` and typing `usetesm`.

The last line adds a nice bonus: fuzzy searching the content of the file. Thanks to it you can easily find lines like *The quick brown fox jumps over the lazy dog* just by typing *quickjumps*. I don't use it very often, but sometimes it comes in handy.

### Windows

Usually I work with multiple windows and very often I want to resize them. To make the process easier, I created the following mapping:

```vim
map <a-l> :res +1<cr>
map <a-L> :res -1<cr>
map <a-h> :vertical res +1<cr>
map <a-H> :vertical res -1<cr>
```

This configuration lets me change the window width/height without touching the mouse (unfortunately, mapping the `Alt` key makes it work only in GVim).

### Indentation

PEP-8 specifies that one indentation level should be 4 spaces, and I'm not going to argue with that. For JavaScript/HTML files I prefer 2 spaces:

```vim
au FileType python setl ts=4 sw=4 sts=4 et
au FileType javascript,htmldjango,html,css,cucumber setl ts=2 sw=2 sts=2 et

set smartindent
```

The `smartindent` flag makes your life easier by detecting the current indentation level before you start a new line.

### Status line

I used a status line plugin for some time, but I didn't like it. It was bothersome to configure, and it didn't actually bring any value (except for the nice look). So I uninstalled the plugin and decided to instead configure my status line to show everything I need to know:

```vim
set laststatus=2

set statusline=
set statusline+=%t%m
set statusline+=%{TagInStatusLine()}
set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*%=
set statusline+=%l:%c(%p%%)
```

The first line makes the status line always visible. Next, we clear any existing status line configuration and display what follows:

* the name of the current file and the modified flag (`[+]`)
* current class and function name (only for Python files, requires `mgedmin/pythonhelper.vim` plugin)
* any warning messages
* `syntastic` flag (showing, by default, first error line number and the total number of errors)
* restore the normal highlight color and right align the rest of the status line
* the current line, column and percentage through the file

### Syntax

For syntax highlighting I use a plugin called `syntastic`:

```vim
Plugin 'scrooloose/syntastic'
```

The configuration looks like this:

```vim
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0
let g:syntastic_python_checkers = ['flake8']
let g:syntastic_python_flake8_exec = 'python3'
let g:syntastic_python_flake8_args = ['-m', 'flake8']
let g:syntastic_javascript_checkers = ['eslint']
let g:syntastic_javascript_eslint_exec = 'eslint'
```

It makes `syntactic` check the syntax when a file is opened (but not when you close Vim) and sets the linters for Python and JavaScript files (you need to install them first).

### Whitespaces

I can't remember the last time I actually wanted to leave some trailing whitespaces. So I configured Vim to display them:

```vim
set list
set listchars=tab:>-,trail:~

map <leader>l :set list!<cr>
```

The mapping allows you to toggle displaying whitespaces (but I can't imagine why you would want to turn it off).

### Color scheme

I initially used `solarized` theme, but I switched to `gruvbox`. You can install it like a normal plugin:

```vim
Plugin 'morhetz/gruvbox'
```

Additional configuration looks like this:

```vim
syntax enable
set background=dark
colorscheme gruvbox
```

### Git

To make working with Git a bit easier, I recommend these plugins:

```vim
Plugin 'airblade/vim-gitgutter'
Plugin 'tpope/vim-fugitive'
```

The first one marks modified lines and allows you to stage/undo/preview them (it has a lot of other features as well). The second is very useful for tracking authors of changes (`:GBlame`).

There are probably many other Vim plugins, but I prefer working with Git using the command line.

### Python

With some plugins and configuration, you can turn Vim into a powerful Python IDE:

```vim
Plugin 'fisadev/vim-isort'
Plugin 'davidhalter/jedi-vim'
Plugin 'python-rope/ropevim'
```

The `vim-isort` plugin helps you with sorting Python imports (but it doesn't always work the right way, and you need to install the `isort` module first). Jedi and Rope are Python autocompletion and refactoring tools. They add most of the IDE functionality to Vim (search for occurences, rename, go to definition and so on).

```vim
set colorcolumn=80

au FileType python map <buffer> <leader>b oimport ipdb; ipdb.set_trace()<esc>
au FileType python map <buffer> <leader>B Oimport ipdb; ipdb.set_trace()<esc>
```

Highlighting the 80th column helps a lot with keeping the line width withing the recommended 79 characters. Next 2 lines create a mapping for adding breakpoints.

### Other

There are several other plugins I use on daily basis:

* `scrooloose/nerdcommenter` makes commenting/uncommenting lines very easy
* `jiangmiao/auto-pairs` automatically creates a closing bracket when you open one
* `tpope/vim-surround` lets you easily surround text with brackets, quotes, HTML tags; lets you change the surrounding character, delete it and much more
* `tpope/vim-abolish` it has a lot of options, but I usually use it to change variable names from snake case to upper case

This additional configuration might also make your life easier:

```vim
map <a-j> :m+1<cr>
map <a-k> :m-2<cr>

set cursorline
set nu
set autoread
set guioptions-=m
set shortmess+=I

nnoremap j gj
nnoremap k gk

command! XmlPrettyPrint :%!xmllint --format -
command! JsonPrettyPrint :%!python -m json.tool
```

First 2 lines create a mapping for moving the current line up and down (unfortunately, since I mapped the `Alt` key, it only works in GVim).

Next we tell Vim to always highlight the current line, always show the line numbers, automatically reload the files if they were modified outside of Vim, hide the menu bar (for GVim) and not to display the intro message on startup.

Sometimes the line you are editing will not fit in the window and will instead be wrapped. Using `gj` and `gk` lets you navigate through such lines (instead of moving to the next line, pressing `j` will move the cursor down, but still in the same line; that's the behavior you can expect from a normal editor).

If you work with JSON and XML files, you might want to format them. That's what the next 2 commands do (you need to install `json.tool` module and `xmllint` for them to work).

### Summary

Vim is a very powerful editor. If you ever tried it and failed (like I did), maybe you can give it another chance with these hints. If you know other useful tricks or spot an error in this post, please let me know.
