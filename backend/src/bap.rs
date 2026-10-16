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

use crate::{ah, invest, pb, signon};
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
pub const MSG_WORLD_SERVER_REQUEST: u16 = 10;
pub const MSG_WORLD_SERVER_RESPONSE: u16 = 11;
pub const MSG_ECHO_REQUEST: u16 = 250;
pub const MSG_UPDATE_PURCHASED_OFFERS_REQUEST: u16 = 21;
pub const MSG_USER_MESSAGE_REQUEST: u16 = 32;
pub const MSG_ACCOUNT_ID_TRANSLATION_REQUEST: u16 = 23;
pub const MSG_CLIENT_CONFIG_REQUEST: u16 = 18;
pub const MSG_QUEUEZ_UPDATE_NOTIFICATION: u16 = 123;
pub const MSG_QUEUEZ_REGISTER_REQUEST: u16 = 121;
pub const MSG_REGISTER_RELAY_CLIENT_REQUEST: u16 = 302;
/// bap_to_client_notification: activity host messages as the client receives them (push
/// policy 0x565440). Notification 100 (activity_host_to_client) is the AH-side form, which
/// the client would only relay onward to the service named in its header.
pub const MSG_BAP_TO_CLIENT: u16 = 9;
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
        32 => "user_message_request",
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

/// TCP port of the activity host (a second BAP endpoint).
pub const AH_PORT: u16 = 7500;
/// Identifier of our (single) activity host instance.
pub const AH_HOST_ID: u64 = 0x4D31_4148_0000_0001;

pub async fn serve(listener: TcpListener) {
    serve_role(listener, Role::Primary).await
}
pub async fn serve_ah(listener: TcpListener) {
    serve_role(listener, Role::ActivityHost).await
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Role {
    Primary,
    ActivityHost,
}

async fn serve_role(listener: TcpListener, role: Role) {
    loop {
        let Ok((sock, peer)) = listener.accept().await else { continue };
        tokio::spawn(crate::account::PLAYER.scope(std::cell::RefCell::new(None), async move {
            info!("bap: {role:?} connection from {peer}");
            match session(sock, role).await {
                Ok(()) => info!("bap: {peer} closed"),
                Err(e) => info!("bap: {peer} ended: {e}"),
            }
        }));
    }
}

struct Envelope {
    kind: u8,
    body: Vec<u8>,
}

async fn read_envelope(sock: &mut (impl AsyncReadExt + Unpin)) -> std::io::Result<Envelope> {
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

/// Notification message: base header (type, sequence) + payload.
fn notification(kind: u16, sequence: u32, payload: &[u8]) -> Vec<u8> {
    let mut m = Vec::with_capacity(6 + payload.len());
    m.extend_from_slice(&kind.to_be_bytes());
    m.extend_from_slice(&sequence.to_be_bytes());
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
async fn send(sock: &mut (impl AsyncWriteExt + Unpin), chan: &mut Option<Channel>, msg: &[u8]) -> std::io::Result<()> {
    let out = match chan.as_mut() {
        Some(c) => c.seal(msg),
        None => plain(msg),
    };
    sock.write_all(&out).await
}

async fn session(sock: TcpStream, role: Role) -> std::io::Result<()> {
    let mut chan: Option<Channel> = None;
    let mut notify_seq: u32 = 0;
    let mut ah_state = ah::Host::default();
    // Envelopes are read in their own task (read_exact is not cancel-safe) so the loop can
    // also wake for periodic host messages.
    let (mut rd, mut sock) = sock.into_split();
    let (tx, mut rx) = tokio::sync::mpsc::channel::<std::io::Result<Envelope>>(64);
    tokio::spawn(async move {
        loop {
            let r = read_envelope(&mut rd).await;
            let end = r.is_err();
            if tx.send(r).await.is_err() || end {
                break;
            }
        }
    });
    let mut tick = tokio::time::interval(ah::KEEPALIVE_INTERVAL);
    loop {
        let env = tokio::select! {
            r = rx.recv() => match r {
                Some(r) => r?,
                None => return Ok(()),
            },
            _ = tick.tick() => {
                if role == Role::ActivityHost && chan.is_some() {
                    for (ty, data) in ah_state.keepalive() {
                        notify_seq += 1;
                        let msg = notification(MSG_BAP_TO_CLIENT, notify_seq, &ah::host_payload(AH_HOST_ID, ty, &data));
                        send(&mut sock, &mut chan, &msg).await?;
                    }
                }
                continue;
            }
        };
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
                // field 1: the sign-on security token, "d1-backend:<online id>"
                if let Some(name) = crate::pb::first_bytes(payload, 1)
                    .and_then(|t| String::from_utf8(t).ok())
                    .and_then(|t| t.strip_prefix("d1-backend:").map(str::to_string))
                {
                    crate::account::set_current(&name);
                }
                let mut nonce = [0u8; 12];
                let mut key = [0u8; 16];
                rand::thread_rng().fill_bytes(&mut nonce);
                rand::thread_rng().fill_bytes(&mut key);
                let p = hello_payload(&nonce, &key);
                sock.write_all(&plain(&response(MSG_SECURE_HELLO_RESPONSE, sequence, STATUS_OK, &p))).await?;
                chan = Some(Channel::new(&key, nonce));
                info!("bap: channel keyed (AES-128-GCM)");
            }
            MSG_SUBSCRIPTION_REQUEST => {
                // u8 family type, u64 BE family root soid (0x5631F0). Acknowledge, then push
                // the family's baseline as a queuez update.
                let family = payload.first().copied().unwrap_or(0xff);
                let root = payload.get(1..9).map(|b| i64::from_be_bytes(b.try_into().unwrap())).unwrap_or(0);
                info!("bap: subscribe family {family} root {root:#x} (seq {sequence})");
                send(&mut sock, &mut chan, &response(kind + 1, sequence, STATUS_OK, &[])).await?;
                match invest::family_baseline(family as u32, root) {
                    Some(u) => {
                        let n = invest::queuez_update(&[u]);
                        notify_seq += 1;
                        send(&mut sock, &mut chan, &notification(MSG_QUEUEZ_UPDATE_NOTIFICATION, notify_seq, &n)).await?;
                        info!("bap: pushed family {family} baseline ({} bytes)", n.len());
                    }
                    None => warn!("bap: no data for family {family} root {root:#x}"),
                }
            }
            // matchmaking skill/core, friends update, party invite / check, clan: protobuf
            // responses with only optional fields; an empty one is valid. (Any request left
            // unanswered blocks every later response in its queue.)
            16 => {
                // get activity host proxy: request u64 BE (0x563CF0); response 16 bytes
                // (0x563EF0): u64 BE id, u32 BE, u32 BE (the activity host's address).
                // No activity host exists yet: point at port 7500 so the request does not
                // block the queue; the client then times out creating the activity client.
                warn!("bap: activity host proxy requested (seq {sequence}): no activity host yet");
                let mut body = Vec::with_capacity(16);
                body.extend_from_slice(payload.get(..8).unwrap_or(&[0; 8]));  // the requested id
                body.extend_from_slice(&[127, 0, 0, 1]);  // IPv4, network order
                body.extend_from_slice(&u32::from(AH_PORT).to_be_bytes());
                send(&mut sock, &mut chan, &response(17, sequence, STATUS_OK, &body)).await?;
            }
            6 if role == Role::ActivityHost => {
                // activity host manager request (0x55BD10): u8 kind (3 = host startup
                // 0xE0C bytes, 1 = 0x100E bytes), padded to 0x100F. Response 7 (0x55C0A0):
                // exactly 0x89 bytes, u8 kind (must be 2), u64 BE id, 0x80 bytes.
                let k = payload.first().copied().unwrap_or(0);
                info!("bap[AH]: activity host manager request kind {k} (seq {sequence}, {} bytes): {}", payload.len(),
                      pb::hex(&payload[..payload.len().min(96)]));
                if k == 3 {
                    ah_state.on_startup(&payload[1..]);
                }
                let mut body = vec![0u8; 0x89];
                body[0] = 2;
                body[1..9].copy_from_slice(&AH_HOST_ID.to_be_bytes());
                send(&mut sock, &mut chan, &response(7, sequence, STATUS_OK, &body)).await?;
            }
            8 if role == Role::ActivityHost => {
                let Some(m) = ah::parse_client(payload) else {
                    warn!("bap[AH]: malformed activity message {}", pb::hex(&payload[..payload.len().min(64)]));
                    continue;
                };
                for (ty, data) in ah_state.on_client(&m) {
                    notify_seq += 1;
                    let msg = notification(MSG_BAP_TO_CLIENT, notify_seq, &ah::host_payload(AH_HOST_ID, ty, &data));
                    send(&mut sock, &mut chan, &msg).await?;
                    info!("bap[AH]: sent activity message type {ty} ({} bytes)", data.len());
                }
            }
            42 => {
                // matchmaking configuration (0x59A780): request {1 kind, 2, 3 nonce, 11
                // {activity hash, content hash}}. Response schema 0x19421B0: 1, 2 nonce,
                // 3 matches, 4 configuration; the client needs field 4 present (0x59B0E0)
                // and the nonce echoed.
                let f = pb::parse(payload).unwrap_or_default();
                let get = |n: u32| f.iter().find_map(|(k, v)| match (k, v) { (k, pb::Val::Varint(x)) if *k == n => Some(*x), _ => None });
                let nonce = get(3).unwrap_or(0);
                let body = pb::Msg::new().uint(1, get(1).unwrap_or(0)).uint(2, nonce).msg(4, pb::Msg::new()).into_bytes();
                info!("bap: matchmaking configuration (seq {sequence}, nonce {nonce:#x})");
                send(&mut sock, &mut chan, &response(43, sequence, STATUS_OK, &body)).await?;
            }
            34 | 36 | 38 | 40 | 44 => {
                info!("bap: {} (seq {sequence}, {} bytes) -> ok\n{}", name(kind), payload.len(), pb::dump(payload, 2));
                let resp_kind = if kind == 36 { 37 } else { kind + 1 };
                send(&mut sock, &mut chan, &response(resp_kind, sequence, STATUS_OK, &[])).await?;
            }
            MSG_QUEUEZ_REGISTER_REQUEST | MSG_UNSUBSCRIBE_REQUEST
            | MSG_REGISTER_RELAY_CLIENT_REQUEST | MSG_ECHO_REQUEST => {
                // Responses with no payload (codec 0x1F70 on both sides).
                info!("bap: {} (seq {sequence}, {} bytes) -> ok\n{}", name(kind), payload.len(), pb::dump(payload, 2));
                let reply = response(kind + 1, sequence, STATUS_OK, &[]);
                send(&mut sock, &mut chan, &reply).await?;
            }
            MSG_UPDATE_PURCHASED_OFFERS_REQUEST => {
                // protobuf request (0x55CBF0): 2 = packed offer keys the console found locally
                // (0xE0000002 = paid base game), 3 = PSN token JSON. Response schema
                // 0x15BA140: 1 = repeated offer keys owned. BAP is the ownership authority:
                // an empty list leaves the game in trial mode (Earth only), so grant what
                // the console reports.
                let mut offers = Vec::new();
                for (f, v) in pb::parse(payload).unwrap_or_default() {
                    match (f, v) {
                        (2, pb::Val::Bytes(b)) => {
                            let mut r = &b[..];
                            while let Some(x) = pb::read_varint(&mut r) {
                                offers.push(x);
                            }
                        }
                        (2, pb::Val::Varint(x)) => offers.push(x),
                        _ => {}
                    }
                }
                info!("bap: update_purchased_offers (seq {sequence}): granting {:x?}", offers);
                let mut m = pb::Msg::new();
                for o in &offers {
                    m = m.uint(1, *o);
                }
                send(&mut sock, &mut chan, &response(kind + 1, sequence, STATUS_OK, &m.into_bytes())).await?;
            }
            MSG_ACCOUNT_ID_TRANSLATION_REQUEST => {
                // bitstream (0x55B220): u16 count, u8 from type, u8 to type, `count` ids of the
                // from type (7 = platform id record, 0xFF = 64-bit membership id). The response
                // (0x55B620) repeats header and from list, then the to list. Every platform id
                // maps to our one account.
                let mut out = payload.to_vec();
                let count = if payload.len() >= 4 { u16::from_be_bytes([payload[0], payload[1]]) } else { 0 };
                let to = payload.get(3).copied().unwrap_or(0);
                info!("bap: account id translation ({count} ids, {:#x} -> {to:#x})", payload.get(2).copied().unwrap_or(0));
                info!("bap: translation request {}", pb::hex(payload));
                if to == 0xff {
                    // Each platform id record names a PSN online id: map it to that player's
                    // account (slot n: base + n << 32), in the order the names appear.
                    let mut found: Vec<(usize, i64)> = crate::account::players()
                        .iter()
                        .enumerate()
                        .filter_map(|(slot, name)| {
                            payload.windows(name.len()).position(|w| w == name.as_bytes())
                                .map(|at| (at, invest::ACCOUNT_ID_BASE + ((slot as i64) << 32)))
                        })
                        .collect();
                    found.sort();
                    for i in 0..count as usize {
                        let id = found.get(i).map(|f| f.1).unwrap_or_else(invest::account_id);
                        info!("bap: translation {i} -> {id:#x}");
                        out.extend_from_slice(&id.to_be_bytes());
                    }
                }
                send(&mut sock, &mut chan, &response(kind + 1, sequence, STATUS_OK, &out)).await?;
            }
            MSG_CLIENT_CONFIG_REQUEST => {
                // request: u64 BE config cookie (the one from sign-on field 4.1). Response
                // schema 0x15B67E0: 1 cookie, 2 social matchmaking id, 3 optional config
                // stream. Same cookie = keep the configuration from sign-on.
                let cookie = payload.get(..8).map(|b| u64::from_be_bytes(b.try_into().unwrap())).unwrap_or(1);
                info!("bap: client config request (cookie {cookie})");
                let body = pb::Msg::new().uint(1, cookie).int(2, 0).into_bytes();
                send(&mut sock, &mut chan, &response(kind + 1, sequence, STATUS_OK, &body)).await?;
            }
            MSG_USER_MESSAGE_REQUEST => {
                // response schema 0x15BA560: 1/2/3 optional strings, 4 required int
                let body = pb::Msg::new().int(4, 0).into_bytes();
                send(&mut sock, &mut chan, &response(kind + 1, sequence, STATUS_OK, &body)).await?;
            }
            MSG_WORLD_SERVER_REQUEST => {
                let req = invest::parse_request(payload);
                info!("bap: world server request {:#x} (seq {sequence}): {}{}", req.id,
                      req.body.as_ref().map(invest::show).unwrap_or_else(|| format!("(unknown message) {}", pb::hex(payload))),
                      req.extra.as_ref().map(|e| format!(" extra {}", pb::hex(e))).unwrap_or_default());
                let Some(body) = invest::respond(&req) else {
                    continue;
                };
                send(&mut sock, &mut chan, &response(MSG_WORLD_SERVER_RESPONSE, sequence, STATUS_OK, &body)).await?;
                if req.id == 0x1f5 {
                    let n = invest::queuez_update(&[invest::account_baseline(), invest::profile_baseline()]);
                    notify_seq += 1;
                    send(&mut sock, &mut chan, &notification(MSG_QUEUEZ_UPDATE_NOTIFICATION, notify_seq, &n)).await?;
                    info!("bap: character created; pushed account and profile ({} bytes)", n.len());
                }
                if req.id == 0xce {
                    // After the account summary, push the account profile family (4), which
                    // the client registered at sign-in and waits for. It accepts the baseline only
                    // once the family has moved to "awaiting baseline" (replication state 2),
                    // a moment after the account summary is applied.
                    tokio::time::sleep(std::time::Duration::from_millis(1000)).await;
                    let n = invest::queuez_update(&[invest::profile_baseline()]);
                    notify_seq += 1;
                    send(&mut sock, &mut chan, &notification(MSG_QUEUEZ_UPDATE_NOTIFICATION, notify_seq, &n)).await?;
                    info!("bap: pushed family {} baseline ({} bytes)", invest::FAMILY_PROFILE, n.len());
                }
            }
            _ => {
                // xetrov request kind 6 (field 4: {1 kind, 2 report}): report field 43 =
                // {1 session id, 2 BAP address, 4 account, 5 character, ...}
                if kind == 171 {
                    let report = pb::first_bytes(payload, 4)
                        .and_then(|r| pb::first_bytes(&r, 2))
                        .and_then(|r| pb::first_bytes(&r, 43));
                    if let Some(r) = report {
                        let sid = pb::first_bytes(&r, 1).and_then(|b| String::from_utf8(b).ok());
                        let ver = pb::parse(&r).and_then(|f| f.into_iter().find_map(|(n, v)| match v {
                            pb::Val::Varint(x) if n == 7 => Some(x),
                            _ => None,
                        }));
                        info!("bap: xetrov: {} is in session {sid:?} (net version {ver:?})", crate::account::current());
                        crate::account::with(|a| {
                            a.session_id = sid;
                            a.net_version = ver;
                        });
                    }
                }
                warn!("bap[{role:?}]: {enc}message {} ({kind}) seq {sequence} ({} bytes, unhandled): {}\n{}", name(kind), payload.len(),
                      pb::hex(&payload[..payload.len().min(256)]), pb::dump(payload, 2))
            }
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
