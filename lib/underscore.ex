defmodule Underscore do
  alias Underscore.{
    Html,
    Pins,
    Store
  }

  def main do
    # Store.write_object("underscore", "pins.json", Pins.fetch_and_store_pins())

    store_pin_keys = Store.downloaded_pin_keys()
    pins = Store.retrieve_pins()

    download_pins =
      Enum.filter(pins, fn pin ->
        !Store.has_already_been_downloaded?(store_pin_keys, pin["url"])
      end)

    IO.puts("Downloading #{Enum.count(download_pins)} pins")

    download_pins
    |> Enum.with_index()
    |> Enum.each(fn {pin, index} ->
      percentage = index / Enum.count(download_pins) * 100
      IO.puts("* #{index}/#{Enum.count(download_pins)} - #{percentage}% - #{pin["grid_title"]}")

      Utils.on_exception(fn ->
        Store.download_and_store(pin["url"])
      end)
    end)

    Html.make_html(pins)

    IO.puts("Done")
  end
end
