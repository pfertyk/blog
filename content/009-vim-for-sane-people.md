Title: Vim for sane people
Date: 2017-08-09
Summary: When you want something powerful but also something normal
Tags: vim

Long time ago, I decided to master Vim. Like many before me, I started with the vimtutor to learn the basics, then played around with the editor a bit and attempted to use it for actual work. I soon realized that it will not be that simple. Vim's commands were powerful, but required some time getting used to. I knew I had to spend a lot more time to become proficient enough to use Vim as my main text editor.

But there was also something else.

Vim was significantly different than other editors I used by far. Things I took for granted become difficult. Keeping the list of previously opened files? Not easy. Searching in the whole document? Unintuitive. Pasting content from the clipboard? I had to use a mouse for that. A mouse in Vim! All of those problems made me come back to other editors and not spend enough time to master Vim.

I realized that those problems were the ones that kept me from using Vim on daily basis. I had to solve them, otherwise I would keep coming back to other editors and never really master Vim. So I searched through documentation and available plugins and, after many days of tweaking my `.vimrc` file, I finally came up with configuration that made Vim an editor I could use.

Note: I'm a Python/JavaScript developer, so part of my configuration is prepared especially for those languages. But you can still find some useful hints if you are using a different language.

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

Leader is a special key in Vim. It's a prefix for sequences of keys that you can map to a command. Unlike shortcuts, you don't have to press all keys simultaneously, but one after another quickly. By default, the leader key is the backslash. But you are going to use the leader key very often, so it should be changed to something more convinient, something that you can use with any hand, something bigger than the usual key. Space key is an excellent choice:

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

### Windows

Vim lets you 

```vim
map <a-j> :m+1<cr>
map <a-k> :m-2<cr>
map <a-l> :res +1<cr>
map <a-L> :res -1<cr>
map <a-h> :vertical res +1<cr>
map <a-H> :vertical res -1<cr>

set cursorline
set colorcolumn=80
set nu
set autoread
set guioptions-=m
set shortmess+=I

nnoremap j gj
nnoremap k gk
```

### Buffers and sessions

```vim
set hidden
```

```vim
set sessionoptions=blank,buffers,curdir,resize,winpos,winsize

set directory^=$HOME/.vim/swp//
set viminfo^=%
set hidden

au VimLeave * call SaveVimProject()
function! SaveVimProject()
    if filereadable("./Project.vim")
        mksession! Project.vim
    endif
endfunction
```

Plugin 'ctrlpvim/ctrlp.vim'

```vim
let g:ctrlp_cmd = 'CtrlPMixed'
let g:ctrlp_working_path_mode = 0
let g:ctrlp_max_files=0
let g:ctrlp_custom_ignore = '__pycache__\|node_modules'

map \ :CtrlPLine<cr>
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
