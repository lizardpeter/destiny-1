
undefined8 FUN_01019890(long *param_1,undefined8 param_2,undefined4 param_3)

{
  undefined *puVar1;
  long *plVar2;
  char cVar3;
  undefined8 uVar4;
  long lVar5;
  uint uVar6;
  ushort uVar7;
  int iVar8;
  long *plVar9;
  long lVar10;
  bool bVar11;
  int local_e0;
  long local_dc [20];
  long local_38;
  
  puVar1 = PTR_DAT_0191a3c0;
  local_38 = *DAT_01a1f100;
  local_e0 = 0;
  lVar10 = *(long *)(PTR_DAT_0191a3c0 + 8);
  uVar4 = FUN_000e8680(lVar10,0,0xffffffff);
  thunk_FUN_012aa986(&local_e0,0,uVar4);
  uVar7 = *(ushort *)(lVar10 + 0x1c) & 0x78;
  bVar11 = uVar7 != 0;
  if (uVar7 == 0) {
    uVar6 = *(uint *)(lVar10 + 0x20);
    if ((*(ushort *)(lVar10 + 0x1c) & 0x40) != 0) {
      lVar5 = FUN_000e8a90(lVar10,&local_e0);
      if (lVar5 == 0) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = *(uint *)(lVar5 + 0x20) & 0x5488bf | uVar6;
      }
    }
    bVar11 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar11) {
    FUN_000e6730(lVar10,&local_e0,0,0xffffffff,0);
  }
  (**(code **)(*param_1 + 0x38))(param_1);
  cVar3 = FUN_002a4ac0(*(undefined4 *)puVar1,param_2,param_3,&local_e0);
  uVar4 = 0;
  if ((cVar3 != '\0') && (uVar4 = 1, 0 < local_e0)) {
    lVar10 = 0;
    do {
      iVar8 = 0;
      plVar2 = param_1 + 0xc97;
      do {
        plVar9 = plVar2;
        if (*(int *)((long)param_1 + 0x64b4) <= iVar8) goto LAB_010199ea;
        iVar8 = iVar8 + 1;
        plVar2 = (long *)((long)plVar9 + 10);
      } while (*plVar9 != local_dc[lVar10]);
      if (iVar8 != 0) {
        *(undefined1 *)(plVar9 + 1) = 1;
      }
LAB_010199ea:
      lVar10 = lVar10 + 1;
    } while ((int)lVar10 < local_e0);
  }
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return uVar4;
}

