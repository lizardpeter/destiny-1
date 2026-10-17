
undefined8 FUN_00269550(long param_1)

{
  undefined2 uVar1;
  uint uVar2;
  long *plVar3;
  long lVar4;
  long lVar5;
  ulong unaff_RBX;
  long lVar6;
  
  uVar2 = (uint)*(char *)(param_1 + 0x10);
  if (((*(uint *)(*(long *)(param_1 + 0x18) + (long)((int)uVar2 >> 5) * 4) >> (uVar2 & 0x1f) & 1) !=
       0) && (*(long *)(*(long *)(param_1 + 8) + (long)(int)uVar2 * 8) != 0)) {
    return 1;
  }
  plVar3 = (long *)FUN_0025a550();
  lVar4 = (**(code **)(*plVar3 + 0x388))(plVar3,*(undefined1 *)(param_1 + 0x20));
  if ((lVar4 != 0) && (0 < *(long *)(lVar4 + 8))) {
    lVar6 = 0;
    do {
      uVar1 = *(undefined2 *)(lVar4 + 0x10 + lVar6 * 2 + *(long *)(lVar4 + 0x10) + 0x10);
      unaff_RBX = CONCAT62((int6)(unaff_RBX >> 0x10),uVar1);
      plVar3 = (long *)FUN_0025a550();
      lVar5 = (**(code **)(*plVar3 + 0x410))(plVar3,unaff_RBX & 0xffffffff);
      if (((lVar5 != 0) && (*(long *)(lVar5 + 0x18) != 0)) &&
         (*(char *)(param_1 + 0x10) == *(char *)(lVar5 + 0x30 + *(long *)(lVar5 + 0x18)))) {
        *(undefined2 *)(param_1 + 0x22) = uVar1;
        return 1;
      }
      lVar6 = lVar6 + 1;
    } while (lVar6 < *(long *)(lVar4 + 8));
  }
  return 0;
}

