
void FUN_007541c0(undefined8 param_1,int *param_2)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  long lVar4;
  undefined1 local_158 [320];
  long local_18;
  
  local_18 = *DAT_01a1f100;
  uVar3 = FUN_00587520();
  lVar4 = FUN_0057de80(uVar3);
  if (*(int *)(lVar4 + 0x480) == -0x7ee3623b) {
    cVar1 = FUN_000e4d70(5,4);
    if (cVar1 != '\0') {
      if (DAT_026c9480 == '\0') {
        iVar2 = thunk_FUN_012aa7d6(&DAT_026c9480);
        if (iVar2 != 0) {
          DAT_026c9478 = FUN_000e4a10(s_world_controller_orbit_map_loade_0164a251);
          thunk_FUN_012aa7e6(&DAT_026c9480);
        }
      }
      FUN_01008290(local_158,s_world_controller_orbit_map_loade_0164a251);
      FUN_000e4aa0(DAT_026c9478,local_158);
    }
  }
  else {
    *param_2 = *(int *)(lVar4 + 0x480);
  }
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

