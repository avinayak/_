defmodule Underscore do
  alias Underscore.{
    Html,
    Pins,
    Store
  }

  def main do
    Store.write_object("underscore", "pins.json", Pins.fetch_and_store_pins())

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

    IO.puts("Generating Pages")
    File.rm_rf!("pages")
    File.mkdir_p!("pages")

    pin_chunks =
      Enum.sort_by(pins, & &1["id"])
      |> Enum.reverse()
      |> Enum.chunk_every(100)

    n_pages = Enum.count(pin_chunks) - 1

    pin_chunks
    |> Enum.with_index()
    |> Enum.each(fn {pins, index} ->
      IO.write(".")

      html =
        Html.make_html(index,
          image_urls: Enum.map(pins, & &1["img_src"]),
          total_pages: n_pages
        )

      File.write!("pages/#{index}.html", html)
    end)

    IO.puts("Done")
  end
end
