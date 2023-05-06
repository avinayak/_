defmodule Underscore.Html do
  import EEx

  def make_html(index, image_urls: image_urls, total_pages: total_pages) do
    {:ok, template} = File.read("template.html.eex")
    eval_string(template, index: index, image_urls: image_urls, total_pages: total_pages)
  end
end
