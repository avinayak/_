import Config
import Dotenvy

source!([".env", System.get_env()])


config :ex_aws,
  access_key_id: env!("AWS_ACCESS_KEY_ID", :string!), #{:system, "AWS_ACCESS_KEY_ID"},
  secret_access_key: env!("AWS_SECRET_ACCESS_KEY", :string!)# {:system, "AWS_SECRET_ACCESS_KEY"}

config :ex_aws, :s3,
  scheme: "https://",
  host: env!("CLOUDFLARE_HOST", :string!)
