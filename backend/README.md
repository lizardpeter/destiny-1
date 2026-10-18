# d1-backend — replacement online services for Destiny 1 (d1-native)

Runs the services the game talks to, so d1-native can sign in without Bungie's or
Sony's servers. Same machine for now; to serve another machine, bind to `0.0.0.0`
and set `--public-ip` to the address clients use.

```bash
cargo run --release -- --packages /path/packages.txt --packages-dir /path/app0/packages
# game side
D1_BACKEND=127.0.0.1 D1_BYPASS=prereq,transport d1-native --eboot ... --app0 /path/app0 ...
```

| service | how the game reaches it | module |
|---|---|---|
| PSN OAuth token | `POST https://auth.api.sp-int.ac.playstation.net/2.0/oauth/token` | `psn.rs` |
| Bungie sign-on | `POST https://www*.signon.{deadorbit,gravityshavings}.net/SignOn` (protobuf) | `signon.rs` |
| content manifest | URL from the sign-on client config (id 100) | `content.rs` |
| BAP | TCP address from the sign-on response (stub: logs traffic) | `bap.rs` |

Status: the game signs on, passes `content_check` and `package_registration`, and
reaches `bootflow:bap_signin`. The protocol notes live in each module and in
`findings/LOG.md`.
