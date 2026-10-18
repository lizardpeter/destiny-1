
void FUN_007df250(long param_1,uint param_2,uint param_3)

{
  long lVar1;
  long lVar2;
  char cVar3;
  long lVar4;
  undefined *puVar5;
  ulong uVar6;
  
  lVar4 = (ulong)(((uint)((int)param_3 >> 0xd) >> 0x12 | 0x3ff) & (int)param_3 >> 0xd) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar4);
  uVar6 = (ulong)((param_3 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar4));
  puVar5 = (undefined *)
           FUN_00057f80((lVar2 + uVar6) -
                        ((long)*(int *)(lVar1 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar6)));
  uVar6 = (ulong)param_2;
  if (puVar5 == (undefined *)0x0) {
    puVar5 = PTR_DAT_01a1f4b8;
  }
  if (puVar5 != *(undefined **)(&DAT_00001ef8 + uVar6 * 8 + param_1)) {
    cVar3 = FUN_00f84710(puVar5);
    if (cVar3 == '\0') {
      puVar5 = PTR_DAT_01a1f4b8;
    }
    FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,1,uVar6,1,puVar5);
    *(undefined **)(&DAT_00001ef8 + uVar6 * 8 + param_1) = puVar5;
  }
  return;
}

