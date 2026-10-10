//! Opt-in, low-frequency native Windows performance-regression capture.
//! Normal gameplay does not construct a recorder or perform any I/O.
//! Exact GPU pass durations require the existing F11 timestamp profiler.
#![cfg_attr(not(target_os = "windows"), allow(dead_code))]

use std::{
    fs::{self, OpenOptions},
    io::Write,
    path::PathBuf,
    sync::OnceLock,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

const WINDOW: Duration = Duration::from_secs(10);
const MAX_SAMPLES: usize = 16_384;
const METRIC_COUNT: usize = 13;
pub(crate) const CPU: usize = 0;
pub(crate) const GPU_EXEC: usize = 1;
pub(crate) const GPU_FENCE: usize = 2;
pub(crate) const GPU_UPLOADS: usize = 3;
pub(crate) const GPU_STATIC: usize = 4;
pub(crate) const GPU_SOURCE: usize = 5;
pub(crate) const GPU_SKINNED: usize = 6;
pub(crate) const GPU_WORLD: usize = 7;
pub(crate) const GPU_HUD: usize = 8;
pub(crate) const CPU_STATIC: usize = 9;
pub(crate) const CPU_SKINNED: usize = 10;
pub(crate) const CPU_WORLD: usize = 11;
pub(crate) const PRESENT_CALL: usize = 12;

const HEADER: &str = "elapsed_s,map,mode,width,height,presented_frames,frame_fps,cpu_p50_ms,cpu_p95_ms,cpu_p99_ms,gpu_exec_p50_ms,gpu_exec_p95_ms,gpu_exec_p99_ms,gpu_fence_p95_ms,gpu_upload_p95_ms,gpu_static_p95_ms,gpu_source_p95_ms,gpu_skinned_p95_ms,gpu_world_p95_ms,gpu_hud_p95_ms,cpu_static_p95_ms,cpu_skinned_p95_ms,cpu_world_p95_ms,present_call_p95_ms,fence_busy_pct_cumulative,acquire_busy_pct_cumulative";

pub(crate) fn enabled() -> bool {
    static ENABLED: OnceLock<bool> = OnceLock::new();
    *ENABLED.get_or_init(|| std::env::var("RUST_TEST_PERF_CAPTURE").is_ok_and(|v| v == "1"))
}

#[derive(Clone, Copy, Debug)]
pub(crate) struct Sample {
    pub(crate) values: [Option<f32>; METRIC_COUNT],
    pub(crate) fence_busy_pct: f32,
    pub(crate) acquire_busy_pct: f32,
    pub(crate) width: u32,
    pub(crate) height: u32,
}

#[derive(Default)]
struct Metrics {
    values: [Vec<f32>; METRIC_COUNT],
    frames: usize,
    fence_busy_pct: f32,
    acquire_busy_pct: f32,
}

impl Metrics {
    fn push(&mut self, sample: Sample) {
        self.frames += 1;
        self.fence_busy_pct = sample.fence_busy_pct;
        self.acquire_busy_pct = sample.acquire_busy_pct;
        if self.frames <= MAX_SAMPLES {
            for (into, value) in self.values.iter_mut().zip(sample.values) {
                if let Some(value) = value.filter(|v| v.is_finite() && *v >= 0.0) {
                    into.push(value);
                }
            }
        }
    }
}

#[inline]
fn percentile(values: &mut Vec<f32>, numerator: usize) -> Option<f32> {
    if values.is_empty() { return None; }
    values.sort_unstable_by(f32::total_cmp);
    let idx = ((values.len() - 1) * numerator + 99) / 100;
    Some(values[idx.min(values.len() - 1)])
}

fn csv_value(value: Option<f32>) -> String {
    value.map(|v| format!("{v:.3}")).unwrap_or_default()
}

fn safe_map_label(map: &str) -> String {
    map.chars().map(|c| if c.is_ascii_alphanumeric() || matches!(c, '-' | '_') { c } else { '_' })
        .take(80).collect()
}

/// Only allocated when the environment explicitly enables this recorder.
/// CSV flush happens once per 10-second window, never per frame.
pub(crate) struct PerfCapture {
    path: PathBuf,
    started: Instant,
    window_start: Instant,
    current_map: String,
    gameplay: bool,
    width: u32,
    height: u32,
    metrics: Metrics,
}

impl PerfCapture {
    pub(crate) fn from_env() -> Option<Self> {
        if !enabled() { return None; }
        let root = std::env::current_exe().ok()?.parent()?.join("logs").join("performance");
        if let Err(error) = fs::create_dir_all(&root) {
            eprintln!("Performance capture disabled; logs directory could not be created: {error}");
            return None;
        }
        let unique = SystemTime::now().duration_since(UNIX_EPOCH).ok()?.as_millis();
        let path = root.join(format!("native_vulkan_{unique}_{}.csv", std::process::id()));
        match fs::write(&path, format!("{HEADER}\n")) {
            Ok(()) => println!("Native performance capture: {} (10s windows, opt-in, no frame queuing)", path.display()),
            Err(error) => {
                eprintln!("Performance capture disabled; CSV could not be opened: {error}");
                return None;
            }
        }
        let now = Instant::now();
        Some(Self {
            path, started: now, window_start: now,
            current_map: String::new(), gameplay: false,
            width: 0, height: 0, metrics: Metrics::default(),
        })
    }

    pub(crate) fn observe(&mut self, map: &str, gameplay: bool, sample: Sample) {
        let now = Instant::now();
        let safe_map = safe_map_label(map);
        if (self.current_map != safe_map || self.gameplay != gameplay
            || self.width != sample.width || self.height != sample.height)
            && self.metrics.frames > 0
        {
            self.flush_at(now);
        }
        self.current_map = safe_map;
        self.gameplay = gameplay;
        self.width = sample.width;
        self.height = sample.height;
        self.metrics.push(sample);
        if now.duration_since(self.window_start) >= WINDOW {
            self.flush_at(now);
        }
    }

    fn flush_at(&mut self, now: Instant) {
        if self.metrics.frames == 0 {
            self.window_start = now;
            return;
        }
        let elapsed = now.duration_since(self.window_start).as_secs_f32().max(0.001);
        let mut metrics = std::mem::take(&mut self.metrics);
        let mut p50 = [None; METRIC_COUNT];
        let mut p95 = [None; METRIC_COUNT];
        let mut p99 = [None; METRIC_COUNT];
        for (idx, samples) in metrics.values.iter_mut().enumerate() {
            if !samples.is_empty() {
                samples.sort_unstable_by(f32::total_cmp);
                let last = samples.len() - 1;
                p50[idx] = Some(samples[(last * 50 + 99) / 100]);
                p95[idx] = Some(samples[(last * 95 + 99) / 100]);
                p99[idx] = Some(samples[(last * 99 + 99) / 100]);
            }
        }
        let mut cells = vec![
            format!("{:.2}", now.duration_since(self.started).as_secs_f32()),
            self.current_map.clone(),
            if self.gameplay { "game".to_owned() } else { "menu".to_owned() },
            self.width.to_string(),
            self.height.to_string(),
            metrics.frames.to_string(),
            format!("{:.2}", metrics.frames as f32 / elapsed),
        ];
        for (idx, mode) in [
            (CPU, 50), (CPU, 95), (CPU, 99),
            (GPU_EXEC, 50), (GPU_EXEC, 95), (GPU_EXEC, 99),
            (GPU_FENCE, 95), (GPU_UPLOADS, 95), (GPU_STATIC, 95),
            (GPU_SOURCE, 95), (GPU_SKINNED, 95), (GPU_WORLD, 95),
            (GPU_HUD, 95), (CPU_STATIC, 95), (CPU_SKINNED, 95),
            (CPU_WORLD, 95), (PRESENT_CALL, 95),
        ] {
            cells.push(csv_value(match mode { 50 => p50[idx], 99 => p99[idx], _ => p95[idx] }));
        }
        cells.push(format!("{:.2}", metrics.fence_busy_pct));
        cells.push(format!("{:.2}", metrics.acquire_busy_pct));
        if let Err(error) = OpenOptions::new().append(true).open(&self.path)
            .and_then(|mut file| writeln!(file, "{}", cells.join(",")))
        {
            // Diagnostic output must never panic, block the GPU or change the
            // render path if the filesystem becomes inaccessible.
            eprintln!("Native performance CSV write failed: {error}");
        }
        self.window_start = now;
    }
}

impl Drop for PerfCapture {
    fn drop(&mut self) {
        if self.metrics.frames > 0 {
            self.flush_at(Instant::now());
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn percentiles_use_finite_nonnegative_samples_and_match_header_width() {
        let mut m = Metrics::default();
        for i in 0..100 {
            let mut values = [None; METRIC_COUNT];
            values[CPU] = Some(i as f32);
            values[GPU_EXEC] = Some(i as f32 / 2.0);
            m.push(Sample {
                values, fence_busy_pct: 40.0, acquire_busy_pct: 5.0,
                width: 1920, height: 1080,
            });
        }
        assert_eq!(percentile(&mut m.values[CPU], 95), Some(95.0));
        assert_eq!(percentile(&mut m.values[GPU_EXEC], 50), Some(25.0));
        assert_eq!(m.frames, 100);
        assert_eq!(HEADER.split(',').count(), 26);
    }
    #[test]
    fn map_names_cannot_corrupt_csv_columns() {
        assert_eq!(safe_map_label("SMG,Beach\nGalaxy"), "SMG_Beach_Galaxy");
        assert_eq!(safe_map_label("hijacked"), "hijacked");
    }

    #[test]
    fn csv_flush_has_fixed_schema_and_scene_changes_reset_samples() {
        let unique = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos();
        let path = std::env::temp_dir().join(format!("rust-fps-capture-{}-{unique}.csv", std::process::id()));
        fs::write(&path, format!("{HEADER}\n")).unwrap();
        let start = Instant::now();
        let mut recorder = PerfCapture {
            path: path.clone(), started: start,
            window_start: start, current_map: String::new(),
            gameplay: false, width: 0, height: 0,
            metrics: Metrics::default(),
        };
        let mut values = [None; METRIC_COUNT];
        values[CPU] = Some(11.0);
        values[GPU_EXEC] = Some(9.0);
        let sample = Sample {
            values, fence_busy_pct: 30.0, acquire_busy_pct: 7.0,
            width: 1920, height: 1080,
        };
        recorder.observe("SMG, Beach", true, sample);
        recorder.observe("SMG, Beach", true, sample);
        recorder.observe("Destiny Tower", true, sample);
        recorder.flush_at(Instant::now());
        drop(recorder);
        let data = fs::read_to_string(&path).unwrap();
        fs::remove_file(path).unwrap();
        let rows = data.lines().collect::<Vec<_>>();
        assert_eq!(rows.len(), 3);
        for row in &rows {
            assert_eq!(row.split(',').count(), HEADER.split(',').count(), "{row}");
        }
        assert!(rows[1].contains("SMG__Beach"));
        assert!(rows[2].contains("Destiny_Tower"));
    }

    #[test]
    fn rejects_invalid_samples_and_bounds_retention() {
        let mut m = Metrics::default();
        for _ in 0..MAX_SAMPLES + 3 {
            let mut values = [None; METRIC_COUNT];
            values[CPU] = Some(1.0);
            values[GPU_EXEC] = Some(f32::NAN);
            m.push(Sample {values, fence_busy_pct: 0.0, acquire_busy_pct: 0.0, width:1, height:1});
        }
        assert_eq!(m.frames, MAX_SAMPLES + 3);
        assert_eq!(m.values[CPU].len(), MAX_SAMPLES);
        assert!(m.values[GPU_EXEC].is_empty());
    }
}
