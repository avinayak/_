defmodule UnderscoreTest do
  use ExUnit.Case
  doctest Underscore

  test "greets the world" do
    assert Underscore.hello() == :world
  end
end
