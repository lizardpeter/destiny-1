
void FUN_00669b20(uint param_1,undefined4 param_2,undefined4 *param_3)

{
  uint uVar1;
  long lVar2;
  char cVar3;
  ulong uVar4;
  long lVar5;
  long lVar6;
  undefined4 local_e0 [2];
  undefined1 local_d8 [24];
  uint local_c0;
  long local_b8;
  undefined4 local_a8 [2];
  undefined4 local_a0;
  undefined4 local_98;
  undefined4 local_90;
  undefined4 local_88;
  undefined4 local_80;
  undefined4 local_78;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_1 != 0xffffffff) {
    lVar6 = (ulong)((param_1 & 0x1fff) * DAT_02692230) + DAT_02692228;
    if (lVar6 != 0) {
      cVar3 = FUN_00337fe0(lVar6,*(undefined4 *)PTR_DAT_019b1b40,local_d8,0);
      if (cVar3 != '\0') {
        lVar5 = (ulong)(((uint)((int)local_c0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_c0 >> 0xd) *
                0x40;
        lVar6 = *DAT_01a238a0;
        lVar2 = *(long *)(lVar6 + 0x10 + lVar5);
        uVar4 = (ulong)((local_c0 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar5));
        uVar1 = *(uint *)(local_b8 + 0x24 +
                         ((lVar2 + uVar4) -
                         ((long)*(int *)(lVar6 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar4))));
        if (uVar1 != 0xffffffff) {
          lVar5 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
          lVar2 = *(long *)(lVar6 + 0x10 + lVar5);
          uVar4 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar5));
          lVar6 = (lVar2 + uVar4) -
                  ((long)*(int *)(lVar6 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar4));
          if (lVar6 != 0) {
            local_a8[0] = 0x811c9dc5;
            local_a0 = 0x811c9dc5;
            local_98 = 0x811c9dc5;
            local_90 = 0x811c9dc5;
            local_88 = 0x811c9dc5;
            local_80 = 0x811c9dc5;
            local_78 = 0x811c9dc5;
            local_e0[0] = param_3[3];
            FUN_00672b60(param_3 + 9,*param_3,local_e0,param_2,local_a8);
            FUN_00644640(lVar6,local_a8);
          }
        }
      }
    }
  }
  FUN_005dff10(param_1,param_3);
  FUN_005e0250(param_1,param_3);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

