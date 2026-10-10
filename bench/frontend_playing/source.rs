use std::sync::{Mutex,OnceLock};
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum MenuScreen{Playing,Main}
#[derive(Clone,Debug)]
pub struct GameSettings{pub scratch:[u8;192],pub labels: Vec<String>}
#[derive(Clone,Debug)]
pub struct ServerPreview{pub title:String}
#[derive(Clone,Debug)]
pub struct FrontendSnapshot{
 pub screen:MenuScreen,pub selected:usize,pub settings:GameSettings,pub session_active:bool,
 pub chat_open:bool,pub chat_input:String,pub status:String,
 pub input_devices:Vec<String>,pub output_devices:Vec<String>,
 pub username:String,pub level:u32,pub xp:u64,pub username_editing:bool,pub username_edit:String,
 pub join_endpoint:String,pub join_editing:bool,pub server_preview:Option<ServerPreview>,
}
pub struct FrontendState{
 screen:MenuScreen,selected:usize,session_active:bool,chat_open:bool,
 join_editing:bool,username_editing:bool,chat_input:String,status:String,
 input_devices:Vec<String>,output_devices:Vec<String>,username_edit:String,
 join_endpoint:String,server_preview:Option<ServerPreview>,
}
fn store()->&'static Mutex<FrontendState>{
 static STORE:OnceLock<Mutex<FrontendState>>=OnceLock::new();
 STORE.get_or_init(|| Mutex::new(FrontendState{
  screen:MenuScreen::Playing,selected:1,session_active:true,chat_open:false,
  join_editing:false,username_editing:false,chat_input:String::new(),status:"PLAYING".into(),
  input_devices:(0..40).map(|i|format!("Audio device microphone {i:02}")).collect(),
  output_devices:(0..40).map(|i|format!("Audio device speaker {i:02}")).collect(),
  username_edit:"example player".to_owned(),join_endpoint:"192.168.0.10:27015".into(),
  server_preview:Some(ServerPreview{title:"Synthetic preview".into()}),
 }))
}
mod profile {
 pub struct Player {pub username:String,pub level:u32,pub xp:u64}
 pub fn snapshot()->Player{Player{username:"synthetic_player".into(),level:40,xp:90210}}
}
mod settings_store {
 use super::GameSettings;
 pub fn snapshot()->GameSettings {
  GameSettings{scratch:[0x5Au8;192],labels:vec!["High".into(),"Ultra".into(),"Low latency".into()]}
 }
}

pub fn playing_header() -> Option<(String, u32, u64, bool)> {
    let active = {
        let guard = store().lock().unwrap_or_else(|poisoned| poisoned.into_inner());
        (guard.screen == MenuScreen::Playing).then_some(guard.session_active)
    }?;
    let player = profile::snapshot();
    Some((player.username, player.level, player.xp, active))
}

pub fn snapshot() -> FrontendSnapshot {
    let guard = store()
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    let current_profile = profile::snapshot();
    FrontendSnapshot {
        screen: guard.screen,
        selected: guard.selected,
        settings: settings_store::snapshot(),
        session_active: guard.session_active,
        chat_open: guard.chat_open || guard.join_editing || guard.username_editing,
        chat_input: guard.chat_input.clone(),
        status: guard.status.clone(),
        input_devices: guard.input_devices.clone(),
        output_devices: guard.output_devices.clone(),
        username: current_profile.username,
        level: current_profile.level,
        xp: current_profile.xp,
        username_editing: guard.username_editing,
        username_edit: guard.username_edit.clone(),
        join_endpoint: guard.join_endpoint.clone(),
        join_editing: guard.join_editing,
        server_preview: guard.server_preview.clone(),
    }
}