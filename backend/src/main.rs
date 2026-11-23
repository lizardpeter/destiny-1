//! d1-backend: replacement online services for Destiny 1 under d1-native.
//!
//! d1-native resolves Bungie, DemonWare and PSN hostnames to this server (`D1_BACKEND`)
//! and sends libSceHttp requests to it as plain HTTP with the original `Host` header.
//! Each service lives in its own module; the HTTP front routes by `Host` and path.
//! It never talks to the real services.

mod account;
mod ah;
mod bap;
mod content;
mod gear;
mod invest;
mod npwebapi;
mod pb;
mod psn;
mod signon;

use axum::{extract::Request, http::StatusCode, response::IntoResponse, routing::any, Router};
use clap::Parser;
use std::net::{Ipv4Addr, SocketAddr};
use std::sync::Arc;
use tracing::{info, warn};

#[derive(Parser, Debug, Clone)]
#[command(about = "Replacement online services for Destiny 1 under d1-native")]
struct Args {
    /// Address to listen on (use 0.0.0.0 to serve another machine).
    #[arg(long, env = "D1B_BIND", default_value = "127.0.0.1")]
    bind: String,
    /// HTTP port; must match d1-native's D1_BACKEND_HTTP_PORT.
    #[arg(long, env = "D1B_HTTP_PORT", default_value_t = 8080)]
    http_port: u16,
    /// Address the game should connect to for the services after sign-on (this machine
    /// as the client sees it).
    #[arg(long, env = "D1B_PUBLIC_IP", default_value = "127.0.0.1")]
    public_ip: Ipv4Addr,
    /// TCP port of the post-sign-on service.
    #[arg(long, env = "D1B_BAP_PORT", default_value_t = 7400)]
    bap_port: u16,
    /// Package list (one .pkg name per line). Optional: by default every .pkg in
    /// --packages-dir is used. The content manifest registers these packages.
    #[arg(long, env = "D1B_PACKAGES")]
    packages: Option<std::path::PathBuf>,
    /// Directory with the package files, normally `<game dir>/packages` (only read).
    #[arg(long, env = "D1B_PACKAGES_DIR")]
    packages_dir: Option<std::path::PathBuf>,
    /// Where the account (characters) is saved. Without it nothing is kept between runs.
    #[arg(long, env = "D1B_DATA_DIR")]
    data_dir: Option<std::path::PathBuf>,
}

/// State shared by all handlers.
pub struct Config {
    pub public_ip: Ipv4Addr,
    pub bap_port: u16,
    /// Content build the client reports (`networking:sku_manager: base content version`).
    pub content_version: String,
    /// Content manifest URL handed out in the client config (must be a routed hostname).
    pub manifest_url: String,
    pub packages: Vec<content::Package>,
}
pub type Shared = Arc<Config>;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .init();
    let args = Args::parse();
    account::init(args.data_dir.clone());
    npwebapi::init(args.data_dir.clone());

    let st: Shared = Arc::new(Config {
        public_ip: args.public_ip,
        bap_port: args.bap_port,
        content_version: "56578-1-3407992".into(),
        manifest_url: "http://cdn.signon.deadorbit.net/content/manifest".into(),
        packages: match (&args.packages, &args.packages_dir) {
            (_, None) => Vec::new(),
            (Some(list), Some(dir)) => content::load_packages(&std::fs::read_to_string(list).expect("read packages list"), dir),
            (None, Some(dir)) => {
                let names: Vec<String> = std::fs::read_dir(dir)
                    .expect("read packages dir")
                    .filter_map(|e| e.ok()?.file_name().into_string().ok())
                    .collect();
                content::load_packages(&names.join("\n"), dir)
            }
        },
    });
    info!("{} patchable packages in the content manifest", st.packages.len());
    let bap = tokio::net::TcpListener::bind(format!("{}:{}", args.bind, args.bap_port)).await.expect("bind bap");
    info!("d1-backend BAP (stub) on {}:{} tcp+udp", args.bind, args.bap_port);
    tokio::spawn(bap::serve(bap));
    let bap_udp = tokio::net::UdpSocket::bind(format!("{}:{}", args.bind, args.bap_port)).await.expect("bind bap udp");
    tokio::spawn(bap::serve_udp(bap_udp));
    // Activity host: the client reaches it with a second BAP connection ("FAH"), at the
    // address the get-activity-host-proxy reply names.
    let ah = tokio::net::TcpListener::bind(format!("{}:{}", args.bind, bap::AH_PORT)).await.expect("bind activity host");
    info!("d1-backend activity host on {}:{}", args.bind, bap::AH_PORT);
    tokio::spawn(bap::serve_ah(ah));

    let app = Router::new()
        .route("/2.0/oauth/token", any(psn::oauth_token))
        .route("/SignOn", any(signon::sign_on))
        .route("/content/manifest", any(content::manifest))
        .route("/npwebapi/:group/*path", any(npwebapi::request))
        .fallback(any(unhandled))
        .with_state(st);

    let addr: SocketAddr = format!("{}:{}", args.bind, args.http_port).parse().expect("bind address");
    info!("d1-backend HTTP on {addr}");
    let listener = tokio::net::TcpListener::bind(addr).await.expect("bind");
    axum::serve(listener, app).await.expect("serve");
}

/// Logs requests nothing handles yet, so the next protocol step is visible.
async fn unhandled(req: Request) -> impl IntoResponse {
    let host = req.headers().get("host").and_then(|h| h.to_str().ok()).unwrap_or("?").to_string();
    let (parts, body) = req.into_parts();
    let body = axum::body::to_bytes(body, 1 << 20).await.unwrap_or_default();
    warn!(
        "unhandled {} http://{}{} headers={:?} body={:?}",
        parts.method,
        host,
        parts.uri,
        parts.headers,
        String::from_utf8_lossy(&body[..body.len().min(2048)])
    );
    StatusCode::NOT_IMPLEMENTED
}
