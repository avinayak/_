defmodule Underscore.Pins do
  alias Pinbacker

  def fetch_pins do
    pins = Pinbacker.metadata("https://www.pinterest.jp/atulvinayak/")

    board_pins =
      pins
      |> Enum.map(fn {:ok, _,
                      %{
                        board_pins: boardp
                      }} ->
        boardp
      end)

    section_pins =
      pins
      |> Enum.map(fn {:ok, _,
                      %{
                        section_pins: secp
                      }} ->
        secp |> Map.values() |> List.flatten()
      end)
      |> List.flatten()

    section_pins ++ board_pins
  end

  def map_pin(pin) do
    orig_url = pin["images"]["orig"]["url"]

    %{
      "id" => pin["id"],
      "grid_title" => pin["grid_title"],
      "dominant_color" => pin["dominant_color"],
      "url" => orig_url,
      "link" => pin["link"],
      "img_src" =>
        "https://pub-f2874ecc07e640469d2fd159ae738e39.r2.dev/#{Utils.pinurl_to_imageurl(orig_url)}"
    }
  end

  def fetch_and_store_pins do
    Utils.on_exception(&fetch_pins/0)
    |> List.flatten()
    |> Enum.map(&map_pin/1)
    |> Poison.encode!()
  end
end
