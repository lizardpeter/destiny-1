
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0071de10(long param_1,undefined8 *param_2,undefined8 param_3,undefined8 param_4,
                 long param_5)

{
  float fVar1;
  undefined1 auVar2 [16];
  char cVar3;
  ulong uVar4;
  undefined8 local_b8;
  undefined8 uStack_b0;
  undefined8 local_a8;
  undefined8 uStack_a0;
  undefined8 local_98;
  undefined8 uStack_90;
  undefined8 local_88;
  undefined8 uStack_80;
  undefined1 local_78 [16];
  undefined8 local_68;
  undefined8 uStack_60;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar3 = *(char *)(param_2 + 0x1e);
  if ((((cVar3 == '\0') || (cVar3 == '\x04')) ||
      ((cVar3 == '\x01' && (*(int *)(param_2 + 0x25) < *(int *)((long)param_2 + 0x134))))) &&
     ((*(ushort *)(param_2 + 0x2f) & 0x206) == 0)) {
    FUN_0071eae0(param_1,param_2,param_4,param_5);
    auVar2 = vandps_avx(*(undefined1 (*) [16])(param_2 + 2),_DAT_016489d0);
    local_48 = vorps_avx(auVar2,_DAT_016489e0);
    local_58 = param_2[0x42];
    uStack_50 = param_2[0x43];
    local_68 = param_2[0x40];
    uStack_60 = param_2[0x41];
    if (*(char *)(param_1 + 0x1ad) == '\0') {
      cVar3 = FUN_0071f180(param_2,param_1,local_48,&local_58,param_3);
      if (cVar3 != '\0') {
        *(undefined1 *)(param_1 + 0x1ad) = 1;
      }
    }
    if ((*(uint *)(param_2 + 0x2f) & 0x1000002) == 0) {
      if (*(char *)(param_5 + 0x1d) != '\0') {
        FUN_0071fac0(param_2,param_2 + 4,&local_68);
      }
      FUN_0071fe20(param_1,param_2,&local_68,local_78);
      FUN_00720480(param_1,param_2,&local_58,&local_68,local_78);
    }
    else {
      FUN_0030d510(&local_98,param_1);
      param_2[2] = local_88;
      param_2[3] = uStack_80;
      *param_2 = local_98;
      param_2[1] = uStack_90;
    }
    fVar1 = *(float *)(param_1 + 0x158);
    if ((((fVar1 != 0.0) || (NAN(fVar1))) && (fVar1 < *(float *)(param_2 + 0x34) + DAT_016490d4)) &&
       (*(byte *)((long)param_2 + 0x179) = *(byte *)((long)param_2 + 0x179) | 0x80,
       *(char *)(param_2 + 0x1e) < '\x01')) {
      *(undefined1 *)(param_2 + 0x1e) = 1;
      *(undefined2 *)((long)param_2 + 0xf1) = 2;
      param_2[0x22] = 0;
      param_2[0x23] = 0;
      param_2[0x20] = 0;
      param_2[0x21] = 0;
    }
  }
  else {
    uVar4 = (ulong)((*(uint *)(param_1 + 0x2c) & 0x1fff) * DAT_02692230);
    if ((*(byte *)(uVar4 + 6 + DAT_02692228) & 2) != 0) {
      FUN_003376e0(DAT_02692228 + uVar4);
    }
    FUN_0030d510(&local_b8,param_1);
    param_2[2] = local_a8;
    param_2[3] = uStack_a0;
    *param_2 = local_b8;
    param_2[1] = uStack_b0;
    if (*(int *)((long)param_2 + 0x124) != -1) {
      FUN_007b9680(0);
      *(undefined4 *)((long)param_2 + 0x124) = 0xffffffff;
    }
  }
  if ((*(int *)(param_5 + 8) == -1) && ((*(byte *)(param_2 + 0x2f) & 2) != 0)) {
    *(undefined4 *)(param_5 + 8) =
         *(undefined4 *)
          ((ulong)((*(uint *)(param_1 + 0x2c) & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

