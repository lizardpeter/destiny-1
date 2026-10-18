// NID = first 8 bytes of SHA-1(name || 518D64A635DED8C1E6B039B1C3E55230), read as a
// little-endian u64, written big-endian and Base64-encoded with '/' replaced by '-',
// truncated to 11 characters.
#pragma once
#include <cstdint>
#include <cstring>
#include <string>

namespace d1 {

inline void sha1(const uint8_t* data, size_t len, uint8_t out[20]) {
    uint32_t h[5] = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0};
    auto rol = [](uint32_t v, int n) { return (v << n) | (v >> (32 - n)); };
    std::string m(reinterpret_cast<const char*>(data), len);
    uint64_t bits = uint64_t(len) * 8;
    m.push_back(char(0x80));
    while (m.size() % 64 != 56) m.push_back(0);
    for (int i = 7; i >= 0; --i) m.push_back(char(bits >> (i * 8)));
    for (size_t c = 0; c < m.size(); c += 64) {
        uint32_t w[80];
        for (int i = 0; i < 16; ++i)
            w[i] = (uint8_t(m[c + 4 * i]) << 24) | (uint8_t(m[c + 4 * i + 1]) << 16) |
                   (uint8_t(m[c + 4 * i + 2]) << 8) | uint8_t(m[c + 4 * i + 3]);
        for (int i = 16; i < 80; ++i) w[i] = rol(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
        uint32_t a = h[0], b = h[1], cc = h[2], d = h[3], e = h[4];
        for (int i = 0; i < 80; ++i) {
            uint32_t f, k;
            if (i < 20) { f = (b & cc) | (~b & d); k = 0x5A827999; }
            else if (i < 40) { f = b ^ cc ^ d; k = 0x6ED9EBA1; }
            else if (i < 60) { f = (b & cc) | (b & d) | (cc & d); k = 0x8F1BBCDC; }
            else { f = b ^ cc ^ d; k = 0xCA62C1D6; }
            uint32_t t = rol(a, 5) + f + e + k + w[i];
            e = d; d = cc; cc = rol(b, 30); b = a; a = t;
        }
        h[0] += a; h[1] += b; h[2] += cc; h[3] += d; h[4] += e;
    }
    for (int i = 0; i < 5; ++i)
        for (int j = 0; j < 4; ++j) out[i * 4 + j] = uint8_t(h[i] >> (24 - 8 * j));
}

inline std::string nid_of(const std::string& name) {
    static const uint8_t suffix[16] = {0x51, 0x8D, 0x64, 0xA6, 0x35, 0xDE, 0xD8, 0xC1,
                                       0xE6, 0xB0, 0x39, 0xB1, 0xC3, 0xE5, 0x52, 0x30};
    std::string in = name;
    in.append(reinterpret_cast<const char*>(suffix), 16);
    uint8_t d[20];
    sha1(reinterpret_cast<const uint8_t*>(in.data()), in.size(), d);
    uint64_t v;
    std::memcpy(&v, d, 8);  // little-endian read
    uint8_t be[8];
    for (int i = 0; i < 8; ++i) be[i] = uint8_t(v >> (56 - 8 * i));
    static const char* A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-";
    std::string s;
    uint32_t acc = 0;
    int nb = 0;
    for (int i = 0; i < 8; ++i) {
        acc = (acc << 8) | be[i];
        nb += 8;
        while (nb >= 6) { s.push_back(A[(acc >> (nb - 6)) & 63]); nb -= 6; }
    }
    if (nb) s.push_back(A[(acc << (6 - nb)) & 63]);
    return s.substr(0, 11);
}

}  // namespace d1
