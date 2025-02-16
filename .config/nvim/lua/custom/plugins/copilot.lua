return {
  'github/copilot.vim',
  config = function()
    vim.api.nvim_create_autocmd('BufRead', {
      pattern = '*',
      callback = function()
        local project_root = vim.fn.getcwd() -- Use the current working directory
        vim.g.copilot_workspace_folders = { project_root }
      end,
    })
  end,
}
