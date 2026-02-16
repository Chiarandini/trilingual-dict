-- Trilingual Dictionary Neovim Plugin
-- Initialization and command registration

vim.api.nvim_create_user_command('Dict', function(opts)
    require('tridict').search(opts.args)
end, {
    nargs = 1,
    desc = 'Search trilingual dictionary'
})

-- Optional: Set up keybinding for word under cursor
vim.api.nvim_create_user_command('DictWord', function()
    local word = vim.fn.expand('<cword>')
    require('tridict').search(word)
end, {
    desc = 'Search dictionary for word under cursor'
})
