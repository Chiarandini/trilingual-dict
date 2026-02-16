# TriDict Neovim Plugin

Trilingual dictionary lookup inside Neovim.

## Installation

### Using [lazy.nvim](https://github.com/folke/lazy.nvim)

```lua
{
    dir = '~/trilingual-dict/nvim',
    config = function()
        require('tridict').setup({
            dict_binary = 'dict',  -- or path to binary
        })
    end,
}
```

### Using [packer.nvim](https://github.com/wbthomason/packer.nvim)

```lua
use {
    '~/trilingual-dict/nvim',
    config = function()
        require('tridict').setup()
    end
}
```

### Manual Installation

```bash
ln -s ~/trilingual-dict/nvim ~/.config/nvim/pack/plugins/start/tridict
```

## Usage

```vim
:Dict cat              " Look up English word
:Dict 猫               " Look up Japanese/Chinese
:Dict ねこ             " Look up by reading
:DictWord              " Look up word under cursor
```

### Keybindings (in dictionary window)

- `q` - Close window
- `<Esc>` - Close window

## Optional Keymaps

Add to your `init.lua`:

```lua
vim.keymap.set('n', '<leader>d', ':DictWord<CR>', { desc = 'Dictionary lookup' })
```

## Requirements

- Neovim 0.8+
- `dict` binary in PATH (or specify path in setup)
- `dictionary.db` in project root or `~/.tridict/`
