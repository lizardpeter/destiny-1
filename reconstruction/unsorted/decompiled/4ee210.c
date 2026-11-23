
void FUN_004ee210(long param_1,uint param_2)

{
  uint uVar1;
  long lVar2;
  long *plVar3;
  char cVar4;
  ulong uVar5;
  long lVar6;
  long lVar7;
  undefined1 local_58 [24];
  uint local_40;
  long local_38;
  long local_28;
  
  plVar3 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  if (*(int *)(param_1 + 0x318) != -1) {
    cVar4 = FUN_0063ff50();
    if ((cVar4 == '\0') && (*(int *)(param_1 + 0x318) != -1)) {
      lVar7 = (ulong)((param_2 & 0x1fff) * DAT_02692230) + DAT_02692228;
      if (lVar7 != 0) {
        cVar4 = FUN_00337fe0(lVar7,*(undefined4 *)PTR_DAT_019b1b40,local_58,0);
        if (cVar4 != '\0') {
          lVar6 = (ulong)(((uint)((int)local_40 >> 0xd) >> 0x12 | 0x3ff) & (int)local_40 >> 0xd) *
                  0x40;
          lVar7 = *DAT_01a238a0;
          lVar2 = *(long *)(lVar7 + 0x10 + lVar6);
          uVar5 = (ulong)((local_40 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar6));
          uVar1 = *(uint *)(local_38 + 0x24 +
                           ((lVar2 + uVar5) -
                           ((long)*(int *)(lVar7 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar5))));
          if (uVar1 != 0xffffffff) {
            lVar6 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
            lVar2 = *(long *)(lVar7 + 0x10 + lVar6);
            uVar5 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar6));
            FUN_00644640((lVar2 + uVar5) -
                         ((long)*(int *)(lVar7 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar5)),
                         param_1 + 0x26c);
          }
        }
      }
    }
  }
  if (*plVar3 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

