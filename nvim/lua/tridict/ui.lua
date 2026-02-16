-- UI module for displaying dictionary results

local M = {}

local namespace = vim.api.nvim_create_namespace('tridict')

function M.show(data)
    if not data or not data.outputs then
        vim.notify('No results found', vim.log.levels.WARN)
        return
    end

    -- Find Japanese and Chinese outputs
    local ja_output, zh_output
    for _, output in ipairs(data.outputs) do
        if output.language == 'ja' then
            ja_output = output
        elseif output.language == 'zh' then
            zh_output = output
        end
    end

    -- Create floating windows
    local width = vim.o.columns
    local height = vim.o.lines
    local win_width = math.floor(width * 0.4)
    local win_height = math.floor(height * 0.6)

    -- Create two side-by-side buffers
    local ja_buf = vim.api.nvim_create_buf(false, true)
    local zh_buf = vim.api.nvim_create_buf(false, true)

    -- Japanese window (left)
    local ja_win = vim.api.nvim_open_win(ja_buf, true, {
        relative = 'editor',
        width = win_width,
        height = win_height,
        row = math.floor((height - win_height) / 2),
        col = math.floor((width - win_width * 2 - 2) / 2),
        style = 'minimal',
        border = 'rounded',
        title = ' Japanese ',
        title_pos = 'center',
    })

    -- Chinese window (right)
    local zh_win = vim.api.nvim_open_win(zh_buf, false, {
        relative = 'editor',
        width = win_width,
        height = win_height,
        row = math.floor((height - win_height) / 2),
        col = math.floor((width - win_width * 2 - 2) / 2) + win_width + 2,
        style = 'minimal',
        border = 'rounded',
        title = ' Chinese ',
        title_pos = 'center',
    })

    -- Populate buffers
    M.populate_buffer(ja_buf, ja_output)
    M.populate_buffer(zh_buf, zh_output)

    -- Set buffer options
    for _, buf in ipairs({ja_buf, zh_buf}) do
        vim.api.nvim_buf_set_option(buf, 'modifiable', false)
        vim.api.nvim_buf_set_option(buf, 'buftype', 'nofile')
        vim.api.nvim_buf_set_option(buf, 'bufhidden', 'wipe')
        vim.api.nvim_buf_set_option(buf, 'filetype', 'tridict')
    end

    -- Set keymaps to close
    local close_fn = function()
        pcall(vim.api.nvim_win_close, ja_win, true)
        pcall(vim.api.nvim_win_close, zh_win, true)
    end

    for _, buf in ipairs({ja_buf, zh_buf}) do
        vim.keymap.set('n', 'q', close_fn, { buffer = buf, nowait = true })
        vim.keymap.set('n', '<Esc>', close_fn, { buffer = buf, nowait = true })
    end
end

function M.populate_buffer(buf, output)
    if not output then
        vim.api.nvim_buf_set_lines(buf, 0, -1, false, {'No results found'})
        return
    end

    local lines = {}

    -- Headword and reading
    local headword_line = output.headword
    if output.reading and output.reading ~= '' then
        headword_line = headword_line .. ' (' .. output.reading .. ')'
    end
    table.insert(lines, headword_line)
    table.insert(lines, '')

    -- Definition
    table.insert(lines, 'Definition:')
    table.insert(lines, '  ' .. output.definition)
    table.insert(lines, '')

    -- Metadata
    if output.meta then
        local meta_lines = {}
        if output.meta.jlpt_level then
            table.insert(meta_lines, 'JLPT: ' .. output.meta.jlpt_level)
        end
        if output.meta.hsk_level then
            table.insert(meta_lines, 'HSK: ' .. output.meta.hsk_level)
        end
        if output.meta.stroke_count then
            table.insert(meta_lines, 'Strokes: ' .. output.meta.stroke_count)
        end
        if output.meta.traditional then
            table.insert(meta_lines, 'Traditional: ' .. output.meta.traditional)
        end

        if #meta_lines > 0 then
            table.insert(lines, 'Metadata:')
            for _, line in ipairs(meta_lines) do
                table.insert(lines, '  ' .. line)
            end
            table.insert(lines, '')
        end
    end

    -- Examples
    if output.examples and #output.examples > 0 then
        table.insert(lines, 'Examples:')
        for i, ex in ipairs(output.examples) do
            table.insert(lines, string.format('  %d. %s', i, ex.source_text))
            table.insert(lines, string.format('     %s', ex.english_text))
            table.insert(lines, '')
        end
    end

    vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)

    -- Add highlighting
    vim.api.nvim_buf_add_highlight(buf, namespace, 'Title', 0, 0, -1)
end

return M
