defmodule Underscore.Html do
  import EEx

  def make_html(pins) do
    IO.puts("Generating Pages")
    File.rm_rf!("pages")
    File.mkdir_p!("pages")

    pin_chunks =
      Enum.sort_by(pins, & &1["id"])
      |> Enum.reverse()
      |> Enum.chunk_every(100)

    total_pages = Enum.count(pin_chunks) - 1
    {:ok, template} = File.read("template.html.eex")

    pin_chunks
    |> Enum.with_index()
    |> Enum.each(fn {cpins, index} ->
      IO.write(".")

      urls =
        Enum.map(cpins, fn pin ->
          pin["img_src"]
        end)

      filename =
        if index == 0 do
          "index.html"
        else
          "#{index}.html"
        end

      page_names =
        Enum.map(0..total_pages, fn i ->
          if i == 0 do
            "index.html"
          else
            "#{i}.html"
          end
        end)

      html =
        eval_string(template,
          filename: filename,
          page_index: index,
          image_urls: urls,
          page_names: page_names
        )

      File.write!("pages/#{filename}", html)
    end)
  end
end
