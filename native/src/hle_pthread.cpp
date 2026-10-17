// libkernel threading: scePthread*, POSIX pthread_* (libScePosix), semaphores, event flags.
//
// PS4 pthread objects are pointers to opaque structures (FreeBSD libthr). A zero
// pointer is the static initializer, so every lock/wait lazily creates the host object.
#include <pthread.h>
#include <sched.h>
#include <time.h>
#include <unistd.h>

#include <array>
#include <atomic>
#include <condition_variable>
#include <cstring>
#include <mutex>
#include <string>
#include <utility>

#include "hle.h"
#include "runtime.h"

namespace d1 {

static int32_t sce(int r) { return r ? sce_err(to_ps4_errno(r)) : SCE_OK; }
static std::mutex g_lazy;

// ------------------------------------------------------------------ mutex
struct MutexAttr { int type = 1; int protocol = 0; };
struct Mutex { pthread_mutex_t m; std::string name; };

static int host_mutex_type(int t) {
    switch (t) {
    case 2: return PTHREAD_MUTEX_RECURSIVE;
    case 3: case 4: return PTHREAD_MUTEX_NORMAL;
    default: return PTHREAD_MUTEX_ERRORCHECK;
    }
}

static Mutex* make_mutex(int type, const char* name) {
    auto* m = new Mutex;
    pthread_mutexattr_t a;
    pthread_mutexattr_init(&a);
    pthread_mutexattr_settype(&a, host_mutex_type(type));
    pthread_mutex_init(&m->m, &a);
    pthread_mutexattr_destroy(&a);
    if (name) m->name = name;
    return m;
}
static Mutex* get_mutex(Mutex** p) {
    // FreeBSD static initializers: NULL (default), 1 (adaptive), 2 (recursive? errorcheck)
    if (reinterpret_cast<uintptr_t>(*p) <= 3) {
        std::lock_guard lk(g_lazy);
        uintptr_t v = reinterpret_cast<uintptr_t>(*p);
        if (v <= 3) *p = make_mutex(v == 0 ? 1 : (v == 1 ? 4 : 2), nullptr);
    }
    return *p;
}

static int32_t scePthreadMutexattrInit(MutexAttr** a) { *a = new MutexAttr; return SCE_OK; }
HLE("scePthreadMutexattrInit", scePthreadMutexattrInit)
static int32_t scePthreadMutexattrDestroy(MutexAttr** a) { delete *a; *a = nullptr; return SCE_OK; }
HLE("scePthreadMutexattrDestroy", scePthreadMutexattrDestroy)
static int32_t scePthreadMutexattrSettype(MutexAttr** a, int t) { (*a)->type = t; return SCE_OK; }
HLE("scePthreadMutexattrSettype", scePthreadMutexattrSettype)
static int32_t scePthreadMutexattrSetprotocol(MutexAttr** a, int p) { (*a)->protocol = p; return SCE_OK; }
HLE("scePthreadMutexattrSetprotocol", scePthreadMutexattrSetprotocol)

static int32_t scePthreadMutexInit(Mutex** m, MutexAttr** a, const char* name) {
    *m = make_mutex(a && *a ? (*a)->type : 1, name);
    return SCE_OK;
}
HLE("scePthreadMutexInit", scePthreadMutexInit)
static int32_t scePthreadMutexDestroy(Mutex** m) {
    if (reinterpret_cast<uintptr_t>(*m) > 3) { pthread_mutex_destroy(&(*m)->m); delete *m; }
    *m = nullptr;
    return SCE_OK;
}
HLE("scePthreadMutexDestroy", scePthreadMutexDestroy)
static int32_t scePthreadMutexLock(Mutex** m) { return sce(pthread_mutex_lock(&get_mutex(m)->m)); }
HLE("scePthreadMutexLock", scePthreadMutexLock)
static int32_t scePthreadMutexTrylock(Mutex** m) { return sce(pthread_mutex_trylock(&get_mutex(m)->m)); }
HLE("scePthreadMutexTrylock", scePthreadMutexTrylock)
static int32_t scePthreadMutexUnlock(Mutex** m) { return sce(pthread_mutex_unlock(&get_mutex(m)->m)); }
HLE("scePthreadMutexUnlock", scePthreadMutexUnlock)

// POSIX flavours return errno values
static int px(int r) { return r ? to_ps4_errno(r) : 0; }
static int p_mutexattr_init(MutexAttr** a) { *a = new MutexAttr; return 0; }
HLE("pthread_mutexattr_init", p_mutexattr_init)
static int p_mutexattr_settype(MutexAttr** a, int t) { (*a)->type = t; return 0; }
HLE("pthread_mutexattr_settype", p_mutexattr_settype)
static int p_mutex_init(Mutex** m, MutexAttr** a) { *m = make_mutex(a && *a ? (*a)->type : 1, nullptr); return 0; }
HLE("pthread_mutex_init", p_mutex_init)
static int p_mutex_destroy(Mutex** m) { scePthreadMutexDestroy(m); return 0; }
HLE("pthread_mutex_destroy", p_mutex_destroy)
static int p_mutex_lock(Mutex** m) { return px(pthread_mutex_lock(&get_mutex(m)->m)); }
HLE("pthread_mutex_lock", p_mutex_lock)
static int p_mutex_trylock(Mutex** m) { return px(pthread_mutex_trylock(&get_mutex(m)->m)); }
HLE("pthread_mutex_trylock", p_mutex_trylock)
static int p_mutex_unlock(Mutex** m) { return px(pthread_mutex_unlock(&get_mutex(m)->m)); }
HLE("pthread_mutex_unlock", p_mutex_unlock)

// ------------------------------------------------------------------ condition variables
struct Cond { pthread_cond_t c; };
static Cond* get_cond(Cond** p) {
    if (!*p) {
        std::lock_guard lk(g_lazy);
        if (!*p) {
            auto* c = new Cond;
            pthread_condattr_t a;
            pthread_condattr_init(&a);
#if !D1_WINDOWS
            pthread_condattr_setclock(&a, CLOCK_MONOTONIC);
#endif
            pthread_cond_init(&c->c, &a);
            *p = c;
        }
    }
    return *p;
}
static int32_t scePthreadCondattrInit(void** a) { *a = nullptr; return SCE_OK; }
HLE("scePthreadCondattrInit", scePthreadCondattrInit)
static int32_t scePthreadCondattrDestroy(void** a) { return SCE_OK; }
HLE("scePthreadCondattrDestroy", scePthreadCondattrDestroy)
static int32_t scePthreadCondInit(Cond** c, void**, const char*) { *c = nullptr; get_cond(c); return SCE_OK; }
HLE("scePthreadCondInit", scePthreadCondInit)
// Destroyed condition variables and semaphores are never freed: another thread may still be
// inside a wait or broadcast on them (the PS4 refuses such a destroy with EBUSY), and glibc
// operating on freed memory hangs in pthread_cond_broadcast. They are small; the count is
// logged occasionally.
static std::atomic<uint64_t> g_leaked_sync{0};
static void note_leak(const char* what) {
    const uint64_t n = ++g_leaked_sync;
    if ((n & (n - 1)) == 0 && n >= 64) log("sync: %llu destroyed %s objects kept alive", (unsigned long long)n, what);
}
static int32_t scePthreadCondDestroy(Cond** c) { if (*c) note_leak("cond"); *c = nullptr; return SCE_OK; }
HLE("scePthreadCondDestroy", scePthreadCondDestroy)
static int32_t scePthreadCondWait(Cond** c, Mutex** m) { return sce(pthread_cond_wait(&get_cond(c)->c, &get_mutex(m)->m)); }
HLE("scePthreadCondWait", scePthreadCondWait)
static int32_t scePthreadCondTimedwait(Cond** c, Mutex** m, uint32_t usec) {
    timespec ts;
#if D1_WINDOWS
    clock_gettime(CLOCK_REALTIME, &ts);  // winpthreads waits against the real-time clock
#else
    clock_gettime(CLOCK_MONOTONIC, &ts);
#endif
    uint64_t ns = uint64_t(ts.tv_nsec) + uint64_t(usec) * 1000;
    ts.tv_sec += ns / 1000000000;
    ts.tv_nsec = ns % 1000000000;
    return sce(pthread_cond_timedwait(&get_cond(c)->c, &get_mutex(m)->m, &ts));
}
HLE("scePthreadCondTimedwait", scePthreadCondTimedwait)
static int32_t scePthreadCondSignal(Cond** c) { return sce(pthread_cond_signal(&get_cond(c)->c)); }
HLE("scePthreadCondSignal", scePthreadCondSignal)
static int32_t scePthreadCondBroadcast(Cond** c) { return sce(pthread_cond_broadcast(&get_cond(c)->c)); }
HLE("scePthreadCondBroadcast", scePthreadCondBroadcast)

static int p_condattr_init(void** a) { *a = nullptr; return 0; }
HLE("pthread_condattr_init", p_condattr_init)
static int p_cond_init(Cond** c, void**) { *c = nullptr; get_cond(c); return 0; }
HLE("pthread_cond_init", p_cond_init)
static int p_cond_destroy(Cond** c) { scePthreadCondDestroy(c); return 0; }
HLE("pthread_cond_destroy", p_cond_destroy)
static int p_cond_wait(Cond** c, Mutex** m) { return px(pthread_cond_wait(&get_cond(c)->c, &get_mutex(m)->m)); }
HLE("pthread_cond_wait", p_cond_wait)
static int p_cond_signal(Cond** c) { return px(pthread_cond_signal(&get_cond(c)->c)); }
HLE("pthread_cond_signal", p_cond_signal)
static int p_cond_broadcast(Cond** c) { return px(pthread_cond_broadcast(&get_cond(c)->c)); }
HLE("pthread_cond_broadcast", p_cond_broadcast)

// ------------------------------------------------------------------ rwlock
struct RwLock { pthread_rwlock_t l; };
static RwLock* get_rw(RwLock** p) {
    if (!*p) {
        std::lock_guard lk(g_lazy);
        if (!*p) { auto* r = new RwLock; pthread_rwlock_init(&r->l, nullptr); *p = r; }
    }
    return *p;
}
static int32_t scePthreadRwlockInit(RwLock** r, void**, const char*) { *r = nullptr; get_rw(r); return SCE_OK; }
HLE("scePthreadRwlockInit", scePthreadRwlockInit)
static int32_t scePthreadRwlockDestroy(RwLock** r) { if (*r) { pthread_rwlock_destroy(&(*r)->l); delete *r; } *r = nullptr; return SCE_OK; }
HLE("scePthreadRwlockDestroy", scePthreadRwlockDestroy)
static int32_t scePthreadRwlockRdlock(RwLock** r) { return sce(pthread_rwlock_rdlock(&get_rw(r)->l)); }
HLE("scePthreadRwlockRdlock", scePthreadRwlockRdlock)
static int32_t scePthreadRwlockWrlock(RwLock** r) { return sce(pthread_rwlock_wrlock(&get_rw(r)->l)); }
HLE("scePthreadRwlockWrlock", scePthreadRwlockWrlock)
static int32_t scePthreadRwlockTryrdlock(RwLock** r) { return sce(pthread_rwlock_tryrdlock(&get_rw(r)->l)); }
HLE("scePthreadRwlockTryrdlock", scePthreadRwlockTryrdlock)
static int32_t scePthreadRwlockTrywrlock(RwLock** r) { return sce(pthread_rwlock_trywrlock(&get_rw(r)->l)); }
HLE("scePthreadRwlockTrywrlock", scePthreadRwlockTrywrlock)
static int32_t scePthreadRwlockUnlock(RwLock** r) { return sce(pthread_rwlock_unlock(&get_rw(r)->l)); }
HLE("scePthreadRwlockUnlock", scePthreadRwlockUnlock)

// ------------------------------------------------------------------ threads
struct ThreadAttr { uint64_t stack = 1 << 20; int detach = 0; int prio = 700; int policy = 1; uint64_t affinity = 0x7F; };
struct Thread {
    pthread_t host{};
    std::string name;
    void* (*entry)(void*) = nullptr;
    void* arg = nullptr;
    void* tcb = nullptr;
    int prio = 700;
    uint64_t affinity = 0x7F;
    void* ret = nullptr;
};
static thread_local Thread* t_self = nullptr;

Thread* ensure_self(const char* name) {
    if (!t_self) {
        t_self = new Thread;
        t_self->host = pthread_self();
        if (name) t_self->name = name;
    }
    return t_self;
}

static int32_t scePthreadAttrInit(ThreadAttr** a) { *a = new ThreadAttr; return SCE_OK; }
HLE("scePthreadAttrInit", scePthreadAttrInit)
static int32_t scePthreadAttrDestroy(ThreadAttr** a) { delete *a; *a = nullptr; return SCE_OK; }
HLE("scePthreadAttrDestroy", scePthreadAttrDestroy)
static int32_t scePthreadAttrSetstacksize(ThreadAttr** a, uint64_t s) { (*a)->stack = s; return SCE_OK; }
HLE("scePthreadAttrSetstacksize", scePthreadAttrSetstacksize)
static int32_t scePthreadAttrSetdetachstate(ThreadAttr** a, int d) { (*a)->detach = d; return SCE_OK; }
HLE("scePthreadAttrSetdetachstate", scePthreadAttrSetdetachstate)
static int32_t scePthreadAttrSetinheritsched(ThreadAttr**, int) { return SCE_OK; }
HLE("scePthreadAttrSetinheritsched", scePthreadAttrSetinheritsched)
static int32_t scePthreadAttrSetschedpolicy(ThreadAttr** a, int p) { (*a)->policy = p; return SCE_OK; }
HLE("scePthreadAttrSetschedpolicy", scePthreadAttrSetschedpolicy)
static int32_t scePthreadAttrSetschedparam(ThreadAttr** a, const int* prio) { (*a)->prio = *prio; return SCE_OK; }
HLE("scePthreadAttrSetschedparam", scePthreadAttrSetschedparam)
static int32_t scePthreadAttrGetschedparam(ThreadAttr** a, int* prio) { *prio = (*a)->prio; return SCE_OK; }
HLE("scePthreadAttrGetschedparam", scePthreadAttrGetschedparam)
static int32_t scePthreadAttrSetaffinity(ThreadAttr** a, uint64_t m) { (*a)->affinity = m; return SCE_OK; }
HLE("scePthreadAttrSetaffinity", scePthreadAttrSetaffinity)

void register_guest_thread(const char* name);
// scePthreadExit returns to the thread's start without unwinding the game's frames (they
// have no host unwind information; Windows would crash walking them).
static thread_local uint64_t t_exit_sp = 0;
static void* thread_trampoline(void* p) {
    auto* t = static_cast<Thread*>(p);
    t_self = t;
    register_guest_thread(t->name.c_str());
    t->tcb = tls_create_thread_block();
    tls_set_current(t->tcb);
    if (!t->name.empty()) os::set_thread_name(t->name.c_str());
    t->ret = reinterpret_cast<void*>(d1_call_guest_exitable(reinterpret_cast<const void*>(t->entry),
                                                            reinterpret_cast<uint64_t>(t->arg), &t_exit_sp));
    t_exit_sp = 0;
    return t->ret;
}

static int32_t scePthreadCreate(Thread** out, ThreadAttr** attr, void* (*entry)(void*), void* arg, const char* name) {
    auto* t = new Thread;
    t->entry = entry;
    t->arg = arg;
    if (name) t->name = name;
    ThreadAttr def;
    const ThreadAttr& a = (attr && *attr) ? **attr : def;
    t->prio = a.prio;
    t->affinity = a.affinity;
    pthread_attr_t ha;
    pthread_attr_init(&ha);
    pthread_attr_setstacksize(&ha, std::max<uint64_t>(a.stack, 256 * 1024) + 64 * 1024);
    if (a.detach) pthread_attr_setdetachstate(&ha, PTHREAD_CREATE_DETACHED);
    int r = pthread_create(&t->host, &ha, thread_trampoline, t);
    pthread_attr_destroy(&ha);
    if (r) return sce(r);
    log("thread created: %s (entry %s)", name ? name : "?", describe_addr(reinterpret_cast<uint64_t>(entry)).c_str());
    *out = t;
    return SCE_OK;
}
HLE("scePthreadCreate", scePthreadCreate)

static Thread* scePthreadSelf() { return ensure_self(nullptr); }
HLE("scePthreadSelf", scePthreadSelf)
static Thread* p_self() { return ensure_self(nullptr); }
HLE("pthread_self", p_self)
static int32_t scePthreadJoin(Thread* t, void** ret) {
    int r = pthread_join(t->host, ret);
    return sce(r);
}
HLE("scePthreadJoin", scePthreadJoin)
static int32_t scePthreadDetach(Thread* t) { return sce(pthread_detach(t->host)); }
HLE("scePthreadDetach", scePthreadDetach)
[[noreturn]] static void scePthreadExit(void* v) {
    if (t_exit_sp) d1_guest_exit(t_exit_sp, reinterpret_cast<uint64_t>(v));
    pthread_exit(v);
    __builtin_unreachable();
}
HLE("scePthreadExit", scePthreadExit)
static int32_t scePthreadCancel(Thread* t) { return sce(pthread_cancel(t->host)); }
HLE("scePthreadCancel", scePthreadCancel)
static int scePthreadEqual(Thread* a, Thread* b) { return a == b; }
HLE("scePthreadEqual", scePthreadEqual)
static int32_t scePthreadYield() { sched_yield(); return SCE_OK; }
HLE("scePthreadYield", scePthreadYield)
static int ps4_sched_yield() { return sched_yield(); }
HLE("sched_yield", ps4_sched_yield)
static int32_t scePthreadGetprio(Thread* t, int* p) { *p = t->prio; return SCE_OK; }
HLE("scePthreadGetprio", scePthreadGetprio)
static int32_t scePthreadSetprio(Thread* t, int p) { t->prio = p; return SCE_OK; }
HLE("scePthreadSetprio", scePthreadSetprio)
static int32_t scePthreadGetschedparam(Thread* t, int* pol, int* prio) { if (pol) *pol = 1; if (prio) *prio = t->prio; return SCE_OK; }
HLE("scePthreadGetschedparam", scePthreadGetschedparam)
static int32_t scePthreadSetschedparam(Thread* t, int, const int* prio) { if (prio) t->prio = *prio; return SCE_OK; }
HLE("scePthreadSetschedparam", scePthreadSetschedparam)
static int p_setschedparam(Thread*, int, const int*) { return 0; }
HLE("pthread_setschedparam", p_setschedparam)
static int32_t scePthreadGetaffinity(Thread* t, uint64_t* m) { *m = t->affinity; return SCE_OK; }
HLE("scePthreadGetaffinity", scePthreadGetaffinity)
static int32_t scePthreadSetaffinity(Thread* t, uint64_t m) { t->affinity = m; return SCE_OK; }
HLE("scePthreadSetaffinity", scePthreadSetaffinity)
static int32_t scePthreadRename(Thread* t, const char* n) {
    if (n) t->name = n;
    return SCE_OK;
}
HLE("scePthreadRename", scePthreadRename)

// ------------------------------------------------------------------ keys / once
// Destructors are game functions (System V); the host calls them through one small host
// function per key that knows which game function to call.
using GuestDtor = D1_SYSV void (*)(void*);
static constexpr size_t kMaxKeys = 512;
static GuestDtor g_key_dtors[kMaxKeys];
template <size_t K> static void key_dtor(void* v) { if (g_key_dtors[K]) g_key_dtors[K](v); }
template <size_t... K> static constexpr auto make_key_dtors(std::index_sequence<K...>) {
    return std::array<void (*)(void*), sizeof...(K)>{&key_dtor<K>...};
}
static constexpr auto kKeyDtors = make_key_dtors(std::make_index_sequence<kMaxKeys>{});

// Guest key K is backed by host key g_host_keys[K], created with key_dtor<K>.
static pthread_key_t g_host_keys[kMaxKeys];
static std::atomic<bool> g_key_used[kMaxKeys];
static int32_t scePthreadKeyCreate(uint32_t* key, GuestDtor dtor) {
    for (size_t k = 0; k < kMaxKeys; ++k) {
        bool expected = false;
        if (!g_key_used[k].compare_exchange_strong(expected, true)) continue;
        g_key_dtors[k] = dtor;
        int r = pthread_key_create(&g_host_keys[k], dtor ? kKeyDtors[k] : nullptr);
        if (r) { g_key_used[k] = false; return sce(r); }
        *key = uint32_t(k);
        return SCE_OK;
    }
    return sce_err(35);  // EAGAIN: out of keys
}
HLE("scePthreadKeyCreate", scePthreadKeyCreate)
static int32_t scePthreadKeyDelete(uint32_t k) {
    if (k >= kMaxKeys || !g_key_used[k]) return sce_err(22);
    pthread_key_delete(g_host_keys[k]);
    g_key_dtors[k] = nullptr;
    g_key_used[k] = false;
    return SCE_OK;
}
HLE("scePthreadKeyDelete", scePthreadKeyDelete)
static void* scePthreadGetspecific(uint32_t k) { return k < kMaxKeys ? pthread_getspecific(g_host_keys[k]) : nullptr; }
HLE("scePthreadGetspecific", scePthreadGetspecific)
static int32_t scePthreadSetspecific(uint32_t k, const void* v) {
    if (k >= kMaxKeys || !g_key_used[k]) return sce_err(22);
    return sce(pthread_setspecific(g_host_keys[k], v));
}
HLE("scePthreadSetspecific", scePthreadSetspecific)

struct Once { std::atomic<int32_t> state; int32_t pad; void* mutex; };
static int32_t scePthreadOnce(Once* o, D1_SYSV void (*fn)()) {
    static std::recursive_mutex mu;
    if (o->state.load() == 2) return SCE_OK;
    std::lock_guard lk(mu);
    if (o->state.load() != 2) {
        o->state = 1;
        fn();
        o->state = 2;
    }
    return SCE_OK;
}
HLE("scePthreadOnce", scePthreadOnce)

// ------------------------------------------------------------------ semaphores
struct Sema { std::mutex m; std::condition_variable cv; int count, max; std::string name; };
static int32_t sceKernelCreateSema(Sema** out, const char* name, uint32_t attr, int init, int max, void*) {
    auto* s = new Sema;
    s->count = init;
    s->max = max;
    if (name) s->name = name;
    *out = s;
    return SCE_OK;
}
HLE("sceKernelCreateSema", sceKernelCreateSema)
static int32_t sceKernelDeleteSema(Sema* s) { if (s) note_leak("semaphore"); return SCE_OK; }
HLE("sceKernelDeleteSema", sceKernelDeleteSema)
// PS4 semantics (libkernel): waiting for more than the maximum is EINVAL; a timed wait
// writes the remaining time back (0 on timeout, ETIMEDOUT); signalling past the maximum
// fails with EINVAL and leaves the count unchanged. The game's job system counts pending
// wakeups by whether its signal succeeded (0xF4E40), so a signal that silently clamps
// makes it lose track of sleeping workers.
static int32_t sceKernelWaitSema(Sema* s, int need, uint32_t* timeout_us) {
    if (!s || need < 1 || need > s->max) return sce_err(22);
    std::unique_lock lk(s->m);
    auto ready = [&] { return s->count >= need; };
    if (timeout_us) {
        const auto start = std::chrono::steady_clock::now();
        if (!s->cv.wait_for(lk, std::chrono::microseconds(*timeout_us), ready)) {
            *timeout_us = 0;
            return sce_err(60);
        }
        const auto used = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - start).count();
        *timeout_us = used >= int64_t(*timeout_us) ? 0 : uint32_t(*timeout_us - used);
    } else {
        s->cv.wait(lk, ready);
    }
    s->count -= need;
    return SCE_OK;
}
HLE("sceKernelWaitSema", sceKernelWaitSema)
static int32_t sceKernelSignalSema(Sema* s, int n) {
    if (!s || n < 1) return sce_err(22);
    {
        std::lock_guard lk(s->m);
        if (s->count + n > s->max) {
            static std::atomic<int> logged{0};
            if (logged.fetch_add(1) < 5)
                log("sema '%s': signal %d past max %d (count %d) -> EINVAL", s->name.c_str(), n, s->max, s->count);
            return sce_err(22);
        }
        s->count += n;
    }
    s->cv.notify_all();
    return SCE_OK;
}
HLE("sceKernelSignalSema", sceKernelSignalSema)

// ------------------------------------------------------------------ event flags
struct EventFlag { std::mutex m; std::condition_variable cv; uint64_t bits; std::string name; };
static int32_t sceKernelCreateEventFlag(EventFlag** out, const char* name, uint32_t, uint64_t init, void*) {
    auto* e = new EventFlag;
    e->bits = init;
    if (name) e->name = name;
    *out = e;
    return SCE_OK;
}
HLE("sceKernelCreateEventFlag", sceKernelCreateEventFlag)
static int32_t sceKernelDeleteEventFlag(EventFlag* e) { if (e) note_leak("event flag"); return SCE_OK; }
HLE("sceKernelDeleteEventFlag", sceKernelDeleteEventFlag)
static int32_t sceKernelSetEventFlag(EventFlag* e, uint64_t bits) {
    { std::lock_guard lk(e->m); e->bits |= bits; }
    e->cv.notify_all();
    return SCE_OK;
}
HLE("sceKernelSetEventFlag", sceKernelSetEventFlag)
static int32_t sceKernelClearEventFlag(EventFlag* e, uint64_t bits) {
    std::lock_guard lk(e->m);
    e->bits &= bits;
    return SCE_OK;
}
HLE("sceKernelClearEventFlag", sceKernelClearEventFlag)
// mode: 0x01 AND, 0x02 OR, 0x10 clear all, 0x20 clear matched
static bool ef_match(uint64_t have, uint64_t want, uint32_t mode) {
    return (mode & 1) ? (have & want) == want : (have & want) != 0;
}
static void ef_clear(EventFlag* e, uint64_t want, uint32_t mode) {
    if (mode & 0x10) e->bits = 0;
    else if (mode & 0x20) e->bits &= ~want;
}
static int32_t sceKernelWaitEventFlag(EventFlag* e, uint64_t want, uint32_t mode, uint64_t* result, uint32_t* timeout_us) {
    std::unique_lock lk(e->m);
    auto ready = [&] { return ef_match(e->bits, want, mode); };
    if (timeout_us) {
        if (!e->cv.wait_for(lk, std::chrono::microseconds(*timeout_us), ready)) {
            if (result) *result = e->bits;
            *timeout_us = 0;
            return sce_err(60);
        }
    } else {
        e->cv.wait(lk, ready);
    }
    if (result) *result = e->bits;
    ef_clear(e, want, mode);
    return SCE_OK;
}
HLE("sceKernelWaitEventFlag", sceKernelWaitEventFlag)
static int32_t sceKernelPollEventFlag(EventFlag* e, uint64_t want, uint32_t mode, uint64_t* result) {
    std::lock_guard lk(e->m);
    if (result) *result = e->bits;
    if (!ef_match(e->bits, want, mode)) return sce_err(16);
    ef_clear(e, want, mode);
    return SCE_OK;
}
HLE("sceKernelPollEventFlag", sceKernelPollEventFlag)

}  // namespace d1
