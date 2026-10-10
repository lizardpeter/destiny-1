const COEFF_RECORD_BYTES: usize = 54;
const INV_65535: f32 = f32::from_bits(0x3780_0080);
const SCALE_32: f32 = 32.0;
const BIAS_NEG16: f32 = -16.0;
const QUARTER: f32 = 0.25;
const HALF: f32 = 0.5;
const EPSILON: f32 = f32::from_bits(0x38d1_b717);
const THREE: f32 = 3.0;
const TWO_THIRDS: f32 = f32::from_bits(0x3f2a_aaab);

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct T6WorldLightGridEntry {
    pub(crate) coeff_index: u16,
    pub(crate) primary_light_index: u8,
    pub(crate) needs_trace: u8,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct T6WorldLightGridRun {
    pub(crate) column_start: u16,
    pub(crate) column_count: u8,
    pub(crate) z_start: u16,
    pub(crate) z_count: u8,
    pub(crate) first_entry: usize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct T6WorldLightGridRow {
    pub(crate) row_index: usize,
    pub(crate) raw_byte_offset: usize,
    pub(crate) col_start: u16,
    pub(crate) col_count: u16,
    pub(crate) z_start: u16,
    pub(crate) z_count: u16,
    pub(crate) first_entry: usize,
    pub(crate) runs: Vec<T6WorldLightGridRun>,
}

/// Exact decoded 9xRGB coefficient record used by the retail T6 PC light-grid
/// routines. Values remain in the game's native 32x signed coefficient domain.
pub(crate) type T6DecodedLightGridCoeffs = [[f32; 3]; 9];

/// Exact T6 `GfxLightingSH` 3xvec4 packing reconstructed from the retail PC
/// renderer. This is retained separately from any shader-side interpretation.
pub(crate) type T6LightingSh = [[f32; 4]; 3];

/// Renderer-neutral ownership of the exact serialized T6 GfxLightGrid.
///
/// The retail decoder has now source-closed the SHA-pinned Nuketown row/RLE
/// grammar through exact row/entry-boundary validation. This runtime therefore
/// retains exact integer-grid-point -> GfxLightGridEntry ownership as well as
/// the coefficient bank. It still deliberately stops before inventing BO2's
/// world-space sample selection, visibility trace policy, or GPU
/// modelLightingSampler texture3D layout.
#[derive(Clone, Debug)]
pub(crate) struct T6WorldLightGridRuntime {
    pub(crate) sun_primary_light_index: u32,
    pub(crate) mins: [u16; 3],
    pub(crate) maxs: [u16; 3],
    pub(crate) offset: f32,
    pub(crate) row_axis: u32,
    pub(crate) col_axis: u32,
    pub(crate) row_data_start: Vec<u16>,
    pub(crate) raw_row_data: Vec<u8>,
    pub(crate) rows: Vec<T6WorldLightGridRow>,
    pub(crate) entries: Vec<T6WorldLightGridEntry>,
    pub(crate) coeff_bytes: Vec<u8>,
    pub(crate) coeff_count: usize,
}

/// Cold-path lookup used only after validated wide RLE rows reach late
/// columns. Keeping it out-of-line preserves a compact early-grid hot path.
#[inline(never)]
fn t6_late_lightgrid_run(
    runs: &[T6WorldLightGridRun],
    local_col: usize,
) -> Option<&T6WorldLightGridRun> {
    let index = runs.partition_point(|run| {
        usize::from(run.column_start) + usize::from(run.column_count) <= local_col
    });
    let run = runs.get(index)?;
    let first = usize::from(run.column_start);
    (local_col >= first && local_col < first + usize::from(run.column_count))
        .then_some(run)
}

impl T6WorldLightGridRuntime {
    #[cfg(feature = "import-bo2")]
    pub(crate) fn load_direct_if_present(map_id: &str) -> Result<Option<Self>, String> {
        const NUKETOWN_MAP: &str = "mp_nuketown_2020";
        const EXPANDED_SHA256: &str =
            "7e791fb90a085f3bff9e0df895e5a232fa91cc43bcd0027225fe811f7891d505";
        if map_id != NUKETOWN_MAP {
            return Ok(None);
        }

        let files = match bo2_importer::bo2::retail_runtime::T6RetailNuketownFiles::discover() {
            Ok(files) => files,
            Err(_) => return Ok(None),
        };
        let encrypted = std::fs::read(&files.map_fastfile).map_err(|error| {
            format!(
                "failed to read retail T6 FastFile for exact light grid {}: {error}",
                files.map_fastfile.display()
            )
        })?;
        let (expanded, _audit, summary) = bo2_importer::bo2::fastfile::decode_bytes(&encrypted)
            .map_err(|error| format!("retail T6 light-grid FastFile decode failed: {error}"))?;
        if summary.zone_name != map_id || summary.expanded_sha256 != EXPANDED_SHA256 {
            return Err(format!(
                "retail T6 direct-light-grid source identity drift: zone={:?} sha={}",
                summary.zone_name, summary.expanded_sha256
            ));
        }
        let source =
            bo2_importer::bo2::retail_world_lightgrid::decode_nuketown_world_lightgrid(&expanded)?;
        let rows = source
            .rows
            .iter()
            .map(|row| T6WorldLightGridRow {
                row_index: row.row_index,
                raw_byte_offset: row.raw_byte_offset,
                col_start: row.col_start,
                col_count: row.col_count,
                z_start: row.z_start,
                z_count: row.z_count,
                first_entry: row.first_entry,
                runs: row
                    .runs
                    .iter()
                    .map(|run| T6WorldLightGridRun {
                        column_start: run.column_start,
                        column_count: run.column_count,
                        z_start: run.z_start,
                        z_count: run.z_count,
                        first_entry: run.first_entry,
                    })
                    .collect(),
            })
            .collect::<Vec<_>>();
        let entries = source
            .entries
            .iter()
            .map(|entry| T6WorldLightGridEntry {
                coeff_index: entry.coeff_index,
                primary_light_index: entry.primary_light_index,
                needs_trace: entry.needs_trace,
            })
            .collect::<Vec<_>>();
        let runtime = Self {
            sun_primary_light_index: source.sun_primary_light_index,
            mins: source.mins,
            maxs: source.maxs,
            offset: source.offset,
            row_axis: source.row_axis,
            col_axis: source.col_axis,
            row_data_start: source.row_data_start,
            raw_row_data: source.raw_row_data,
            rows,
            entries,
            coeff_bytes: source.coeff_bytes,
            coeff_count: source.coeff_count,
        };
        runtime.validate()?;

        // Exercise the exact PC coefficient decode on the full bank at source
        // acquisition time. This catches endian/layout/numeric drift before the
        // renderer can build any model-lighting representation from the data.
        let mut min_value = f32::INFINITY;
        let mut max_value = f32::NEG_INFINITY;
        for index in 0..runtime.coeff_count {
            let coeffs = runtime.decode_coeff_record(index).ok_or_else(|| {
                format!("T6 light-grid coefficient record {index} vanished during validation")
            })?;
            for value in coeffs.into_iter().flatten() {
                if !value.is_finite() {
                    return Err(format!(
                        "T6 light-grid coefficient record {index} decoded non-finite value"
                    ));
                }
                min_value = min_value.min(value);
                max_value = max_value.max(value);
            }
        }
        println!(
            "T6 canonical retail light grid retained: bounds {:?}..{:?} / {} structurally closed rows / {} raw-row bytes / {} entries / {} coefficient records; exact PC coefficient decode range {:.6}..{:.6}",
            runtime.mins,
            runtime.maxs,
            runtime.rows.len(),
            runtime.raw_row_data.len(),
            runtime.entries.len(),
            runtime.coeff_count,
            min_value,
            max_value,
        );
        Ok(Some(runtime))
    }

    #[cfg(not(feature = "import-bo2"))]
    pub(crate) fn load_direct_if_present(_map_id: &str) -> Result<Option<Self>, String> {
        Ok(None)
    }

    pub(crate) fn validate(&self) -> Result<(), String> {
        if self.row_axis >= 3 || self.col_axis >= 3 || self.row_axis == self.col_axis {
            return Err(format!(
                "T6 light grid has invalid row/column axes {}/{}",
                self.row_axis, self.col_axis
            ));
        }
        if !self.offset.is_finite() || self.coeff_count == 0 {
            return Err("T6 light grid has invalid offset/coefficient count".to_owned());
        }
        if self.coeff_bytes.len()
            != self
                .coeff_count
                .checked_mul(COEFF_RECORD_BYTES)
                .ok_or_else(|| "T6 light-grid coefficient byte count overflow".to_owned())?
        {
            return Err(format!(
                "T6 light-grid coefficient payload has {} bytes for {} records",
                self.coeff_bytes.len(), self.coeff_count
            ));
        }
        let row_axis = self.row_axis as usize;
        let expected_rows = usize::from(self.maxs[row_axis])
            .checked_sub(usize::from(self.mins[row_axis]))
            .and_then(|value| value.checked_add(1))
            .ok_or_else(|| "T6 light-grid row count underflow/overflow".to_owned())?;
        if self.row_data_start.len() != expected_rows || self.rows.len() != expected_rows {
            return Err(format!(
                "T6 light-grid row populations disagree: offsets={} decoded={} bounds-derived={expected_rows}",
                self.row_data_start.len(), self.rows.len()
            ));
        }
        if self.entries.iter().any(|entry| usize::from(entry.coeff_index) >= self.coeff_count) {
            return Err("T6 light-grid entry references coefficient outside retained bank".to_owned());
        }
        for (row_index, row) in self.rows.iter().enumerate() {
            if row.row_index != row_index
                || self.row_data_start[row_index] == u16::MAX
                || row.raw_byte_offset != usize::from(self.row_data_start[row_index]) * 4
                || row.col_count == 0
                || row.z_count == 0
                || row.first_entry >= self.entries.len()
            {
                return Err(format!(
                    "T6 light-grid decoded row {row_index} no longer matches retained serialized ownership"
                ));
            }
            let mut next_column = 0usize;
            let mut next_entry = row.first_entry;
            for run in &row.runs {
                if usize::from(run.column_start) != next_column
                    || run.column_count == 0
                    || next_column + usize::from(run.column_count) > usize::from(row.col_count)
                    || usize::from(run.z_start) + usize::from(run.z_count) > usize::from(row.z_count)
                    || run.first_entry != next_entry
                {
                    return Err(format!(
                        "T6 light-grid decoded row {row_index} contains a non-canonical RLE run"
                    ));
                }
                if run.z_count != 0 {
                    next_entry = next_entry
                        .checked_add(usize::from(run.column_count) * usize::from(run.z_count))
                        .ok_or_else(|| format!("T6 light-grid row {row_index} entry span overflow"))?;
                    if next_entry > self.entries.len() {
                        return Err(format!(
                            "T6 light-grid row {row_index} RLE entry span exceeds retained entries"
                        ));
                    }
                }
                next_column += usize::from(run.column_count);
            }
            if next_column != usize::from(row.col_count) {
                return Err(format!(
                    "T6 light-grid row {row_index} RLE covers {next_column} columns, expected {}",
                    row.col_count
                ));
            }
            let expected_next_entry = self
                .rows
                .get(row_index + 1)
                .map(|next| next.first_entry)
                .unwrap_or(self.entries.len());
            if next_entry != expected_next_entry {
                return Err(format!(
                    "T6 light-grid row {row_index} entry ownership ends at {next_entry}, expected {expected_next_entry}"
                ));
            }
        }
        Ok(())
    }

    /// Resolve an exact integer native-grid point to the retained entry index.
    /// This does not perform any world-space conversion or choose a sample point.
    pub(crate) fn entry_index_at_grid_coord(&self, coord: [u16; 3]) -> Option<usize> {
        let row_axis = usize::try_from(self.row_axis).ok()?;
        let col_axis = usize::try_from(self.col_axis).ok()?;
        let row_coord = coord[row_axis];
        if row_coord < self.mins[row_axis] || row_coord > self.maxs[row_axis] {
            return None;
        }
        let row = self.rows.get(usize::from(row_coord - self.mins[row_axis]))?;
        let col_coord = coord[col_axis];
        if col_coord < row.col_start {
            return None;
        }
        let local_col = usize::from(col_coord - row.col_start);
        if local_col >= usize::from(row.col_count) {
            return None;
        }
        let z_coord = coord[2];
        if z_coord < row.z_start {
            return None;
        }
        let local_z = usize::from(z_coord - row.z_start);
        if local_z >= usize::from(row.z_count) {
            return None;
        }
        // Native source RLE runs are sorted and gap-free after validation.
        // For wide rows beyond the 32nd interval, an out-of-line binary seek
        // avoids the long first-match scan. Early coordinates and short rows
        // retain the source's original branch-predictable linear search.
        let run = if row.runs.len() >= 64
            && local_col >= usize::from(row.runs[32].column_start)
        {
            t6_late_lightgrid_run(&row.runs, local_col)?
        } else {
            row.runs.iter().find(|run| {
                let first = usize::from(run.column_start);
                local_col >= first && local_col < first + usize::from(run.column_count)
            })?
        };
        if run.z_count == 0 || local_z < usize::from(run.z_start) {
            return None;
        }
        let run_z = local_z - usize::from(run.z_start);
        if run_z >= usize::from(run.z_count) {
            return None;
        }
        let run_col = local_col - usize::from(run.column_start);
        run.first_entry
            .checked_add(run_col.checked_mul(usize::from(run.z_count))?)?
            .checked_add(run_z)
            .filter(|index| *index < self.entries.len())
    }

    #[inline]
    pub(crate) fn entry_at_grid_coord(&self, coord: [u16; 3]) -> Option<&T6WorldLightGridEntry> {
        self.entry_index_at_grid_coord(coord)
            .and_then(|index| self.entries.get(index))
    }

    #[inline]
    pub(crate) fn coeff_record(&self, index: usize) -> Option<&[u8]> {
        if index >= self.coeff_count {
            return None;
        }
        let start = index.checked_mul(COEFF_RECORD_BYTES)?;
        self.coeff_bytes
            .get(start..start + COEFF_RECORD_BYTES)
    }

    /// Exact scalar equivalent of retail PC `R_DecodeLightGridCoeffsWeighted`
    /// for one record at weight 1.0. The game performs uint16 -> /65535 -> *32
    /// -> -16 using float32 arithmetic for every coefficient lane.
    pub(crate) fn decode_coeff_record(&self, index: usize) -> Option<T6DecodedLightGridCoeffs> {
        let raw = self.coeff_record(index)?;
        let mut out = [[0.0f32; 3]; 9];
        for (coefficient, row) in out.iter_mut().enumerate() {
            for (channel, value) in row.iter_mut().enumerate() {
                let byte = (coefficient * 3 + channel) * 2;
                let encoded = u16::from_le_bytes([raw[byte], raw[byte + 1]]);
                let mut decoded = encoded as f32;
                decoded *= INV_65535;
                decoded *= SCALE_32;
                decoded += BIAS_NEG16;
                *value = decoded;
            }
        }
        Some(out)
    }

    /// Exact operation order of retail PC `R_CalculateLightGridColorFromCoeffs`
    /// for the RGB lanes, including the final max(value, 0) clamp.
    pub(crate) fn evaluate_directional_color(
        coeffs: &T6DecodedLightGridCoeffs,
        direction: [f32; 3],
    ) -> [f32; 3] {
        let [x, y, z] = direction;
        let zx = z * x;
        let zy = z * y;
        let yx = y * x;
        let z_basis = z * z * THREE - 1.0;
        let xy_basis = x * x - y * y;
        let mut out = [0.0; 3];
        for lane in 0..3 {
            let mut value = x * coeffs[1][lane];
            value += coeffs[0][lane];
            value += y * coeffs[2][lane];
            value += z * coeffs[3][lane];
            value += zx * coeffs[4][lane];
            value += zy * coeffs[5][lane];
            value += yx * coeffs[6][lane];
            value += z_basis * coeffs[7][lane];
            value += xy_basis * coeffs[8][lane];
            out[lane] = value.max(0.0);
        }
        out
    }

    /// Exact scalar packing performed by the retained T6 PC renderer when it
    /// reduces a decoded coefficient record to `GfxLightingSH`.
    pub(crate) fn pack_gfx_lighting_sh(
        coeffs: &T6DecodedLightGridCoeffs,
    ) -> Result<T6LightingSh, String> {
        let mut luminance = [0.0f32; 9];
        for index in 0..9 {
            let mut value = coeffs[index][0] * QUARTER;
            value += coeffs[index][1] * HALF;
            value += coeffs[index][2] * QUARTER;
            luminance[index] = value;
        }
        let denom = luminance[0] + EPSILON;
        if denom == 0.0 || !denom.is_finite() {
            return Err("T6 GfxLightingSH normalization denominator is invalid".to_owned());
        }
        Ok([
            [
                coeffs[0][0] / denom,
                coeffs[0][1] / denom,
                coeffs[0][2] / denom,
                luminance[7] * THREE,
            ],
            [luminance[1], luminance[2], luminance[3], denom - luminance[7]],
            [luminance[4], luminance[5], luminance[6], luminance[8]],
        ])
    }

    /// Exact 56 normalized shell directions generated by retail T6
    /// `GenerateLightGridBasisDirs`: a 4x4x4 lattice with the 2x2x2 interior
    /// omitted. The returned order is z-major, then y, then x, matching the PC
    /// routine and the model-lighting 4x4x4 shell writer.
    pub(crate) fn basis_directions() -> Vec<[f32; 3]> {
        let mut directions = Vec::with_capacity(56);
        for z_index in 0..4 {
            let z = z_index as f32 * TWO_THIRDS - 1.0;
            for y_index in 0..4 {
                let y = y_index as f32 * TWO_THIRDS - 1.0;
                for x_index in 0..4 {
                    if x_index > 0
                        && x_index < 3
                        && y_index > 0
                        && y_index < 3
                        && z_index > 0
                        && z_index < 3
                    {
                        continue;
                    }
                    let x = x_index as f32 * TWO_THIRDS - 1.0;
                    let length = (x * x + y * y + z * z).sqrt();
                    let inverse = 1.0 / length;
                    directions.push([x * inverse, y * inverse, z * inverse]);
                }
            }
        }
        debug_assert_eq!(directions.len(), 56);
        directions
    }
}

#[cfg(test)]
mod tests {
    use super::*;


    #[test]
    fn wide_canonical_rle_row_seek_matches_original_linear_owner_search() {
        // 64 column intervals with intermittent omitted Z spans; compare
        // every grid coordinate to the old first-matching-run scan.
        let mut runs = Vec::new();
        let mut entries = Vec::new();
        for index in 0..64usize {
            let z_count = if index % 5 == 0 { 0 } else { 2 };
            let first_entry = entries.len();
            for _ in 0..2 * z_count {
                entries.push(T6WorldLightGridEntry {
                    coeff_index: 0, primary_light_index: 0, needs_trace: 0,
                });
            }
            runs.push(T6WorldLightGridRun {
                column_start: (index * 2) as u16,
                column_count: 2,
                z_start: 0,
                z_count: z_count as u8,
                first_entry,
            });
        }
        let runtime = T6WorldLightGridRuntime {
            sun_primary_light_index: 0,
            mins: [0, 0, 0],
            maxs: [0, 127, 1],
            offset: 0.0,
            row_axis: 0, col_axis: 1,
            row_data_start: vec![0],
            raw_row_data: vec![0; 16],
            rows: vec![T6WorldLightGridRow {
                row_index: 0, raw_byte_offset: 0,
                col_start: 0, col_count: 128,
                z_start: 0, z_count: 2,
                first_entry: 0, runs: runs.clone(),
            }],
            entries,
            coeff_bytes: vec![0; COEFF_RECORD_BYTES],
            coeff_count: 1,
        };
        runtime.validate().unwrap();
        for column in 0..=128u16 {
            for z in 0..=2u16 {
                let expected = runs.iter().find(|run| {
                    let first = usize::from(run.column_start);
                    let col = usize::from(column);
                    col >= first && col < first + usize::from(run.column_count)
                }).and_then(|run| {
                    let local_col = usize::from(column - run.column_start);
                    let local_z = usize::from(z);
                    (run.z_count > 0 && local_z < usize::from(run.z_count))
                        .then_some(run.first_entry + local_col * usize::from(run.z_count) + local_z)
                });
                assert_eq!(
                    runtime.entry_index_at_grid_coord([0, column, z]),
                    expected,
                    "column {column} z {z}"
                );
            }
        }
    }

    #[test]
    fn retained_pc_decode_constants_match_oracle_bits() {
        assert_eq!(INV_65535.to_bits(), 0x3780_0080);
        assert_eq!(EPSILON.to_bits(), 0x38d1_b717);
        assert_eq!(TWO_THIRDS.to_bits(), 0x3f2a_aaab);
    }

    #[test]
    fn basis_direction_population_is_exact_cube_shell() {
        let directions = T6WorldLightGridRuntime::basis_directions();
        assert_eq!(directions.len(), 56);
        for direction in directions {
            let length = (direction[0] * direction[0]
                + direction[1] * direction[1]
                + direction[2] * direction[2])
                .sqrt();
            assert!((length - 1.0).abs() < 1.0e-5);
        }
    }

    #[test]
    fn zero_encoded_coefficients_follow_retail_signed_domain() {
        let raw = vec![0u8; COEFF_RECORD_BYTES];
        let runtime = T6WorldLightGridRuntime {
            sun_primary_light_index: 1,
            mins: [0, 0, 0],
            maxs: [0, 0, 0],
            offset: 0.0,
            row_axis: 0,
            col_axis: 1,
            row_data_start: vec![0],
            raw_row_data: vec![0; 12],
            rows: vec![T6WorldLightGridRow {
                row_index: 0,
                raw_byte_offset: 0,
                col_start: 0,
                col_count: 1,
                z_start: 0,
                z_count: 1,
                first_entry: 0,
                runs: vec![T6WorldLightGridRun {
                    column_start: 0,
                    column_count: 1,
                    z_start: 0,
                    z_count: 1,
                    first_entry: 0,
                }],
            }],
            entries: vec![T6WorldLightGridEntry {
                coeff_index: 0,
                primary_light_index: 0,
                needs_trace: 0,
            }],
            coeff_bytes: raw,
            coeff_count: 1,
        };
        let decoded = runtime.decode_coeff_record(0).unwrap();
        assert_eq!(decoded[0][0].to_bits(), (-16.0f32).to_bits());
    }

    #[test]
    fn retained_row_lookup_maps_exact_integer_grid_points() {
        let runtime = T6WorldLightGridRuntime {
            sun_primary_light_index: 1,
            mins: [10, 20, 30],
            maxs: [11, 20, 31],
            offset: 0.0,
            row_axis: 1,
            col_axis: 0,
            row_data_start: vec![0],
            raw_row_data: vec![0; 16],
            rows: vec![T6WorldLightGridRow {
                row_index: 0,
                raw_byte_offset: 0,
                col_start: 10,
                col_count: 2,
                z_start: 30,
                z_count: 2,
                first_entry: 0,
                runs: vec![T6WorldLightGridRun {
                    column_start: 0,
                    column_count: 2,
                    z_start: 0,
                    z_count: 2,
                    first_entry: 0,
                }],
            }],
            entries: (0..4)
                .map(|index| T6WorldLightGridEntry {
                    coeff_index: index,
                    primary_light_index: 0,
                    needs_trace: 0,
                })
                .collect(),
            coeff_bytes: vec![0; COEFF_RECORD_BYTES * 4],
            coeff_count: 4,
        };
        runtime.validate().unwrap();
        assert_eq!(runtime.entry_index_at_grid_coord([10, 20, 30]), Some(0));
        assert_eq!(runtime.entry_index_at_grid_coord([10, 20, 31]), Some(1));
        assert_eq!(runtime.entry_index_at_grid_coord([11, 20, 30]), Some(2));
        assert_eq!(runtime.entry_index_at_grid_coord([11, 20, 31]), Some(3));
        assert_eq!(runtime.entry_index_at_grid_coord([12, 20, 30]), None);
    }
}

pub struct BenchmarkGrid(T6WorldLightGridRuntime);
impl BenchmarkGrid {
 pub fn new(run_count:usize,cols_per_run:usize)->Self {
   let columns=run_count*cols_per_run;
   assert!(columns>0&&columns<=65535&&cols_per_run<=255);
   let mut runs=Vec::with_capacity(run_count);
   for i in 0..run_count {
    runs.push(T6WorldLightGridRun{
     column_start:(i*cols_per_run)as u16,
     column_count:cols_per_run as u8,
     z_start:0,z_count:1,first_entry:i*cols_per_run
    });
   }
   let runtime=T6WorldLightGridRuntime{
    sun_primary_light_index:1,
    mins:[0,0,0],maxs:[0,columns as u16-1,0],
    offset:0.0,row_axis:0,col_axis:1,
    row_data_start:vec![0],
    raw_row_data:vec![0;16],
    rows:vec![T6WorldLightGridRow{
      row_index:0,raw_byte_offset:0,
      col_start:0,col_count:columns as u16,
      z_start:0,z_count:1,first_entry:0,runs,
    }],
    entries:(0..columns).map(|_|T6WorldLightGridEntry{
      coeff_index:0,primary_light_index:0,needs_trace:0
    }).collect(),
    coeff_bytes:vec![0;54],coeff_count:1,
   };
   runtime.validate().expect("synthetic light-grid must be source canonical");
   Self(runtime)
 }
 #[inline(never)]
 pub fn locate(&self,col:u16)->Option<usize> {
   self.0.entry_index_at_grid_coord([0,col,0])
 }
}
