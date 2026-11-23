
void FUN_0073d910(uint param_1,undefined8 param_2)

{
  long lVar1;
  char cVar2;
  uint uVar3;
  long lVar4;
  ulong uVar5;
  undefined8 uVar6;
  long lVar7;
  undefined1 local_10f8 [24];
  uint local_10e0;
  long local_10d8;
  undefined1 local_10c8 [4248];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  if (param_1 != 0xffffffff) {
    if (*(int *)(*(long *)(DAT_0273ea80 + 8) + 0x644 + ((ulong)param_1 & 0xffff) * 0x2af0) == -1) {
      FUN_0066ae90(param_1,param_2);
    }
    else {
      uVar3 = FUN_006ed8f0();
      if (uVar3 != 0xffffffff) {
        lVar4 = (ulong)((uVar3 & 0x1fff) * DAT_02692230) + DAT_02692228;
        if (lVar4 != 0) {
          cVar2 = FUN_00337fe0(lVar4,*(undefined4 *)PTR_DAT_019b3388,local_10f8,0);
          if (cVar2 != '\0') {
            lVar7 = (ulong)(((uint)((int)local_10e0 >> 0xd) >> 0x12 | 0x3ff) &
                           (int)local_10e0 >> 0xd) * 0x40;
            lVar4 = *DAT_01a238a0;
            lVar1 = *(long *)(lVar4 + 0x10 + lVar7);
            uVar5 = (ulong)((local_10e0 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar7));
            uVar3 = *(uint *)(local_10d8 + 0x24 +
                             ((lVar1 + uVar5) -
                             ((long)*(int *)(lVar4 + 0x34 + lVar7) & *(ulong *)(lVar1 + 8 + uVar5)))
                             );
            if (uVar3 != 0xffffffff) {
              uVar6 = FUN_0066ae60(param_1);
              FUN_0104c3c0(local_10c8,uVar6);
              FUN_0066ae90(param_1,param_2);
              lVar7 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) *
                      0x40;
              lVar4 = *DAT_01a238a0;
              lVar1 = *(long *)(lVar4 + 0x10 + lVar7);
              uVar5 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar7));
              FUN_0073fd50((lVar1 + uVar5) -
                           ((long)*(int *)(lVar4 + 0x34 + lVar7) & *(ulong *)(lVar1 + 8 + uVar5)),
                           local_10c8,param_2);
            }
          }
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

