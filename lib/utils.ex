defmodule Utils do
  def pinurl_to_imageurl(url) do
    filename = Path.basename(url)
    first = String.slice(filename, 0, 1)
    "pins/#{first}/#{filename}"
  end


  def on_exception(fun, max_retries \\ 3, retry_count \\ 0) do
    try do
      fun.()
    rescue
      exception ->
        if retry_count < max_retries do
          IO.puts("Retrying due to #{inspect(exception)} - Attempt #{retry_count + 1}")
          on_exception(fun, max_retries, retry_count + 1)
        else
          {:error, exception}
        end
    end
  end

end
