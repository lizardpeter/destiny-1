
void FUN_0056fda0(int param_1,undefined1 *param_2)

{
  char cVar1;
  undefined8 uVar2;
  long lVar3;
  long lVar4;
  long *plVar5;
  int *piVar6;
  ushort uVar7;
  uint uVar8;
  int iVar9;
  bool bVar10;
  
  lVar4 = *(long *)(PTR_DAT_019e4c18 + 8);
  uVar2 = FUN_000e8680(lVar4,0,0xffffffff);
  thunk_FUN_012aa986(param_2,0,uVar2);
  uVar7 = *(ushort *)(lVar4 + 0x1c) & 0x78;
  bVar10 = uVar7 != 0;
  if (uVar7 != 0) goto LAB_0056fe2a;
  uVar8 = *(uint *)(lVar4 + 0x20);
  if ((*(ushort *)(lVar4 + 0x1c) & 0x40) != 0) {
    if (param_2 != (undefined1 *)0x0) {
      lVar3 = FUN_000e8a90(lVar4,param_2);
      if (lVar3 != 0) {
        uVar8 = uVar8 | *(uint *)(lVar3 + 0x20) & 0x5488bf;
        goto LAB_0056fe21;
      }
    }
    uVar8 = uVar8 | 0x5488bf;
  }
LAB_0056fe21:
  bVar10 = (uVar8 & 0xc08070) != 0;
LAB_0056fe2a:
  if (bVar10) {
    FUN_000e6730(lVar4,param_2,0,0xffffffff,0);
  }
  if (param_1 == 4) {
    lVar4 = FUN_005753c0(4);
    if (lVar4 != 0) {
      plVar5 = (long *)FUN_0025a550();
      piVar6 = (int *)(**(code **)(*plVar5 + 0x1d0))(plVar5);
      if (0 < *piVar6) {
        lVar3 = 0x10;
        iVar9 = 0;
        do {
          cVar1 = FUN_00276bc0(lVar4,(long)(piVar6 + 2) + lVar3 + *(long *)(piVar6 + 2));
          uVar8 = 1 << ((byte)iVar9 & 0x1f);
          if (cVar1 == '\0') {
            *(uint *)(param_2 + (long)(iVar9 >> 5) * 4 + 4) =
                 *(uint *)(param_2 + (long)(iVar9 >> 5) * 4 + 4) & ~uVar8;
          }
          else {
            *(uint *)(param_2 + (long)(iVar9 >> 5) * 4 + 4) =
                 *(uint *)(param_2 + (long)(iVar9 >> 5) * 4 + 4) | uVar8;
          }
          lVar3 = lVar3 + 0x28;
          iVar9 = iVar9 + 1;
        } while (iVar9 < *piVar6);
      }
      *param_2 = 1;
    }
  }
  return;
}

