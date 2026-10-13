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
//!
//! Secure hello response payload (decrypt 0xB34FE0, keys from sign-on fields 2 and 3):
//! ```text
//! u32 BE L | IV[16] | AES-128-CBC(PKCS#7) ciphertext[L-48] | HMAC-SHA256[32]
//! ```
//! The MAC covers bytes [0, L-28), length prefix included. The plaintext starts with a
//! 12-byte nonce and a 16-byte channel key (0x6CF80). From then on the channel is
//! AES-128-GCM (libtomcrypt; encrypt 0x6CD20, decrypt 0x6CE20): no AAD, 16-byte tag, one
//! nonce per direction, incremented as a little-endian counter after every message. The
//! client flips bit 0 of byte 11 of its *send* nonce, so the server sends with the nonce as
//! given and receives with byte 11 ^ 1. Encrypted envelope (kind 1): tag[16] + ciphertext of
//! header + payload; the envelope length includes the tag. Types 0x19 and 0x1E always go
//! in the clear.

use crate::{pb, signon};
use aes_gcm::{aead::AeadInPlace, Aes128Gcm, KeyInit};
use cbc::cipher::{BlockEncryptMut, KeyIvInit};
use hmac::{Hmac, Mac};
use rand::RngCore;
use sha2::Sha256;
use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::{TcpListener, TcpStream, UdpSocket},
};
use tracing::{info, warn};

pub const MSG_CHANNEL_STARTUP_REQUEST: u16 = 0x1E;
pub const MSG_CHANNEL_STARTUP_RESPONSE: u16 = 0x1F;
pub const MSG_SECURE_HELLO_REQUEST: u16 = 0x19;
pub const MSG_SECURE_HELLO_RESPONSE: u16 = 0x1A;
pub const MSG_SUBSCRIPTION_REQUEST: u16 = 12;
pub const MSG_UNSUBSCRIBE_REQUEST: u16 = 14;
pub const MSG_QUEUEZ_REGISTER_REQUEST: u16 = 121;
pub const MSG_REGISTER_RELAY_CLIENT_REQUEST: u16 = 302;
pub const STATUS_OK: u16 = 200;

/// Message type ids (vtable slot 0 of each c_investment_bap_message_* class; slot 1 is the
/// header class, 1 = request, 2 = response; slots 2/3 encode/decode the payload).
fn name(kind: u16) -> &'static str {
    match kind {
        6 => "activity_host_manager_request",
        8 => "activity_host_notification",
        9 => "bap_to_client_notification",
        10 => "world_server_request",
        12 => "subscription_request",
        14 => "unsubscribe_request",
        16 => "get_activity_host_proxy_request",
        18 => "client_config_request",
        21 => "update_purchased_offers_request",
        23 => "account_id_translation_request",
        25 => "secure_hello_request",
        29 => "server_challenge_response",
        30 => "channel_startup_request",
        33 => "user_message_response",
        34 => "update_matchmaking_skill_request",
        36 => "friends_update_request",
        38 => "party_invite_request",
        40 => "check_party_invite_request",
        42 => "update_matchmaking_core_request",
        44 => "clan_request",
        46 => "nat_punch_request",
        121 => "queuez_register_request",
        171 => "xetrov_request",
        250 => "echo_request",
        300 => "initiate_relay_connection_notification",
        302 => "register_relay_client_request",
        _ => "?",
    }
}

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

/// Channel state after the secure hello: AES-128-GCM with per-direction nonces.
struct Channel {
    gcm: Aes128Gcm,
    send_nonce: [u8; 12],
    recv_nonce: [u8; 12],
}

fn bump(n: &mut [u8; 12]) {
    for b in n.iter_mut() {
        *b = b.wrapping_add(1);
        if *b != 0 {
            break;
        }
    }
}

impl Channel {
    fn new(key: &[u8; 16], nonce: [u8; 12]) -> Self {
        let mut recv_nonce = nonce;
        recv_nonce[11] ^= 1;
        Channel { gcm: Aes128Gcm::new(key.into()), send_nonce: nonce, recv_nonce }
    }

    fn open(&mut self, body: &[u8]) -> Option<Vec<u8>> {
        if body.len() < 16 {
            return None;
        }
        let (tag, ct) = body.split_at(16);
        let mut buf = ct.to_vec();
        self.gcm
            .decrypt_in_place_detached((&self.recv_nonce).into(), &[], &mut buf, tag.into())
            .ok()?;
        bump(&mut self.recv_nonce);
        Some(buf)
    }

    fn seal(&mut self, msg: &[u8]) -> Vec<u8> {
        let mut buf = msg.to_vec();
        let tag = self
            .gcm
            .encrypt_in_place_detached((&self.send_nonce).into(), &[], &mut buf)
            .expect("gcm encrypt");
        bump(&mut self.send_nonce);
        let mut out = Vec::with_capacity(6 + 16 + buf.len());
        out.push(1);
        out.push(1);
        out.extend_from_slice(&((16 + buf.len()) as u32).to_be_bytes());
        out.extend_from_slice(&tag);
        out.extend_from_slice(&buf);
        out
    }
}

fn plain(msg: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(6 + msg.len());
    out.push(1);
    out.push(2);
    out.extend_from_slice(&(msg.len() as u32).to_be_bytes());
    out.extend_from_slice(msg);
    out
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

/// Secure hello response payload carrying the channel nonce and key (see module docs).
fn hello_payload(nonce: &[u8; 12], key: &[u8; 16]) -> Vec<u8> {
    let mut pt = Vec::with_capacity(28);
    pt.extend_from_slice(nonce);
    pt.extend_from_slice(key);
    let mut iv = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut iv);
    let ct = cbc::Encryptor::<aes::Aes128>::new((&signon::SESSION_AES_KEY).into(), (&iv).into())
        .encrypt_padded_vec_mut::<cbc::cipher::block_padding::Pkcs7>(&pt);
    let l = (16 + ct.len() + 32) as u32; // bytes after the length field
    let mut out = Vec::with_capacity(4 + l as usize);
    out.extend_from_slice(&l.to_be_bytes());
    out.extend_from_slice(&iv);
    out.extend_from_slice(&ct);
    let mut mac = <Hmac<Sha256> as Mac>::new_from_slice(&signon::SESSION_HMAC_KEY).unwrap();
    mac.update(&out);
    out.extend_from_slice(&mac.finalize().into_bytes());
    out
}

/// Send a message: encrypted once the channel is keyed.
async fn send(sock: &mut TcpStream, chan: &mut Option<Channel>, msg: &[u8]) -> std::io::Result<()> {
    let out = match chan.as_mut() {
        Some(c) => c.seal(msg),
        None => plain(msg),
    };
    sock.write_all(&out).await
}

async fn session(mut sock: TcpStream) -> std::io::Result<()> {
    let mut chan: Option<Channel> = None;
    loop {
        let env = read_envelope(&mut sock).await?;
        let body = if env.kind == 1 {
            match chan.as_mut().and_then(|c| c.open(&env.body)) {
                Some(b) => b,
                None => {
                    warn!("bap: encrypted envelope ({} bytes) failed to open: {}", env.body.len(),
                          pb::hex(&env.body[..env.body.len().min(64)]));
                    continue;
                }
            }
        } else {
            env.body
        };
        if body.len() < 6 {
            warn!("bap: short message {}", pb::hex(&body));
            continue;
        }
        let kind = u16::from_be_bytes([body[0], body[1]]);
        let sequence = u32::from_be_bytes([body[2], body[3], body[4], body[5]]);
        let payload = &body[6..];
        let enc = if env.kind == 1 { "encrypted " } else { "" };
        match kind {
            MSG_CHANNEL_STARTUP_REQUEST => {
                info!("bap: channel startup request (seq {sequence}, {} bytes): {}", payload.len(),
                      pb::hex(&payload[..payload.len().min(16)]));
                let reply = [0x5Au8; 128];
                sock.write_all(&plain(&response(MSG_CHANNEL_STARTUP_RESPONSE, sequence, STATUS_OK, &reply))).await?;
            }
            MSG_SECURE_HELLO_REQUEST => {
                info!("bap: secure hello (seq {sequence})\n{}", pb::dump(payload, 2));
                let mut nonce = [0u8; 12];
                let mut key = [0u8; 16];
                rand::thread_rng().fill_bytes(&mut nonce);
                rand::thread_rng().fill_bytes(&mut key);
                let p = hello_payload(&nonce, &key);
                sock.write_all(&plain(&response(MSG_SECURE_HELLO_RESPONSE, sequence, STATUS_OK, &p))).await?;
                chan = Some(Channel::new(&key, nonce));
                info!("bap: channel keyed (AES-128-GCM)");
            }
            MSG_QUEUEZ_REGISTER_REQUEST | MSG_SUBSCRIPTION_REQUEST | MSG_UNSUBSCRIBE_REQUEST
            | MSG_REGISTER_RELAY_CLIENT_REQUEST => {
                // Responses with no payload (codec 0x1F70 on both sides).
                info!("bap: {} (seq {sequence}, {} bytes) -> ok\n{}", name(kind), payload.len(), pb::dump(payload, 2));
                let reply = response(kind + 1, sequence, STATUS_OK, &[]);
                send(&mut sock, &mut chan, &reply).await?;
            }
            _ => warn!("bap: {enc}message {} ({kind}) seq {sequence} ({} bytes, unhandled): {}\n{}", name(kind), payload.len(),
                       pb::hex(&payload[..payload.len().min(256)]), pb::dump(payload, 2)),
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
