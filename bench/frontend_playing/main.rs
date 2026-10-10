use std::{hint::black_box,time::Instant};
mod source;
fn verify() {
 let old=source::snapshot();
 let new=source::playing_header().unwrap();
 assert_eq!(old.username,new.0);
 assert_eq!(old.level,new.1);
 assert_eq!(old.xp,new.2);
 assert_eq!(old.session_active,new.3);
 assert_eq!(old.screen,source::MenuScreen::Playing);
 println!("PASS: Playing identity, level, XP and active state parity using exact original vs optimized snapshot functions");
}
fn bench(iterations:usize) {
 // Original frontend::snapshot triggers legacy::snapshot TWICE and
 // social_notice calls legacy::snapshot once again.
 let old=||{
  let start=Instant::now();let mut checksum=0u64;
  for _ in 0..iterations {
   let first=source::snapshot();
   let second=source::snapshot();
   let third=source::snapshot();
   checksum^=black_box(first.xp + second.xp + third.xp);
   black_box(first);black_box(second);black_box(third);
  }
  black_box(checksum);start.elapsed().as_secs_f64()
 };
 let new=||{
  let start=Instant::now();let mut checksum=0u64;
  for _ in 0..iterations {
   let first=source::playing_header().expect("Playing");
   checksum^=black_box(first.2*3);
   black_box(first);
  }
  black_box(checksum);start.elapsed().as_secs_f64()
 };
 let(mut before,mut after)=(Vec::new(),Vec::new());
 for r in 0..7 {if r%2==0{before.push(old());after.push(new());}else{after.push(new());before.push(old());}}
 before.sort_by(f64::total_cmp);after.sort_by(f64::total_cmp);
 println!("frames={iterations} synthetic_menu_state_old_ms={:.3} playing_header_ms={:.3} speedup={:.2}x",before[3]*1000.,after[3]*1000.,before[3]/after[3]);
}
fn main(){verify();for n in [1_000usize,20_000]{bench(n);}}
