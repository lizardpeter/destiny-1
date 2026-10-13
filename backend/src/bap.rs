//! BAP: Bungie's account/"investment" service, the next server after sign-on (address and
//! port from the sign-on response). Client side: c_network_server_bap_connection
//! (eboot 0xB2E000-0xB35000); states _connecting, _channel_starting, _authenticating,
//! _setup_primary_register_subscriber, _setup_primary_register_relay_client, _connected.
//!
//! Wire format (TCP):
//! ```text
//! envelope   u8 version (1), u8 kind, u32 big-endian length          (reader 0xB2FA10)
//!            kind 2 (or 0): plaintext message of `length` bytes
//!            kind 1: 16-byte tag + encrypted message (length includes the tag)
//! message    header + payload
//! header     base (6 bytes): u16 BE message type (< 0x130), u32 BE sequence  (0xB34840)
//!            response header (8 bytes): base + u16 BE status (200 = ok)       (0x55DA10)
//! ```
//! Handshake (protocol request source 0xB33E80; request kind -> message id table 0x15E0A80):
//! - 0x1E channel startup request: 128 raw bytes ("DESTINY\x01" + 120 random bytes).
//!   Response 0x1F: exactly 128 raw bytes (decoder 0x562AA0).
//! - 0x1A secure hello request (schematized protobuf) / response: u32 BE length (< 93)
//!   + bytes (decoder 0x562C70), decrypted with the sign-on session keys (0xB32DB0) and
//!   used to set the channel encryption key.

use crate::pb;
use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::{TcpListener, TcpStream, UdpSocket},
};
use tracing::{info, warn};

pub const MSG_CHANNEL_STARTUP_REQUEST: u16 = 0x1E;
pub const MSG_CHANNEL_STARTUP_RESPONSE: u16 = 0x1F;
pub const STATUS_OK: u16 = 200;

pub async fn serve(listener: TcpListener) {
    loop {
        let Ok((sock, peer)) = listener.accept().await else { continue };
        tokio::spawn(async move {
            info!("bap: connection from {peer}");
            match session(sock).await {
                Ok(()) => info!("bap: {peer} closed"),
                Err(e) => info!("bap: {peer} ended: {e}"),
            }
        });
    }
}

struct Envelope {
    kind: u8,
    body: Vec<u8>,
}

async fn read_envelope(sock: &mut TcpStream) -> std::io::Result<Envelope> {
    let mut h = [0u8; 6];
    sock.read_exact(&mut h).await?;
    if h[0] != 1 {
        return Err(std::io::Error::other(format!("envelope version {}", h[0])));
    }
    let len = u32::from_be_bytes([h[2], h[3], h[4], h[5]]) as usize;
    if len > 1 << 20 {
        return Err(std::io::Error::other(format!("envelope length {len}")));
    }
    let mut body = vec![0u8; len];
    sock.read_exact(&mut body).await?;
    Ok(Envelope { kind: h[1], body })
}

async fn write_plain(sock: &mut TcpStream, msg: &[u8]) -> std::io::Result<()> {
    let mut out = Vec::with_capacity(6 + msg.len());
    out.push(1);
    out.push(2);
    out.extend_from_slice(&(msg.len() as u32).to_be_bytes());
    out.extend_from_slice(msg);
    sock.write_all(&out).await
}

/// Response message: response header (type, sequence, status) + payload.
fn response(kind: u16, sequence: u32, status: u16, payload: &[u8]) -> Vec<u8> {
    let mut m = Vec::with_capacity(8 + payload.len());
    m.extend_from_slice(&kind.to_be_bytes());
    m.extend_from_slice(&sequence.to_be_bytes());
    m.extend_from_slice(&status.to_be_bytes());
    m.extend_from_slice(payload);
    m
}

async fn session(mut sock: TcpStream) -> std::io::Result<()> {
    loop {
        let env = read_envelope(&mut sock).await?;
        if env.kind == 1 {
            warn!("bap: encrypted envelope ({} bytes), not handled yet: {}", env.body.len(),
                  pb::hex(&env.body[..env.body.len().min(64)]));
            continue;
        }
        if env.body.len() < 6 {
            warn!("bap: short message {}", pb::hex(&env.body));
            continue;
        }
        let kind = u16::from_be_bytes([env.body[0], env.body[1]]);
        let sequence = u32::from_be_bytes([env.body[2], env.body[3], env.body[4], env.body[5]]);
        let payload = &env.body[6..];
        match kind {
            MSG_CHANNEL_STARTUP_REQUEST => {
                info!("bap: channel startup request (seq {sequence}, {} bytes): {}", payload.len(),
                      pb::hex(&payload[..payload.len().min(16)]));
                let reply = [0x5Au8; 128];
                write_plain(&mut sock, &response(MSG_CHANNEL_STARTUP_RESPONSE, sequence, STATUS_OK, &reply)).await?;
            }
            _ => warn!("bap: message {kind:#x} seq {sequence} ({} bytes, unhandled): {}", payload.len(),
                       pb::hex(&payload[..payload.len().min(256)])),
        }
    }
}

/// UDP side of the same port (logged only; the client has not used it so far).
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
