
void FUN_00595fc0(long param_1,undefined8 *param_2,int param_3)

{
  long lVar1;
  char cVar2;
  int iVar3;
  char *pcVar4;
  undefined8 uVar5;
  undefined4 uVar6;
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  if (param_3 == 0x10) {
    lVar1 = param_1 + 0xc;
    cVar2 = FUN_002a35c0(param_2,lVar1);
    if (cVar2 == '\0') {
      uVar5 = *param_2;
      *(undefined8 *)(param_1 + 0x28) = param_2[1];
      *(undefined8 *)(param_1 + 0x20) = uVar5;
      uVar6 = swap_bytes(*(undefined4 *)(param_2 + 1));
      FUN_002e46a0(param_1 + 0x30,uVar6,
                   (*(uint *)((long)param_2 + 0xc) & 0xff) << 8 |
                   *(uint *)((long)param_2 + 0xc) >> 8 & 0xff);
      cVar2 = FUN_000e4d70(2,3);
      if (cVar2 != '\0') {
        if (DAT_026bce00 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_026bce00);
          if (iVar3 != 0) {
            DAT_026bcdf8 = FUN_000e4a10(s_networking_activity_client_messa_0163eb9d);
            thunk_FUN_012aa7e6(&DAT_026bce00);
          }
        }
        cVar2 = FUN_000b4f80(lVar1);
        if (cVar2 == '\0') {
          pcVar4 = s_proxy_0163ebfa;
        }
        else {
          pcVar4 = (char *)FUN_002a35d0(lVar1);
        }
        uVar5 = FUN_002ea610(param_1 + 0x30);
        FUN_01008290(local_170,s_networking_activity_client_messa_0163eb9d,pcVar4,uVar5);
        FUN_000e4aa0(DAT_026bcdf8,local_170);
      }
      *(undefined4 *)(param_1 + 8) = 2;
    }
  }
  else {
    *(undefined4 *)(param_1 + 8) = 3;
  }
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

