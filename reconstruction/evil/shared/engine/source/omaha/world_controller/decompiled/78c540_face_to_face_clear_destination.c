
void FUN_0078c540(void)

{
  char cVar1;
  int iVar2;
  undefined1 local_158 [320];
  long local_18;
  
  local_18 = *DAT_01a1f100;
  cVar1 = FUN_000e4d70(5,3);
  if (cVar1 != '\0') {
    if (DAT_026cf2c8 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_026cf2c8);
      if (iVar2 != 0) {
        DAT_026cf2c0 = FUN_000e4a10(s_world_controller_face_to_face_jo_016575bf);
        thunk_FUN_012aa7e6(&DAT_026cf2c8);
      }
    }
    FUN_01008290(local_158,s_world_controller_face_to_face_jo_016575bf);
    FUN_000e4aa0(DAT_026cf2c0,local_158);
  }
  DAT_026cf2b0 = 0x811c9dc5;
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

