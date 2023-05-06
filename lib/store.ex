defmodule Underscore.Store do
  alias ExAws.S3

  def list_buckets do
    ExAws.Config.new(:s3)

    S3.list_buckets()
    |> ExAws.request!()
  end

  def list_objects(bucket_name) do
    list_objects(bucket_name, [])
  end

  defp list_objects(bucket_name, acc, marker \\ "") do
    {:ok, response} = S3.list_objects(bucket_name, marker: marker) |> ExAws.request()

    contents = response.body.contents
    is_truncated = response.body.is_truncated
    new_acc = acc ++ contents

    case is_truncated do
      "true" ->
        last_key = List.last(contents).key
        list_objects(bucket_name, new_acc, last_key)

      "false" ->
        new_acc
    end
  end

  def write_object(bucket, key, body) do
    S3.put_object(bucket, key, body)
    |> ExAws.request!()
  end



  def download_and_store(url) do
    {:ok, %{body: body}} = HTTPoison.get(url)
    write_object("underscore", Utils.pinurl_to_imageurl(url), body)
  end

  def has_already_been_downloaded?(downloaded_pins, url) do
    downloaded_pins |> Enum.member?(Utils.pinurl_to_imageurl(url))
  end

  def downloaded_pin_keys do
    downloaded_pins = list_objects("underscore")
    downloaded_pins |> Enum.map(& &1.key)
  end


  def retrieve_pins do
    %{body: body} = S3.get_object("underscore", "pins.json") |> ExAws.request!()
    Poison.decode!(body)
  end


end
