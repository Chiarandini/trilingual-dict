-- Main tridict module

local M = {}

-- Configuration
M.config = {
    dict_binary = 'dict',
    db_path = nil, -- Auto-detect
}

function M.setup(opts)
    M.config = vim.tbl_deep_extend('force', M.config, opts or {})
end

function M.search(word)
    if not word or word == '' then
        vim.notify('No word provided', vim.log.levels.ERROR)
        return
    end

    -- Find dict binary
    local dict_cmd = M.config.dict_binary
    local handle = io.popen('which ' .. dict_cmd .. ' 2>/dev/null')
    if handle then
        local result = handle:read('*a')
        handle:close()
        if result == '' then
            -- Try project-relative path
            local project_root = vim.fn.getcwd()
            dict_cmd = project_root .. '/cmd/dict/dict'
        end
    end

    -- Execute dict command with JSON output
    local cmd = string.format('%s --json "%s"', dict_cmd, word)
    local output = vim.fn.system(cmd)

    if vim.v.shell_error ~= 0 then
        vim.notify('Dictionary lookup failed: ' .. output, vim.log.levels.ERROR)
        return
    end

    -- Parse JSON
    local ok, data = pcall(vim.json.decode, output)
    if not ok then
        vim.notify('Failed to parse dictionary output', vim.log.levels.ERROR)
        return
    end

    -- Show UI
    require('tridict.ui').show(data)
end

return M
