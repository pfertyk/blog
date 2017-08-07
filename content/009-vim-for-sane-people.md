Title: Vim for sane people
Date: 2017-08-09
Summary: Because not only your production code deserves tenderness
Tags: vim

Long time ago, I tried to learn Vim. I started with the vimtutor,

### Leader

Leader is a special key in Vim. By default, the leader key is the backslash.
But you are going to use the leader key very often, so it should be changed to something more convinient, something that you can use with any hand, something bigger than the usual key. Space key is an excellent choice:

```vim
let mapleader = ' '
```

### Windows

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

### Search

```vim
nnoremap / /\v
vnoremap / /\v
vnoremap // y/<c-r>"<cr>
set ignorecase
set smartcase
set gdefault
set hls
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

### Clipboard

One of the things that annoyed me the most when I started using Vim was copying and pasting text. Vim has its own registers, and they have nothing to do with clipboard. Fortunately, there is a way to fix it:

```vim
vmap <Leader>y "+y
vmap <Leader>d "+d
nmap <Leader>p "+p
nmap <Leader>P "+P
vmap <Leader>p "+p
vmap <Leader>P "+P
```



### Whitespaces

```vim
set list
set listchars=tab:>-,trail:~
set smartindent

map <leader>l :set list!<cr>
```

### Plugins

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
