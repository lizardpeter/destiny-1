
uint FUN_00ae8600(short param_1)

{
  long lVar1;
  ulong uVar2;
  long lVar3;
  uint uVar4;
  long lVar5;
  long lVar6;
  long *plVar7;
  
  uVar4 = 0xffffffff;
  if (param_1 != -1) {
    uVar4 = (int)*(uint *)(DAT_027be860 + 0x1c) >> 0xd;
    lVar3 = (ulong)((uVar4 >> 0x12 | 0x3ff) & uVar4) * 0x40;
    lVar6 = *DAT_01a238a0;
    lVar5 = *(long *)(lVar6 + 0x10 + lVar3);
    uVar2 = (ulong)((*(uint *)(DAT_027be860 + 0x1c) & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar3));
    lVar6 = (lVar5 + uVar2) - ((long)*(int *)(lVar6 + 0x34 + lVar3) & *(ulong *)(lVar5 + 8 + uVar2))
    ;
    uVar4 = *(uint *)(lVar6 + *(long *)(lVar6 + 0x20) + 0x40 + (long)param_1 * 0x18);
    if (0x7f < uVar4) {
      plVar7 = (long *)(lVar6 + 0x30);
      lVar5 = 0;
      lVar3 = -1;
      do {
        lVar3 = lVar3 + 1;
        if (*(long *)(lVar6 + 0x28) <= lVar3) {
          return uVar4;
        }
        lVar1 = lVar5 + (long)((int)param_1 >> 5) * 4 + 0x38 + *plVar7;
        lVar5 = lVar5 + 0xa0;
      } while ((*(uint *)((long)plVar7 + lVar1) & 1 << ((byte)param_1 & 0x1f)) == 0);
      uVar4 = *(uint *)((long)plVar7 + lVar5 + *plVar7 + -0x58);
    }
  }
  return uVar4;
}

