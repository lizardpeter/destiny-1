//! Next service after sign-on (address handed out in the sign-on response). Protocol not
//! yet known: for now accept connections and log what the client sends.

use crate::pb;
use tokio::{io::AsyncReadExt, net::{TcpListener, UdpSocket}};
use tracing::{info, warn};

pub async fn serve(listener: TcpListener) {
    loop {
        let Ok((mut sock, peer)) = listener.accept().await else { continue };
        tokio::spawn(async move {
            info!("bap: connection from {peer}");
            let mut buf = vec![0u8; 65536];
            loop {
                match sock.read(&mut buf).await {
                    Ok(0) => {
                        info!("bap: {peer} closed");
                        return;
                    }
                    Ok(n) => warn!("bap: {peer} sent {n} bytes (unhandled): {}", pb::hex(&buf[..n.min(512)])),
                    Err(e) => {
                        info!("bap: {peer} error {e}");
                        return;
                    }
                }
            }
        });
    }
}

/// UDP side of the same port: the client's BAP status counts datagrams ("packets").
pub async fn serve_udp(sock: UdpSocket) {
    let mut buf = vec![0u8; 65536];
    let mut seen = 0u64;
    loop {
        let Ok((n, peer)) = sock.recv_from(&mut buf).await else { continue };
        seen += 1;
        if seen <= 50 || seen % 100 == 0 {
            warn!("bap/udp: #{seen} {n} bytes from {peer} (unhandled): {}", pb::hex(&buf[..n.min(256)]));
        }
    }
}
