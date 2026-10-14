
void FUN_0078c600(void)

{
  char cVar1;
  int iVar2;
  long lVar3;
  undefined8 uVar4;
  undefined4 *puVar5;
  undefined1 local_160 [320];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  lVar3 = FUN_00775770(0);
  if (lVar3 != 0) {
    cVar1 = FUN_00b8f690(lVar3 + 0x4b8);
    if (cVar1 != '\0') {
      cVar1 = FUN_00b8f690(lVar3 + 0x4b8);
      puVar5 = (undefined4 *)0x0;
      if (cVar1 != '\0') {
        puVar5 = (undefined4 *)(lVar3 + 0x59c);
      }
      cVar1 = FUN_000e4d70(5,3);
      if (cVar1 != '\0') {
        if (DAT_026cf2d8 == '\0') {
          iVar2 = thunk_FUN_012aa7d6(&DAT_026cf2d8);
          if (iVar2 != 0) {
            DAT_026cf2d0 = FUN_000e4a10(s_world_controller_face_to_face_jo_01657600);
            thunk_FUN_012aa7e6(&DAT_026cf2d8);
          }
        }
        uVar4 = FUN_00079a30(&DAT_01620037,*puVar5);
        FUN_01008290(local_160,s_world_controller_face_to_face_jo_01657600,uVar4);
        FUN_000e4aa0(DAT_026cf2d0,local_160);
      }
      DAT_026cf2b0 = *puVar5;
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

