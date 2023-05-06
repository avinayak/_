defmodule Mix.Tasks.Underscore do
  use Mix.Task

  def run(_) do
    Mix.Task.run("app.start")
    Underscore.main()
  end
end
