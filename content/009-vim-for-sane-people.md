Title: Vim for sane people
Date: 2017-08-09
Summary: When you want something powerful but also something normal
Tags: vim

Long time ago, I decided to master Vim. Like many before me, I started with the vimtutor to learn the basics, then played around with the editor a bit and attempted to use it for actual work. I soon realized that it will not be that simple. Vim's commands were powerful, but required some time getting used to. I knew I had to spend a lot more time to become proficient enough to use Vim as my main text editor.

But there was also something else.

Vim was significantly different than other editors I used by far. Things I took for granted become difficult. Keeping the list of previously opened files? Not easy. Searching in the whole document? Unintuitive. Pasting content from the clipboard? I had to use a mouse for that. A mouse in Vim! All of those problems made me come back to other editors and not spend enough time to master Vim.

I realized that those problems were the ones that kept me from using Vim on daily basis. I had to solve them, otherwise I would keep coming back to other editors and never really master Vim. So I searched through documentation and available plugins and, after many days of tweaking my `.vimrc` file, I finally came up with configuration that made Vim an editor I could use. Here I'd like to share that configuration with you.

Note: This post contains mostly hints as to making Vim more user friendly (more like a normal editor), but also some generally useful things you can add to your configuration. Also, I'm a Python/JavaScript developer, so part of my configuration is prepared especially for those languages (but you can still use the rest if you are not working with these languages).

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

Leader is a special key in Vim. It's a prefix for sequences of keys that you can map to different commands. Unlike shortcuts, you don't have to press all keys simultaneously, but one after another quickly. By default, the leader key is the backslash. But you are going to use the leader key very often, so it should be changed to something more convinient, something that you can use with any hand, something bigger than the usual key. Space key is an excellent choice:

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

Now pressing `Space + y` will copy the selected text to clipboard, `space + p` will paste the text from clipboard and so on. I've got to say, this made my work with Vim a lot easier.

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

First 2 lines set `\v` ('very-magic') as default option for searching. It will cause all characters except `a-zA-Z0-9_` to have special meaning, so if you want to use their literal meaning you will have to use the backslash. That makes it a lot easier to work with regular expressions.

The `//` mapping makes it easy to search the currently selected text.

Next 2 lines make the searching case insensitive by default, unless you start typing characters with different case. So searching for `base` will match both `base` and `Base`, but searching for `Base` will only match the latter. I find it quite useful.

By default Vim searches only the current line. It is very unintuitive. Setting `gdefault` fixes this issue.

Lastly, `hls` and `incsearch` highlight the search results as you type and move the coursor to the next available match.

### Buffers and sessions

Instead of having files opened in tabs (like normal editors do), Vim has tabs that can contain windows, and each window can display one buffer, where buffer is a file. Multiple windows can display one buffer, and the buffer can be changed without closing the window.

At first, it confused me a lot, but after a while it become quite natural and convinient. I realized that I don't really need tabs. I split a window using `:split` or `:vsplit` and then navigate between them with `Ctrl+W` and `hjkl`. Still, there is space for improvement here:

```vim
set directory^=$HOME/.vim/swp//
set viminfo^=%
set hidden

set sessionoptions=blank,buffers,curdir,resize,winpos,winsize

au VimLeave * call SaveVimProject()
function! SaveVimProject()
    if filereadable("./Project.vim")
        mksession! Project.vim
    endif
endfunction
```

The first line puts all the swap files created by Vim into one directory, therefore kkeeping your working directory clean.

Vim uses `.viminfo` file to store information from the previous editing session. Adding `%` option to `viminfo` keeps the list of last opened buffers.

Another one of the most annoying things I discovered about Vim is that it didn't let me hide the buffer (e.g. by loading another one into the window) if the buffer was modified. It's the equivalent of a normal editor not letting you switch to another tab unless you save the current file. Setting the `hidden` flag fixed this issue (Vim still complained if I wanted to close it with unsaved modifications, but that's the behavior I wanted to keep).

What comes next is my attempt to add project management to Vim. The `mksession` command creates a file with current session information. What exactly is stored in that file is defined by `sessionoptions`. I chose to store the empty windows, all of the buffers (not only the ones displayed in windows), current directory (very useful for file searching, which will be explained in a moment), size and position of the whole Vim window (useful for GVim), and the sizes of all open windows. That combination is sufficient for me to feel that I pick up the project where I left off.

To automate project management a bit, I created a function. It detects the `Project.vim` file in the current directory, and if it finds one, it overwrites it with current session settings. This function is run automatically when exiting Vim. So, to create a new project, you need to navigate to a directory with the project files and create a `Project.vim` file manually, thus declaring it a project:

```vim
:cd /path/to/your/project
:mksession Project.vim
```

When you leave Vim, the project will be automatically saved. Next time you want to work on it again, all you have to do to open the project file and all your opened windows and files will be restored:

```vim
:so /path/to/your/project/Project.vim
```



```vim
Plugin 'ctrlpvim/ctrlp.vim'
```

```vim
let g:ctrlp_cmd = 'CtrlPMixed'
let g:ctrlp_working_path_mode = 0
let g:ctrlp_max_files=0
let g:ctrlp_custom_ignore = '__pycache__\|node_modules'

map \ :CtrlPLine<cr>
```

### Windows

Vim lets you split the window easily with 

```vim
map <a-l> :res +1<cr>
map <a-L> :res -1<cr>
map <a-h> :vertical res +1<cr>
map <a-H> :vertical res -1<cr>

map <a-j> :m+1<cr>
map <a-k> :m-2<cr>

set cursorline
set colorcolumn=80
set nu
set autoread
set guioptions-=m
set shortmess+=I

nnoremap j gj
nnoremap k gk
```

### Indentation

```vim
au FileType python setl ts=4 sw=4 sts=4 et
au FileType javascript,htmldjango,html,css,cucumber setl ts=2 sw=2 sts=2 et
```

### Status line

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

Plugin 'mgedmin/pythonhelper.vim'

### Syntax

Plugin 'scrooloose/syntastic'

```vim
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0
let g:syntastic_python_checkers = ['flake8']
let g:syntastic_python_flake8_exec = 'python3'
let g:syntastic_python_flake8_args = ['-m', 'flake8']
let g:syntastic_javascript_checkers = ['eslint']
let g:syntastic_javascript_eslint_exec = 'eslint'

map <leader>s :SyntasticToggleMode<cr>
```



### Whitespaces

```vim
set list
set listchars=tab:>-,trail:~
set smartindent

map <leader>l :set list!<cr>
```

### Color scheme

```vim
syntax enable
set background=dark
colorscheme gruvbox
```

### Other

```vim
command! XmlPrettyPrint :%!xmllint --format -
command! JsonPrettyPrint :%!python -m json.tool
command! Bd :bp<bar>bd#
```
Plugin 'jiangmiao/auto-pairs'
Plugin 'tpope/vim-surround'
Plugin 'tpope/vim-abolish'
Plugin 'scrooloose/nerdcommenter'

### Git

Plugin 'airblade/vim-gitgutter'
Plugin 'tpope/vim-fugitive'

### Python

Plugin 'fisadev/vim-isort'
Plugin 'davidhalter/jedi-vim'
Plugin 'python-rope/ropevim'
Plugin 'mgedmin/pythonhelper.vim'

```vim
au FileType python map <buffer> <leader>b oimport ipdb; ipdb.set_trace()<esc>
au FileType python map <buffer> <leader>B Oimport ipdb; ipdb.set_trace()<esc>
```

### Summary
