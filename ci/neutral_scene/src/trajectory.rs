//! Source-neutral timed trajectory primitives.
//!
//! These are data/math contracts only. Script VMs, gameplay events and source
//! importers decide when a trajectory starts and provide already-quantized
//! timing. The renderer never needs to know whether a command came from T6,
//! another game, authored tooling, or network state.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct NeutralTrajectoryTiming {
    /// Complete command duration in source/runtime milliseconds.
    pub total_millis: u32,
    /// Initial constant-acceleration interval.
    pub accel_millis: u32,
    /// Final constant-deceleration interval.
    pub decel_millis: u32,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct NeutralTrajectorySample3 {
    pub value: [f32; 3],
    /// Derivative in value-units per second.
    pub velocity: [f32; 3],
    /// Normalized path progress, clamped to [0, 1].
    pub progress: f32,
    pub complete: bool,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct NeutralTimedTrajectory3 {
    pub start: [f32; 3],
    pub target: [f32; 3],
    pub timing: NeutralTrajectoryTiming,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct NeutralBallisticTrajectory3 {
    pub start: [f32; 3],
    pub initial_velocity: [f32; 3],
    /// Constant acceleration in value-units per second squared.
    pub acceleration: [f32; 3],
    pub duration_millis: u32,
}

fn finite3(value: [f32; 3]) -> bool {
    value.iter().all(|lane| lane.is_finite())
}

impl NeutralTrajectoryTiming {
    pub fn validate(self) -> Result<(), String> {
        if self.total_millis == 0 {
            return Err("trajectory total duration must be at least one millisecond".to_owned());
        }
        let shaped = u64::from(self.accel_millis) + u64::from(self.decel_millis);
        if shaped > u64::from(self.total_millis) {
            return Err(format!(
                "trajectory acceleration ({}) + deceleration ({}) exceeds total duration ({}) milliseconds",
                self.accel_millis, self.decel_millis, self.total_millis
            ));
        }
        Ok(())
    }

    pub fn linear_millis(self) -> u32 {
        self.total_millis
            .saturating_sub(self.accel_millis)
            .saturating_sub(self.decel_millis)
    }

    /// Return normalized position progress and normalized velocity per second.
    ///
    /// The profile is trapezoidal: constant acceleration to one peak speed,
    /// optional constant-speed travel, then constant deceleration to rest.
    /// Supplying zero acceleration/deceleration produces an ordinary linear
    /// stop. Timing is accepted in integral milliseconds so source adapters can
    /// preserve their own quantization instead of this neutral layer silently
    /// rounding host seconds.
    pub fn sample_progress(self, elapsed_millis: u64) -> Result<(f32, f32, bool), String> {
        self.validate()?;

        let total_ms = u64::from(self.total_millis);
        if elapsed_millis >= total_ms {
            return Ok((1.0, 0.0, true));
        }

        let total = f64::from(self.total_millis) * 0.001;
        let accel = f64::from(self.accel_millis) * 0.001;
        let decel = f64::from(self.decel_millis) * 0.001;
        let linear = f64::from(self.linear_millis()) * 0.001;
        let t = elapsed_millis as f64 * 0.001;

        // Unit-distance peak speed. For a trapezoid, area under velocity is:
        // .5*v*a + v*m + .5*v*d = v*(T - .5*(a+d)).
        let denominator = total - 0.5 * (accel + decel);
        if !denominator.is_finite() || denominator <= 0.0 {
            return Err("trajectory timing produced a non-positive velocity denominator".to_owned());
        }
        let peak = 1.0 / denominator;

        let (progress, velocity) = if accel > 0.0 && t < accel {
            let acceleration = peak / accel;
            (0.5 * acceleration * t * t, acceleration * t)
        } else {
            let accel_distance = 0.5 * peak * accel;
            let after_accel = t - accel;
            if after_accel < linear {
                (accel_distance + peak * after_accel, peak)
            } else if decel > 0.0 {
                let decel_t = (after_accel - linear).clamp(0.0, decel);
                let before_decel = accel_distance + peak * linear;
                let deceleration = peak / decel;
                (
                    before_decel + peak * decel_t - 0.5 * deceleration * decel_t * decel_t,
                    (peak - deceleration * decel_t).max(0.0),
                )
            } else {
                // No deceleration: the linear stage runs directly to target.
                (accel_distance + peak * after_accel, peak)
            }
        };

        let progress = progress.clamp(0.0, 1.0) as f32;
        let velocity = velocity.max(0.0) as f32;
        Ok((progress, velocity, false))
    }
}

impl NeutralTimedTrajectory3 {
    pub fn validate(self) -> Result<(), String> {
        self.timing.validate()?;
        if !finite3(self.start) || !finite3(self.target) {
            return Err("trajectory endpoints contain non-finite values".to_owned());
        }
        Ok(())
    }

    pub fn sample(self, elapsed_millis: u64) -> Result<NeutralTrajectorySample3, String> {
        self.validate()?;
        let (progress, normalized_velocity, complete) =
            self.timing.sample_progress(elapsed_millis)?;
        if complete {
            return Ok(NeutralTrajectorySample3 {
                value: self.target,
                velocity: [0.0; 3],
                progress: 1.0,
                complete: true,
            });
        }

        let delta = [
            self.target[0] - self.start[0],
            self.target[1] - self.start[1],
            self.target[2] - self.start[2],
        ];
        Ok(NeutralTrajectorySample3 {
            value: [
                self.start[0] + delta[0] * progress,
                self.start[1] + delta[1] * progress,
                self.start[2] + delta[2] * progress,
            ],
            velocity: [
                delta[0] * normalized_velocity,
                delta[1] * normalized_velocity,
                delta[2] * normalized_velocity,
            ],
            progress,
            complete: false,
        })
    }
}

impl NeutralBallisticTrajectory3 {
    pub fn validate(self) -> Result<(), String> {
        if self.duration_millis == 0 {
            return Err("ballistic trajectory duration must be at least one millisecond".to_owned());
        }
        if !finite3(self.start)
            || !finite3(self.initial_velocity)
            || !finite3(self.acceleration)
        {
            return Err("ballistic trajectory contains non-finite values".to_owned());
        }
        Ok(())
    }

    pub fn sample(self, elapsed_millis: u64) -> Result<NeutralTrajectorySample3, String> {
        self.validate()?;
        let clamped = elapsed_millis.min(u64::from(self.duration_millis));
        let t = clamped as f64 * 0.001;
        let complete = elapsed_millis >= u64::from(self.duration_millis);
        let mut value = [0.0f32; 3];
        let mut velocity = [0.0f32; 3];
        for axis in 0..3 {
            let start = f64::from(self.start[axis]);
            let v0 = f64::from(self.initial_velocity[axis]);
            let accel = f64::from(self.acceleration[axis]);
            value[axis] = (start + v0 * t + 0.5 * accel * t * t) as f32;
            velocity[axis] = (v0 + accel * t) as f32;
        }
        if complete {
            velocity = [0.0; 3];
        }
        Ok(NeutralTrajectorySample3 {
            value,
            velocity,
            progress: (clamped as f64 / f64::from(self.duration_millis)) as f32,
            complete,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn close(a: f32, b: f32) {
        assert!((a - b).abs() <= 1.0e-5, "{a} != {b}");
    }

    #[test]
    fn linear_profile_reaches_target_exactly() {
        let trajectory = NeutralTimedTrajectory3 {
            start: [0.0, 10.0, -2.0],
            target: [10.0, 0.0, 8.0],
            timing: NeutralTrajectoryTiming {
                total_millis: 1000,
                accel_millis: 0,
                decel_millis: 0,
            },
        };
        let halfway = trajectory.sample(500).unwrap();
        assert_eq!(halfway.value, [5.0, 5.0, 3.0]);
        assert_eq!(halfway.velocity, [10.0, -10.0, 10.0]);
        let end = trajectory.sample(1000).unwrap();
        assert_eq!(end.value, trajectory.target);
        assert_eq!(end.velocity, [0.0; 3]);
        assert!(end.complete);
    }

    #[test]
    fn trapezoid_matches_accel_linear_decel_area() {
        let timing = NeutralTrajectoryTiming {
            total_millis: 4000,
            accel_millis: 1000,
            decel_millis: 1000,
        };
        let trajectory = NeutralTimedTrajectory3 {
            start: [0.0, 0.0, 0.0],
            target: [12.0, 0.0, 0.0],
            timing,
        };
        // Peak speed = 12 / (4 - .5*(1+1)) = 4 units/s.
        let accel_end = trajectory.sample(1000).unwrap();
        close(accel_end.value[0], 2.0);
        close(accel_end.velocity[0], 4.0);

        let mid = trajectory.sample(2000).unwrap();
        close(mid.value[0], 6.0);
        close(mid.velocity[0], 4.0);

        let decel_start = trajectory.sample(3000).unwrap();
        close(decel_start.value[0], 10.0);
        close(decel_start.velocity[0], 4.0);

        let end = trajectory.sample(4000).unwrap();
        close(end.value[0], 12.0);
        assert!(end.complete);
    }

    #[test]
    fn accel_only_and_decel_only_profiles_are_closed() {
        let accel_only = NeutralTimedTrajectory3 {
            start: [0.0; 3],
            target: [3.0, 0.0, 0.0],
            timing: NeutralTrajectoryTiming {
                total_millis: 2000,
                accel_millis: 1000,
                decel_millis: 0,
            },
        };
        close(accel_only.sample(1000).unwrap().value[0], 1.0);
        close(accel_only.sample(2000).unwrap().value[0], 3.0);

        let decel_only = NeutralTimedTrajectory3 {
            start: [0.0; 3],
            target: [3.0, 0.0, 0.0],
            timing: NeutralTrajectoryTiming {
                total_millis: 2000,
                accel_millis: 0,
                decel_millis: 1000,
            },
        };
        close(decel_only.sample(1000).unwrap().value[0], 2.0);
        close(decel_only.sample(2000).unwrap().value[0], 3.0);
    }

    #[test]
    fn timing_rejects_impossible_stage_lengths() {
        let error = NeutralTrajectoryTiming {
            total_millis: 1000,
            accel_millis: 750,
            decel_millis: 500,
        }
        .validate()
        .unwrap_err();
        assert!(error.contains("exceeds total duration"));
    }

    #[test]
    fn zero_distance_keeps_zero_velocity() {
        let trajectory = NeutralTimedTrajectory3 {
            start: [4.0, 5.0, 6.0],
            target: [4.0, 5.0, 6.0],
            timing: NeutralTrajectoryTiming {
                total_millis: 1500,
                accel_millis: 300,
                decel_millis: 200,
            },
        };
        let sample = trajectory.sample(700).unwrap();
        assert_eq!(sample.value, trajectory.start);
        assert_eq!(sample.velocity, [0.0; 3]);
    }

    #[test]
    fn ballistic_uses_explicit_acceleration_and_clamps_to_duration() {
        let trajectory = NeutralBallisticTrajectory3 {
            start: [0.0, 0.0, 10.0],
            initial_velocity: [1.0, 2.0, 3.0],
            acceleration: [0.0, 0.0, -8.0],
            duration_millis: 2000,
        };
        let one_second = trajectory.sample(1000).unwrap();
        close(one_second.value[0], 1.0);
        close(one_second.value[1], 2.0);
        close(one_second.value[2], 9.0);
        close(one_second.velocity[2], -5.0);

        let end = trajectory.sample(3000).unwrap();
        close(end.value[0], 2.0);
        close(end.value[1], 4.0);
        close(end.value[2], 0.0);
        assert_eq!(end.velocity, [0.0; 3]);
        assert!(end.complete);
    }
}
